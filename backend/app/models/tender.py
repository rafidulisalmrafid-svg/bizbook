import enum
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text, Integer, Float, JSON
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import TimestampMixin, generate_uuid

class RequirementType(str, enum.Enum):
    LEGAL = "LEGAL"
    FINANCIAL = "FINANCIAL"
    EXPERIENCE = "EXPERIENCE"
    TECHNICAL = "TECHNICAL"
    TEAM = "TEAM"
    DOCUMENT = "DOCUMENT"
    TIMELINE = "TIMELINE"
    BUDGET = "BUDGET"
    DECLARATION = "DECLARATION"
    OTHER = "OTHER"

class MatchingStatus(str, enum.Enum):
    READY = "READY"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    EXPIRED = "EXPIRED"
    GENERATE = "GENERATE"
    REVIEW = "REVIEW"
    NOT_APPLICABLE = "NOT_APPLICABLE"

class TenderStatus(str, enum.Enum):
    ANALYZING = "ANALYZING"
    MATCHING = "MATCHING"
    DRAFTING = "DRAFTING"
    READY = "READY"
    SUBMITTED = "SUBMITTED"
    WON = "WON"
    LOST = "LOST"

class Tender(Base, TimestampMixin):
    __tablename__ = "tenders"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    reference_number = Column(String(100), nullable=True)
    issuing_organization = Column(String(255), nullable=False)
    deadline = Column(DateTime, nullable=True)
    estimated_budget = Column(Float, default=0.0, nullable=False)
    currency = Column(String(10), default="USD", nullable=False)
    status = Column(SQLEnum(TenderStatus), default=TenderStatus.ANALYZING, nullable=False)
    readiness_score = Column(Float, default=0.0, nullable=False)
    blocking_issues_count = Column(Integer, default=0, nullable=False)
    non_blocking_issues_count = Column(Integer, default=0, nullable=False)

    requirements = relationship("TenderRequirement", back_populates="tender", cascade="all, delete-orphan")
    sections = relationship("TenderProposalSection", back_populates="tender", cascade="all, delete-orphan")

class TenderRequirement(Base, TimestampMixin):
    __tablename__ = "tender_requirements"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tender_id = Column(String(36), ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False, index=True)
    section = Column(String(100), default="General", nullable=False)
    requirement_text = Column(Text, nullable=False)
    requirement_type = Column(SQLEnum(RequirementType), default=RequirementType.TECHNICAL, nullable=False)
    mandatory = Column(Boolean, default=True, nullable=False)
    deadline = Column(DateTime, nullable=True)
    evidence_type = Column(String(100), nullable=True)
    status = Column(SQLEnum(MatchingStatus), default=MatchingStatus.REVIEW, nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)
    source_document_id = Column(String(100), nullable=True)
    source_page = Column(Integer, default=1, nullable=False)
    matched_evidence_id = Column(String(100), nullable=True)
    matched_evidence_type = Column(String(50), nullable=True) # PROJECT, DOCUMENT, TEAM
    matched_evidence_title = Column(String(255), nullable=True)
    matching_reason = Column(Text, nullable=True)
    is_user_approved = Column(Boolean, default=False, nullable=False)

    tender = relationship("Tender", back_populates="requirements")

class TenderProposalSection(Base, TimestampMixin):
    __tablename__ = "tender_proposal_sections"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tender_id = Column(String(36), ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False, index=True)
    section_key = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    is_approved = Column(Boolean, default=False, nullable=False)

    tender = relationship("Tender", back_populates="sections")
