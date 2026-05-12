"""Resume parsing pipeline.

Stage 1 — Text extraction:
    PDF bytes → Azure Document Intelligence (prebuilt-read model) → plain text
    Falls back to raw byte decoding if Document Intelligence is not configured.

Stage 2 — Structured extraction:
    Plain text → Azure OpenAI GPT-4o (JSON mode) → ParsedResume

Stage 3 — Confidence scoring:
    Field-presence heuristic applied on top of the model's self-reported score.
"""
from __future__ import annotations

import base64
import logging
import re

from pydantic import ValidationError

from app.services.ai_client import AzureOpenAIClient, azure_openai_client
from app.services.ai_schemas import (
    EducationEntry,
    ExperienceEntry,
    ParsedResume,
)
from app.services.prompts import build_resume_messages
from app.core.config import settings

logger = logging.getLogger(__name__)


# ── Confidence scoring weights ──────────────────────────────────────────────

_WEIGHTS: dict[str, float] = {
    "name": 0.20,
    "email": 0.25,
    "phone": 0.05,
    "skills_2+": 0.15,    # at least 2 skills present
    "experience": 0.15,
    "education_1+": 0.15, # at least 1 education entry
    "summary": 0.05,
}


def _compute_confidence(parsed: ParsedResume) -> float:
    """Return a heuristic confidence score in [0.0, 1.0]."""
    score = 0.0
    if parsed.name and len(parsed.name.strip()) > 1:
        score += _WEIGHTS["name"]
    if parsed.email and "@" in parsed.email:
        score += _WEIGHTS["email"]
    if parsed.phone:
        score += _WEIGHTS["phone"]
    if len(parsed.skills) >= 2:
        score += _WEIGHTS["skills_2+"]
    if parsed.experience_years is not None and parsed.experience_years >= 0:
        score += _WEIGHTS["experience"]
    if len(parsed.education) >= 1:
        score += _WEIGHTS["education_1+"]
    if parsed.summary and len(parsed.summary.strip()) > 20:
        score += _WEIGHTS["summary"]
    # Blend heuristic (60%) with model's self-reported score (40%)
    model_score = parsed.confidence_score or 0.0
    return round(0.6 * score + 0.4 * model_score, 4)


class ResumeParser:
    """Orchestrates text extraction + GPT-based structured extraction."""

    def __init__(self, client: AzureOpenAIClient | None = None) -> None:
        self._client = client or azure_openai_client

    # ── Stage 1: Text extraction ────────────────────────────────────────

    async def extract_text(self, pdf_bytes: bytes) -> str:
        """Extract plain text from PDF bytes.

        Tries Azure Document Intelligence first; degrades gracefully.
        """
        if (
            settings.AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT
            and settings.AZURE_DOCUMENT_INTELLIGENCE_KEY
        ):
            try:
                return await self._extract_via_document_intelligence(pdf_bytes)
            except Exception as exc:
                logger.warning(
                    "Document Intelligence extraction failed (%s); falling back to raw decode.",
                    exc,
                )

        return self._extract_text_fallback(pdf_bytes)

    async def _extract_via_document_intelligence(self, pdf_bytes: bytes) -> str:
        from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
        from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
        from azure.core.credentials import AzureKeyCredential

        async with DocumentIntelligenceClient(
            endpoint=settings.AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT,
            credential=AzureKeyCredential(settings.AZURE_DOCUMENT_INTELLIGENCE_KEY),
        ) as doc_client:
            poller = await doc_client.begin_analyze_document(
                "prebuilt-read",
                AnalyzeDocumentRequest(bytes_source=pdf_bytes),
            )
            result = await poller.result()
            text = result.content or ""
            logger.debug(
                "Document Intelligence extracted %d characters", len(text)
            )
            return text

    @staticmethod
    def _extract_text_fallback(pdf_bytes: bytes) -> str:
        """Best-effort text extraction without external services.

        Attempts UTF-8 / latin-1 decoding and strips non-printable chars.
        Suitable for text-based PDFs; returns empty string for image-only PDFs.
        """
        for encoding in ("utf-8", "latin-1", "cp1252"):
            try:
                raw = pdf_bytes.decode(encoding, errors="replace")
                # Remove PDF binary noise; keep printable ASCII + common whitespace
                cleaned = re.sub(r"[^\x20-\x7e\n\r\t]", " ", raw)
                # Collapse long whitespace runs
                cleaned = re.sub(r" {3,}", "  ", cleaned)
                cleaned = re.sub(r"\n{4,}", "\n\n", cleaned)
                text = cleaned.strip()
                if len(text) > 100:  # sanity check: discard garbage decodings
                    return text
            except Exception:
                continue
        return ""

    # ── Stage 2: Structured extraction ─────────────────────────────────

    async def parse_text(self, resume_text: str) -> ParsedResume:
        """Send resume text to GPT-4o and return a validated ParsedResume."""
        if not resume_text.strip():
            logger.warning("parse_text called with empty text; returning empty ParsedResume")
            return ParsedResume()

        messages = build_resume_messages(resume_text)
        raw: dict = await self._client.chat_json(messages, temperature=0.1, max_tokens=2048)

        return self._validate_raw(raw)

    @staticmethod
    def _validate_raw(raw: dict) -> ParsedResume:
        """Validate and coerce the raw GPT JSON response into ParsedResume."""
        if not raw:
            return ParsedResume()
        try:
            # Coerce nested objects
            raw["education"] = [
                EducationEntry(**e) if isinstance(e, dict) else e
                for e in raw.get("education", [])
            ]
            raw["experience_entries"] = [
                ExperienceEntry(**e) if isinstance(e, dict) else e
                for e in raw.get("experience_entries", [])
            ]
            return ParsedResume(**raw)
        except (ValidationError, TypeError) as exc:
            logger.warning("ParsedResume validation error: %s; attempting partial parse", exc)
            # Partial recovery: take only the safe scalar fields
            safe = {
                k: v for k, v in raw.items()
                if k in {"name", "email", "phone", "summary", "experience_years"}
                and not isinstance(v, (dict, list))
            }
            safe["skills"] = [
                s for s in raw.get("skills", []) if isinstance(s, str)
            ]
            safe["languages"] = [
                l for l in raw.get("languages", []) if isinstance(l, str)
            ]
            return ParsedResume(**safe)

    # ── Stage 3: Full pipeline ──────────────────────────────────────────

    async def pipeline(self, pdf_bytes: bytes) -> ParsedResume:
        """Run the full extract → parse → score pipeline.

        Returns a best-effort ``ParsedResume`` even on partial failure.
        """
        text = await self.extract_text(pdf_bytes)
        if not text:
            logger.warning("Text extraction yielded no content")
            return ParsedResume(confidence_score=0.0)

        parsed = await self.parse_text(text)
        parsed.confidence_score = _compute_confidence(parsed)
        return parsed

    async def pipeline_from_text(self, resume_text: str) -> ParsedResume:
        """Parse from pre-extracted text (skips Document Intelligence)."""
        parsed = await self.parse_text(resume_text)
        parsed.confidence_score = _compute_confidence(parsed)
        return parsed


# Module-level singleton
resume_parser = ResumeParser()
