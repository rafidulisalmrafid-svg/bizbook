from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, Field
from app.models.operations import ProposalStatus, InvoiceStatus, SocialPlatform


# Line Items
class ProposalLineItemBase(BaseModel):
    description: str
    quantity: float = 1.0
    unit_price: float = 0.0


class ProposalLineItemCreate(ProposalLineItemBase):
    pass


class ProposalLineItemResponse(ProposalLineItemBase):
    id: str
    proposal_id: str
    amount: float
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Proposals
class ProposalBase(BaseModel):
    title: str
    client_id: Optional[str] = None
    project_id: Optional[str] = None
    description: Optional[str] = None
    valid_until: Optional[datetime] = None
    currency: str = "USD"
    discount: float = 0.0
    tax_rate: float = 0.0
    terms_and_conditions: Optional[str] = None


class ProposalCreate(ProposalBase):
    line_items: List[ProposalLineItemCreate] = []


class ProposalUpdate(BaseModel):
    title: Optional[str] = None
    client_id: Optional[str] = None
    project_id: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProposalStatus] = None
    valid_until: Optional[datetime] = None
    currency: Optional[str] = None
    discount: Optional[float] = None
    tax_rate: Optional[float] = None
    terms_and_conditions: Optional[str] = None
    line_items: Optional[List[ProposalLineItemCreate]] = None


class ProposalResponse(ProposalBase):
    id: str
    company_id: str
    status: ProposalStatus
    subtotal: float
    tax_amount: float
    total_amount: float
    line_items: List[ProposalLineItemResponse] = []
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Invoices
class InvoiceLineItemBase(BaseModel):
    description: str
    quantity: float = 1.0
    unit_price: float = 0.0


class InvoiceLineItemCreate(InvoiceLineItemBase):
    pass


class InvoiceLineItemResponse(InvoiceLineItemBase):
    id: str
    invoice_id: str
    amount: float
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class InvoiceBase(BaseModel):
    client_id: str
    project_id: Optional[str] = None
    proposal_id: Optional[str] = None
    invoice_number: str
    issue_date: date
    due_date: date
    currency: str = "USD"
    discount: float = 0.0
    tax_rate: float = 0.0
    notes: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    line_items: List[InvoiceLineItemCreate] = []


class InvoiceUpdate(BaseModel):
    client_id: Optional[str] = None
    status: Optional[InvoiceStatus] = None
    issue_date: Optional[date] = None
    due_date: Optional[date] = None
    discount: Optional[float] = None
    tax_rate: Optional[float] = None
    notes: Optional[str] = None
    paid_amount: Optional[float] = None


class InvoicePaymentCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Payment amount to apply to invoice")


class InvoiceResponse(InvoiceBase):
    id: str
    company_id: str
    status: InvoiceStatus
    subtotal: float
    tax_amount: float
    total_amount: float
    paid_amount: float
    line_items: List[InvoiceLineItemResponse] = []
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Case Studies
class PortfolioCaseStudyBase(BaseModel):
    project_id: str
    title: str
    headline: str
    client_display_name: str
    challenge: str
    solution: str
    results_and_impact: str
    metrics: Dict[str, Any] = {}
    is_public_approved: bool = False
    technologies: List[str] = []


class PortfolioCaseStudyCreate(PortfolioCaseStudyBase):
    pass


class PortfolioCaseStudyUpdate(BaseModel):
    title: Optional[str] = None
    headline: Optional[str] = None
    client_display_name: Optional[str] = None
    challenge: Optional[str] = None
    solution: Optional[str] = None
    results_and_impact: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    is_public_approved: Optional[bool] = None
    technologies: Optional[List[str]] = None


class PortfolioCaseStudyResponse(PortfolioCaseStudyBase):
    id: str
    company_id: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Social Copy & AI Marketing
class GenerateSocialCopyRequest(BaseModel):
    project_id: Optional[str] = None
    case_study_id: Optional[str] = None
    platform: SocialPlatform = SocialPlatform.LINKEDIN
    tone: str = "professional"
    key_takeaway: Optional[str] = None


class SocialPostResponse(BaseModel):
    id: str
    company_id: str
    project_id: Optional[str] = None
    platform: SocialPlatform
    content: str
    hashtags: List[str] = []
    call_to_action: Optional[str] = None
    is_published: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Executive Dashboard Analytics
class DashboardMetrics(BaseModel):
    total_clients: int
    active_projects: int
    completed_projects: int
    open_proposals_count: int
    open_proposals_value: float
    invoices_total_receivable: float
    invoices_total_paid: float
    invoices_overdue_count: int
    active_tenders_count: int
    expiring_documents_count: int
    recent_activity: List[Dict[str, Any]] = []
