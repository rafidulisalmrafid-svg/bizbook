from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.document import DocumentProcessingState, DocumentCategory, ApprovalStatus

class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    owner_id: Optional[str] = None
    file_name: str
    mime_type: str
    size_bytes: int
    category: DocumentCategory
    status: DocumentProcessingState
    is_final: bool
    is_archived: bool
    current_version: int
    expiry_date: Optional[datetime] = None
    is_expired: bool
    is_expiring_soon: bool
    metadata_json: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

class DocumentVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    version_number: int
    file_name: str
    size_bytes: int
    change_summary: Optional[str] = None
    is_final: bool
    created_at: datetime

class DocumentUpdate(BaseModel):
    category: Optional[DocumentCategory] = None
    expiry_date: Optional[datetime] = None
    metadata_json: Optional[Dict[str, Any]] = None
    is_final: Optional[bool] = None

class DocumentSearchRequest(BaseModel):
    query: Optional[str] = None
    category: Optional[DocumentCategory] = None
    project_id: Optional[str] = None
    client_id: Optional[str] = None
    expired_only: Optional[bool] = None
    limit: int = 50

class DocumentTemplateCreate(BaseModel):
    title: str
    category: str = "Proposal"
    content: str
    is_approved: bool = False

class DocumentTemplateUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    content: Optional[str] = None
    is_approved: Optional[bool] = None

class DocumentTemplateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    title: str
    category: str
    content: str
    version: int
    is_approved: bool
    created_at: datetime

class TemplateRenderRequest(BaseModel):
    template_id: Optional[str] = None
    variables: Dict[str, Any] = {}

class TemplateRenderResponse(BaseModel):
    template_id: str
    rendered_content: str
    variables_applied: Dict[str, Any]

class SignatureApprovalRequest(BaseModel):
    document_id: str
    signature_id: str
    seal_id: Optional[str] = None

class SignatureApprovalAction(BaseModel):
    status: ApprovalStatus # APPROVED or REJECTED

class SignatureApprovalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    document_id: str
    signature_id: str
    seal_id: Optional[str] = None
    status: ApprovalStatus
    requested_by: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    applied_at: Optional[datetime] = None
    created_at: datetime

class SignedUrlResponse(BaseModel):
    document_id: str
    file_name: str
    signed_url: str
    expires_in_seconds: int = 900
