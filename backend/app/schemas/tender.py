from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.tender import RequirementType, MatchingStatus, TenderStatus

class TenderRequirementCreate(BaseModel):
    section: str = "General"
    requirement_text: str
    requirement_type: RequirementType = RequirementType.TECHNICAL
    mandatory: bool = True
    deadline: Optional[datetime] = None
    evidence_type: Optional[str] = None
    source_document_id: Optional[str] = None
    source_page: int = 1

class TenderRequirementUpdate(BaseModel):
    requirement_text: Optional[str] = None
    requirement_type: Optional[RequirementType] = None
    mandatory: Optional[bool] = None
    status: Optional[MatchingStatus] = None
    matched_evidence_id: Optional[str] = None
    matched_evidence_type: Optional[str] = None
    matched_evidence_title: Optional[str] = None
    matching_reason: Optional[str] = None
    is_user_approved: Optional[bool] = None

class TenderRequirementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tender_id: str
    section: str
    requirement_text: str
    requirement_type: RequirementType
    mandatory: bool
    deadline: Optional[datetime] = None
    evidence_type: Optional[str] = None
    status: MatchingStatus
    confidence: float
    source_document_id: Optional[str] = None
    source_page: int
    matched_evidence_id: Optional[str] = None
    matched_evidence_type: Optional[str] = None
    matched_evidence_title: Optional[str] = None
    matching_reason: Optional[str] = None
    is_user_approved: bool
    created_at: datetime

class TenderProposalSectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tender_id: str
    section_key: str
    title: str
    content: str
    sort_order: int
    is_approved: bool

class TenderCreate(BaseModel):
    title: str
    reference_number: Optional[str] = None
    issuing_organization: str
    deadline: Optional[datetime] = None
    estimated_budget: float = 0.0
    currency: str = "USD"

class TenderUpdate(BaseModel):
    title: Optional[str] = None
    reference_number: Optional[str] = None
    issuing_organization: Optional[str] = None
    deadline: Optional[datetime] = None
    estimated_budget: Optional[float] = None
    currency: Optional[str] = None
    status: Optional[TenderStatus] = None

class TenderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    title: str
    reference_number: Optional[str] = None
    issuing_organization: str
    deadline: Optional[datetime] = None
    estimated_budget: float
    currency: str
    status: TenderStatus
    readiness_score: float
    blocking_issues_count: int
    non_blocking_issues_count: int
    created_at: datetime
    requirements: List[TenderRequirementRead] = []
    sections: List[TenderProposalSectionRead] = []

class ReadinessScoreResponse(BaseModel):
    tender_id: str
    readiness_score: float
    blocking_issues_count: int
    non_blocking_issues_count: int
    blocking_issues: List[str]
    non_blocking_issues: List[str]
    disclaimer: str = "Readiness score is an internal compliance readiness indicator and never a guarantee of tender acceptance."

class TenderExportResponse(BaseModel):
    tender_id: str
    package_name: str
    file_count: int
    download_url: str
