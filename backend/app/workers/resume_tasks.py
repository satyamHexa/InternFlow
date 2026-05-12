from __future__ import annotations

import asyncio
import logging

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.workers.resume_tasks.parse_resume_async",
    bind=True,
    max_retries=3,
)
def parse_resume_async(self, referral_id: str, blob_url: str) -> None:
    """Download PDF from blob_url, run the full AI parse pipeline, and save results."""
    asyncio.run(_parse_resume(referral_id, blob_url))


async def _parse_resume(referral_id: str, blob_url: str) -> None:
    import httpx
    from app.core.database import AsyncSessionLocal
    from app.repositories.referral_repository import ReferralRepository
    from app.services.ai_service import ai_service

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.get(blob_url)
            resp.raise_for_status()
            pdf_bytes = resp.content
    except Exception as exc:
        logger.error("resume_tasks: failed to download %s: %s", blob_url, exc)
        return

    parsed = await ai_service.parse_resume_bytes(pdf_bytes)
    logger.info(
        "resume_tasks: parsed referral=%s confidence=%.2f",
        referral_id,
        parsed.confidence_score,
    )

    async with AsyncSessionLocal() as db:
        repo = ReferralRepository()
        import uuid

        await repo.update(
            uuid.UUID(referral_id),
            {
                "parsed_resume_json": parsed.model_dump(),
                "confidence_score": parsed.confidence_score,
            },
            db,
        )
        await db.commit()


@celery_app.task(name="app.workers.resume_tasks.check_duplicate_async")
def check_duplicate_async(referral_id: str) -> None:
    """Run AI duplicate detection for a newly submitted referral."""
    asyncio.run(_check_duplicate(referral_id))


async def _check_duplicate(referral_id: str) -> None:
    import uuid
    from sqlalchemy import select
    from app.core.database import AsyncSessionLocal
    from app.models.referral import Referral
    from app.repositories.referral_repository import ReferralRepository
    from app.services.ai_service import ai_service

    async with AsyncSessionLocal() as db:
        repo = ReferralRepository()
        referral = await repo.get(uuid.UUID(referral_id), db)
        if referral is None:
            logger.warning("check_duplicate_async: referral %s not found", referral_id)
            return

        # Fetch other referrals for comparison (exclude self)
        result = await db.execute(
            select(Referral.id, Referral.candidate_name, Referral.candidate_email)
            .where(Referral.id != referral.id)
            .limit(200)
        )
        existing = [dict(r) for r in result.mappings().all()]

        dup = await ai_service.check_duplicate(
            candidate_email=referral.candidate_email,
            candidate_name=referral.candidate_name,
            existing_referrals=existing,
        )

        update: dict = {"is_duplicate": dup.is_duplicate}
        if dup.matched_referral_id:
            import uuid as _uuid

            update["duplicate_of_id"] = _uuid.UUID(dup.matched_referral_id)

        await repo.update(uuid.UUID(referral_id), update, db)
        await db.commit()
        logger.info(
            "check_duplicate_async: referral=%s is_duplicate=%s confidence=%.2f",
            referral_id,
            dup.is_duplicate,
            dup.confidence,
        )
