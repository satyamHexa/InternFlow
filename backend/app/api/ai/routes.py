from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import BadRequestException, ServiceUnavailableException
from app.repositories.referral_repository import ReferralRepository
from app.services.ai_client import AIServiceUnavailableError, azure_openai_client
from app.services.ai_schemas import DuplicateResult, EmailContent, ParsedResume
from app.services.ai_service import ai_service
from app.api.auth.dependencies import CurrentUser

router = APIRouter()
_referral_repo = ReferralRepository()

_MAX_PDF_BYTES = 10 * 1024 * 1024  # 10 MB


# ── Schemas ─────────────────────────────────────────────────────────────────
# Re-exported from ai_schemas so the OpenAPI spec is self-contained.

from pydantic import BaseModel, Field


class ParseResumeTextRequest(BaseModel):
    resume_text: str = Field(min_length=50, description="Plain text extracted from resume")


class EmailGenRequest(BaseModel):
    event: str = Field(description="Notification event name, e.g. referral_submitted")
    context: dict = Field(default_factory=dict, description="Template variables")


class DuplicateCheckRequest(BaseModel):
    candidate_email: str
    candidate_name: str


class AIStatusResponse(BaseModel):
    azure_openai_configured: bool
    document_intelligence_configured: bool
    model_deployment: str


# ── Endpoints ────────────────────────────────────────────────────────────────


@router.get("/status", response_model=AIStatusResponse)
async def ai_status(current_user: CurrentUser) -> AIStatusResponse:
    """Return which AI integrations are configured (no credentials exposed)."""
    from app.core.config import settings

    return AIStatusResponse(
        azure_openai_configured=azure_openai_client.is_configured,
        document_intelligence_configured=bool(
            settings.AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT
            and settings.AZURE_DOCUMENT_INTELLIGENCE_KEY
        ),
        model_deployment=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
    )


@router.post(
    "/parse-resume/upload",
    response_model=ParsedResume,
    summary="Parse resume from PDF upload",
)
async def parse_resume_upload(
    current_user: CurrentUser,
    file: UploadFile = File(..., description="PDF resume file (max 10 MB)"),
) -> ParsedResume:
    """Upload a PDF resume and extract structured data via Azure OpenAI.

    - Uses Azure Document Intelligence for text extraction (if configured).
    - Passes extracted text to GPT-4o for structured JSON extraction.
    - Applies heuristic confidence scoring.
    """
    if file.content_type not in ("application/pdf",):
        raise BadRequestException("Only PDF files are accepted")

    pdf_bytes = await file.read()
    if len(pdf_bytes) > _MAX_PDF_BYTES:
        raise BadRequestException("File size must not exceed 10 MB")
    if len(pdf_bytes) == 0:
        raise BadRequestException("Uploaded file is empty")

    return await ai_service.parse_resume_bytes(pdf_bytes)


@router.post(
    "/parse-resume/text",
    response_model=ParsedResume,
    summary="Parse resume from plain text",
)
async def parse_resume_text(
    payload: ParseResumeTextRequest,
    current_user: CurrentUser,
) -> ParsedResume:
    """Extract structured data from pre-extracted resume text via GPT-4o."""
    return await ai_service.parse_resume_text(payload.resume_text)


@router.post(
    "/parse-resume/referral/{referral_id}",
    response_model=ParsedResume,
    summary="Parse resume for an existing referral",
)
async def parse_resume_for_referral(
    referral_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> ParsedResume:
    """Download the referral's resume from blob storage and parse it.

    Requires the referral to have a ``resume_url`` set.
    Returns cached ``parsed_resume_json`` if already parsed.
    """
    from app.core.exceptions import NotFoundException

    referral = await _referral_repo.get(referral_id, db)
    if referral is None:
        raise NotFoundException("Referral")

    # Return cached result if available
    if referral.parsed_resume_json:
        try:
            return ParsedResume(**referral.parsed_resume_json)
        except Exception:
            pass  # Re-parse if cached data is corrupt

    if not referral.resume_url:
        raise BadRequestException("Referral does not have a resume attached yet")

    # Download from blob
    import httpx

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(referral.resume_url)
            resp.raise_for_status()
            pdf_bytes = resp.content
    except Exception as exc:
        raise BadRequestException(f"Could not download resume: {exc}") from exc

    parsed = await ai_service.parse_resume_bytes(pdf_bytes)

    # Persist parsed result back to referral
    await _referral_repo.update(
        referral_id,
        {
            "parsed_resume_json": parsed.model_dump(),
            "confidence_score": parsed.confidence_score,
        },
        db,
    )
    return parsed


@router.post(
    "/generate-email",
    response_model=EmailContent,
    summary="Generate a personalised email via GPT-4o",
)
async def generate_email(
    payload: EmailGenRequest,
    current_user: CurrentUser,
) -> EmailContent:
    """Generate a professional email for the given notification event.

    Supported events: ``referral_submitted``, ``nda_pending``, ``nda_signed``,
    ``sla_breach``, ``certificate_ready``, ``task_assigned``,
    ``intern_start_reminder``.

    Degrades gracefully to a template-based fallback when Azure is not configured.
    """
    return await ai_service.generate_email(payload.event, payload.context)


@router.post(
    "/check-duplicate",
    response_model=DuplicateResult,
    summary="Check if a candidate is a duplicate",
)
async def check_duplicate(
    payload: DuplicateCheckRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=500, description="Max referrals to compare"),
) -> DuplicateResult:
    """Detect whether the given candidate already exists in the system.

    Strategy:
    1. Exact email match (in-DB, no AI) → ``confidence=1.0``.
    2. AI fuzzy name/email matching against recent referrals.

    Degrades to exact-email-only when Azure is not configured.
    """
    # Fetch recent referrals for comparison
    from sqlalchemy import select
    from app.models.referral import Referral

    result = await db.execute(
        select(
            Referral.id,
            Referral.candidate_name,
            Referral.candidate_email,
        ).limit(limit)
    )
    rows = result.mappings().all()
    existing = [dict(r) for r in rows]

    return await ai_service.check_duplicate(
        candidate_email=payload.candidate_email,
        candidate_name=payload.candidate_name,
        existing_referrals=existing,
    )
