from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status, Query
from fastapi.responses import FileResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.api.deps import require_permission, CurrentTenant
from app.models.user_company import PermissionEnum
from app.models.document import DocumentCategory, ApprovalStatus
from app.schemas.document import (
    DocumentRead,
    DocumentUpdate,
    DocumentSearchRequest,
    SignatureApprovalRequest,
    SignatureApprovalAction,
    SignatureApprovalRead,
    SignedUrlResponse,
)
from app.services.document_service import DocumentService
from app.services.storage_service import StorageService
import os
from app.config import settings

router = APIRouter()

@router.post("/upload", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    category: DocumentCategory = Form(DocumentCategory.GENERAL),
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.DOCUMENT_UPLOAD)),
    db: AsyncSession = Depends(get_db),
):
    content = await file.read()
    try:
        doc = await DocumentService.upload_document(
            db=db,
            company_id=tenant.company_id,
            user_id=tenant.user.id,
            file_name=file.filename or "uploaded_document",
            file_bytes=content,
            category=category,
        )
        return doc
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("", response_model=List[DocumentRead])
async def search_documents(
    query: Optional[str] = None,
    category: Optional[DocumentCategory] = None,
    expired_only: Optional[bool] = None,
    limit: int = Query(50, le=100),
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.DOCUMENT_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    params = DocumentSearchRequest(
        query=query,
        category=category,
        expired_only=expired_only,
        limit=limit,
    )
    return await DocumentService.search_documents(db, tenant.company_id, params)

@router.get("/{document_id}", response_model=DocumentRead)
async def get_document(
    document_id: str,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.DOCUMENT_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    return await DocumentService.get_document(db, tenant.company_id, document_id)

@router.put("/{document_id}", response_model=DocumentRead)
async def update_document(
    document_id: str,
    data: DocumentUpdate,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.DOCUMENT_UPLOAD)),
    db: AsyncSession = Depends(get_db),
):
    return await DocumentService.update_document(
        db=db,
        company_id=tenant.company_id,
        user_id=tenant.user.id,
        document_id=document_id,
        data=data,
    )

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.DOCUMENT_DELETE)),
    db: AsyncSession = Depends(get_db),
):
    await DocumentService.delete_document(db, tenant.company_id, tenant.user.id, document_id)
    return {"message": "Document archived successfully"}

@router.get("/{document_id}/signed-url", response_model=SignedUrlResponse)
async def get_signed_download_url(
    document_id: str,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.DOCUMENT_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    doc = await DocumentService.get_document(db, tenant.company_id, document_id)
    signed_url = StorageService.generate_signed_url(doc.id, tenant.company_id)
    return SignedUrlResponse(
        document_id=doc.id,
        file_name=doc.file_name,
        signed_url=signed_url,
    )

@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    # Public download endpoint protected exclusively by the signed URL token
    # Extract company_id from token
    from app.core.security import decode_access_token
    payload = decode_access_token(token)
    if not payload or payload.get("doc_id") != document_id or payload.get("exp_type") != "signed_download":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or expired download signature.")

    company_id = payload.get("comp_id")
    doc = await DocumentService.get_document(db, company_id, document_id)
    
    base_dir = os.path.abspath(settings.STORAGE_LOCAL_DIR)
    full_path = os.path.join(base_dir, doc.storage_path.replace("/", os.sep))
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File content not found in vault")

    return FileResponse(
        path=full_path,
        media_type=doc.mime_type,
        filename=doc.file_name,
    )

# Signature & Seal Approval Workflow Endpoints
@router.post("/{document_id}/signature-approval", response_model=SignatureApprovalRead, status_code=status.HTTP_201_CREATED)
async def request_signature_approval(
    document_id: str,
    data: SignatureApprovalRequest,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.SIGNATURE_USE)),
    db: AsyncSession = Depends(get_db),
):
    return await DocumentService.request_signature(
        db=db,
        company_id=tenant.company_id,
        user_id=tenant.user.id,
        document_id=document_id,
        signature_id=data.signature_id,
        seal_id=data.seal_id,
    )

@router.post("/signature-approval/{approval_id}/action", response_model=SignatureApprovalRead)
async def action_signature_approval(
    approval_id: str,
    data: SignatureApprovalAction,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.SIGNATURE_USE)),
    db: AsyncSession = Depends(get_db),
):
    return await DocumentService.approve_and_apply_signature(
        db=db,
        company_id=tenant.company_id,
        user_id=tenant.user.id,
        approval_id=approval_id,
        approve=(data.status == ApprovalStatus.APPROVED or data.status == ApprovalStatus.APPLIED),
    )
