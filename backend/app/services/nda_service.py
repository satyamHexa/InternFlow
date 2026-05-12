from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class NDAService:
    """Generate and validate NDA documents.
    Stubs produce placeholder data until PDF generation is wired up.
    """

    async def generate_nda(self, referral_id: str, candidate_name: str) -> dict:
        """Generate a pre-filled NDA PDF and store in Blob."""
        logger.debug("NDAService.generate_nda stub: %s", referral_id)
        blob_url = f"https://blob.internflow.test/ndas/{referral_id}/nda.pdf"
        return {
            "blob_url": blob_url,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def sign_nda(self, referral_id: str, signature_data: str) -> dict:
        """Record a digital signature against an NDA document."""
        logger.debug("NDAService.sign_nda stub: %s", referral_id)
        return {
            "signed_at": datetime.now(timezone.utc).isoformat(),
            "signature_ref": str(uuid.uuid4()),
        }


nda_service = NDAService()
