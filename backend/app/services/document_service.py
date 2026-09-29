import os
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.document import (
    Document,
    DocumentVersion,
    DocumentTemplate,
    SignatureApprovalWorkflow,
    DocumentProcessingState,
    DocumentCategory,
    ApprovalStatus,
)
from app.models.user_company import CompanySignature, CompanySeal
from app.services.storage_service import StorageService
from app.services.document_processor import DocumentProcessor
from app.services.audit_service import AuditService
from app.schemas.document import DocumentUpdate, DocumentSearchRequest

class DocumentService:
    @staticmethod
    async def upload_document(
        db: AsyncSession,
        company_id: str,
        user_id: str,
        file_name: str,
        file_bytes: bytes,
        category: DocumentCategory = DocumentCategory.GENERAL,
        expiry_date: Optional[datetime] = None,
    ) -> Document:
        # 1. Validation & Virus scanning
        mime_type = DocumentProcessor.validate_file(file_name, file_bytes)

        # 2. Text & Metadata Extraction
        extracted_text = DocumentProcessor.extract_text(mime_type, file_bytes)
        meta, detected_expiry, is_expired, is_expiring_soon = DocumentProcessor.extract_metadata(extracted_text, file_name)

        final_expiry = expiry_date or detected_expiry

        # 3. Create Document entity
        doc = Document(
            company_id=company_id,
            owner_id=user_id,
            file_name=file_name,
            mime_type=mime_type,
            size_bytes=len(file_bytes),
            storage_path="", # populated below
            category=category,
            status=DocumentProcessingState.PROCESSING,
            current_version=1,
            is_final=False,
            extracted_text=extracted_text,
            metadata_json=meta,
            expiry_date=final_expiry,
            is_expired=is_expired,
            is_expiring_soon=is_expiring_soon,
        )
        db.add(doc)
        await db.flush()

        # 4. Save to Storage
        storage_rel_path = StorageService.get_storage_path(company_id, doc.id, 1, file_name)
        await StorageService.save_file_bytes(storage_rel_path, file_bytes)
        doc.storage_path = storage_rel_path
        doc.status = DocumentProcessingState.PROCESSED

        # 5. Create Version 1 record
        v1 = DocumentVersion(
            document_id=doc.id,
            company_id=company_id,
            version_number=1,
            file_name=file_name,
            storage_path=storage_rel_path,
            size_bytes=len(file_bytes),
            change_summary="Initial upload (Draft v1)",
            created_by=user_id,
            is_final=False,
        )
        db.add(v1)
        await db.commit()
        await db.refresh(doc)

        # Audit log
        await AuditService.log(
            db=db,
            company_id=company_id,
            user_id=user_id,
            action="document.upload",
            resource_type="document",
            resource_id=doc.id,
            details={"file_name": file_name, "category": category.value, "size_bytes": len(file_bytes)},
        )

        return doc

    @staticmethod
    async def get_document(db: AsyncSession, company_id: str, document_id: str) -> Document:
        result = await db.execute(
            select(Document)
            .where(Document.id == document_id, Document.company_id == company_id)
            .options(selectinload(Document.versions))
        )
        doc = result.scalar_one_or_none()
        if not doc or doc.is_archived:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        return doc

    @staticmethod
    async def update_document(
        db: AsyncSession,
        company_id: str,
        user_id: str,
        document_id: str,
        data: DocumentUpdate,
    ) -> Document:
        doc = await DocumentService.get_document(db, company_id, document_id)

        # Non-negotiable rule 4:
        # Final documents are immutable. Any update creates a new version draft.
        if doc.is_final:
            doc.current_version += 1
            doc.is_final = False  # New version starts as mutable draft
            new_storage_path = StorageService.get_storage_path(
                company_id, doc.id, doc.current_version, doc.file_name
            )
            # Copy physical file to new version path
            from app.config import settings
            old_full_path = os.path.join(os.path.abspath(settings.STORAGE_LOCAL_DIR), doc.storage_path.replace("/", os.sep))
            if os.path.exists(old_full_path):
                with open(old_full_path, "rb") as f:
                    old_bytes = f.read()
                await StorageService.save_file_bytes(new_storage_path, old_bytes)

            # Create new version record
            new_v = DocumentVersion(
                document_id=doc.id,
                company_id=company_id,
                version_number=doc.current_version,
                file_name=doc.file_name,
                storage_path=new_storage_path,
                size_bytes=doc.size_bytes,
                change_summary=f"Draft v{doc.current_version} created from immutable final version v{doc.current_version - 1}",
                created_by=user_id,
                is_final=False,
            )
            db.add(new_v)
            doc.storage_path = new_storage_path

        # Apply updates
        if data.category:
            doc.category = data.category
        if data.expiry_date:
            doc.expiry_date = data.expiry_date
            now = datetime.utcnow()
            doc.is_expired = data.expiry_date < now
            doc.is_expiring_soon = now <= data.expiry_date <= now + timedelta(days=60)
        if data.metadata_json:
            merged_meta = dict(doc.metadata_json)
            merged_meta.update(data.metadata_json)
            doc.metadata_json = merged_meta
        if data.is_final is not None:
            doc.is_final = data.is_final

        await db.commit()
        await db.refresh(doc)

        await AuditService.log(
            db=db,
            company_id=company_id,
            user_id=user_id,
            action="document.update",
            resource_type="document",
            resource_id=doc.id,
            details={"version": doc.current_version, "is_final": doc.is_final},
        )
        return doc

    @staticmethod
    async def delete_document(db: AsyncSession, company_id: str, user_id: str, document_id: str) -> None:
        doc = await DocumentService.get_document(db, company_id, document_id)
        doc.is_archived = True
        doc.status = DocumentProcessingState.ARCHIVED
        await db.commit()

        await AuditService.log(
            db=db,
            company_id=company_id,
            user_id=user_id,
            action="document.delete",
            resource_type="document",
            resource_id=document_id,
            details={"file_name": doc.file_name},
        )

    @staticmethod
    async def search_documents(
        db: AsyncSession,
        company_id: str,
        params: DocumentSearchRequest,
    ) -> List[Document]:
        # Rule 1 & Rule 3: Always scoped by company_id
        query = select(Document).where(Document.company_id == company_id, Document.is_archived == False)

        if params.category:
            query = query.where(Document.category == params.category)
        if params.expired_only:
            query = query.where(Document.is_expired == True)
        if params.query:
            q = f"%{params.query.lower()}%"
            query = query.where(
                (Document.file_name.ilike(q)) | (Document.extracted_text.ilike(q))
            )

        query = query.order_by(Document.created_at.desc()).limit(params.limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    # Signature and Seal Approval Workflow
    @staticmethod
    async def request_signature(
        db: AsyncSession,
        company_id: str,
        user_id: str,
        document_id: str,
        signature_id: str,
        seal_id: Optional[str] = None,
    ) -> SignatureApprovalWorkflow:
        # Check document
        doc = await DocumentService.get_document(db, company_id, document_id)

        # Check signature belongs to company
        sig_res = await db.execute(
            select(CompanySignature).where(CompanySignature.id == signature_id, CompanySignature.company_id == company_id)
        )
        if not sig_res.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Signature not found")

        approval = SignatureApprovalWorkflow(
            company_id=company_id,
            document_id=document_id,
            signature_id=signature_id,
            seal_id=seal_id,
            status=ApprovalStatus.REQUESTED,
            requested_by=user_id,
        )
        db.add(approval)
        await db.commit()
        await db.refresh(approval)

        await AuditService.log(
            db=db,
            company_id=company_id,
            user_id=user_id,
            action="signature.request",
            resource_type="signature_approval",
            resource_id=approval.id,
            details={"document_id": document_id, "signature_id": signature_id},
        )
        return approval

    @staticmethod
    async def approve_and_apply_signature(
        db: AsyncSession,
        company_id: str,
        user_id: str,
        approval_id: str,
        approve: bool = True,
    ) -> SignatureApprovalWorkflow:
        result = await db.execute(
            select(SignatureApprovalWorkflow).where(
                SignatureApprovalWorkflow.id == approval_id,
                SignatureApprovalWorkflow.company_id == company_id,
            )
        )
        workflow = result.scalar_one_or_none()
        if not workflow:
            raise HTTPException(status_code=404, detail="Approval request not found")

        doc = await DocumentService.get_document(db, company_id, workflow.document_id)

        if approve:
            workflow.status = ApprovalStatus.APPLIED
            workflow.approved_by = user_id
            workflow.approved_at = datetime.utcnow()
            workflow.applied_at = datetime.utcnow()

            # Rule 9: Lock final version
            doc.is_final = True
            await db.commit()
            await db.refresh(workflow)

            await AuditService.log(
                db=db,
                company_id=company_id,
                user_id=user_id,
                action="signature.apply",
                resource_type="document",
                resource_id=doc.id,
                details={"approval_id": workflow.id, "locked_final": True},
            )
        else:
            workflow.status = ApprovalStatus.REJECTED
            await db.commit()
            await db.refresh(workflow)

        return workflow
