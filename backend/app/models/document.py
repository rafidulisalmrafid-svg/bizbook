import enum
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text, Integer, JSON
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import TimestampMixin, generate_uuid

class DocumentProcessingState(str, enum.Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"

class DocumentCategory(str, enum.Enum):
    LEGAL = "LEGAL"
    FINANCIAL = "FINANCIAL"
    TECHNICAL = "TECHNICAL"
    EXPERIENCE = "EXPERIENCE"
    COMPLIANCE = "COMPLIANCE"
    TEAM = "TEAM"
    GENERAL = "GENERAL"

class ApprovalStatus(str, enum.Enum):
    REQUESTED = "REQUESTED"
    REVIEWED = "REVIEWED"
    APPROVED = "APPROVED"
    APPLIED = "APPLIED"
    REJECTED = "REJECTED"

class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    owner_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    file_name = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=False)
    size_bytes = Column(Integer, default=0, nullable=False)
    storage_path = Column(String(512), nullable=False)
    category = Column(SQLEnum(DocumentCategory), default=DocumentCategory.GENERAL, nullable=False)
    status = Column(SQLEnum(DocumentProcessingState), default=DocumentProcessingState.UPLOADED, nullable=False)
    is_final = Column(Boolean, default=False, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)
    current_version = Column(Integer, default=1, nullable=False)
    
    extracted_text = Column(Text, nullable=True)
    metadata_json = Column(JSON, default=dict, nullable=False)
    expiry_date = Column(DateTime, nullable=True)
    is_expired = Column(Boolean, default=False, nullable=False)
    is_expiring_soon = Column(Boolean, default=False, nullable=False)

    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
    approvals = relationship("SignatureApprovalWorkflow", back_populates="document", cascade="all, delete-orphan")

class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    file_name = Column(String(255), nullable=False)
    storage_path = Column(String(512), nullable=False)
    size_bytes = Column(Integer, default=0, nullable=False)
    change_summary = Column(Text, nullable=True)
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_final = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    document = relationship("Document", back_populates="versions")

class DocumentTemplate(Base, TimestampMixin):
    __tablename__ = "document_templates"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), default="Proposal", nullable=False)
    content = Column(Text, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    is_approved = Column(Boolean, default=False, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)

class SignatureApprovalWorkflow(Base):
    __tablename__ = "signature_approvals"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    signature_id = Column(String(36), ForeignKey("company_signatures.id", ondelete="CASCADE"), nullable=False)
    seal_id = Column(String(36), ForeignKey("company_seals.id", ondelete="SET NULL"), nullable=True)
    status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.REQUESTED, nullable=False)
    requested_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    applied_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    document = relationship("Document", back_populates="approvals")
