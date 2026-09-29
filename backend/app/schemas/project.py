from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.business import ProjectStatusEnum

class ProjectTeamMemberCreate(BaseModel):
    team_member_id: str
    role_in_project: str = "Contributor"

class ProjectTeamMemberRead(ProjectTeamMemberCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    created_at: datetime

class ProjectDocumentCreate(BaseModel):
    title: str
    document_url: str
    document_type: str = "EVIDENCE"
    notes: Optional[str] = None

class ProjectDocumentRead(ProjectDocumentCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    created_at: datetime

class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    client_id: Optional[str] = None
    service_id: Optional[str] = None
    status: ProjectStatusEnum = ProjectStatusEnum.IN_PROGRESS
    contract_value: float = 0.0
    currency: str = "USD"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    completion_summary: Optional[str] = None

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    client_id: Optional[str] = None
    service_id: Optional[str] = None
    status: Optional[ProjectStatusEnum] = None
    contract_value: Optional[float] = None
    currency: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    completion_summary: Optional[str] = None

class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    client_id: Optional[str] = None
    service_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: ProjectStatusEnum
    contract_value: float
    currency: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    completion_summary: Optional[str] = None
    portfolio_draft_created: bool
    is_archived: bool
    created_at: datetime
    team_members: List[ProjectTeamMemberRead] = []
    documents: List[ProjectDocumentRead] = []

class PortfolioDraftResponse(BaseModel):
    project_id: str
    title: str
    client_name: Optional[str] = None
    challenge: str
    solution: str
    results_and_impact: str
    technologies_used: List[str]
    evidence_count: int
    is_ready_for_review: bool = True
