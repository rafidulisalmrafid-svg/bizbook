import os
import uuid
import time
from typing import Tuple
from app.config import settings
from app.core.security import create_access_token, decode_access_token

class StorageService:
    @staticmethod
    def get_storage_path(company_id: str, document_id: str, version: int, filename: str) -> str:
        safe_filename = filename.replace(" ", "_")
        return f"{company_id}/vault/{document_id}/v{version}_{safe_filename}"

    @staticmethod
    async def save_file_bytes(storage_path: str, data: bytes) -> str:
        base_dir = os.path.abspath(settings.STORAGE_LOCAL_DIR)
        full_path = os.path.join(base_dir, storage_path.replace("/", os.sep))
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "wb") as f:
            f.write(data)
        return full_path

    @staticmethod
    def generate_signed_url(document_id: str, company_id: str, expires_in_seconds: int = 900) -> str:
        token = create_access_token(
            {"doc_id": document_id, "comp_id": company_id, "exp_type": "signed_download"},
            expires_delta=None
        )
        return f"/api/v1/documents/{document_id}/download?token={token}"

    @staticmethod
    def verify_signed_token(token: str, document_id: str, company_id: str) -> bool:
        payload = decode_access_token(token)
        if not payload:
            return False
        return payload.get("doc_id") == document_id and payload.get("comp_id") == company_id
