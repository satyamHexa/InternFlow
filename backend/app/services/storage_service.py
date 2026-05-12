from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class StorageService:
    """Facade for Azure Blob Storage.
    Stubs return placeholder URLs until Azure credentials are configured.
    """

    async def upload_resume(self, referral_id: str, file_bytes: bytes, filename: str) -> str:
        logger.debug("StorageService.upload_resume stub: %s", filename)
        return f"https://blob.internflow.test/resumes/{referral_id}/{filename}"

    async def upload_document(self, referral_id: str, doc_type: str, file_bytes: bytes) -> str:
        logger.debug("StorageService.upload_document stub: %s/%s", referral_id, doc_type)
        return f"https://blob.internflow.test/documents/{referral_id}/{doc_type}.pdf"

    async def get_blob_sas_url(self, blob_url: str, expiry_seconds: int = 3600) -> str:
        logger.debug("StorageService.get_blob_sas_url stub")
        return blob_url + "?sv=stub-sas-token"


storage_service = StorageService()
