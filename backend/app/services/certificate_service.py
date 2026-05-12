from __future__ import annotations

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class CertificateService:
    """Generate internship completion certificates.
    Stubs produce placeholder data until PDF generation is wired up.
    """

    async def generate_certificate(
        self, referral_id: str, candidate_name: str, generated_by: str
    ) -> dict:
        """Render certificate PDF, upload to Blob, return URL."""
        logger.debug("CertificateService.generate_certificate stub: %s", referral_id)
        blob_url = f"https://blob.internflow.test/certificates/{referral_id}/certificate.pdf"
        return {
            "blob_url": blob_url,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def get_download_url(self, referral_id: str) -> str:
        """Return a time-limited download URL for the certificate."""
        logger.debug("CertificateService.get_download_url stub: %s", referral_id)
        return f"https://blob.internflow.test/certificates/{referral_id}/certificate.pdf?sv=stub-sas"


certificate_service = CertificateService()
