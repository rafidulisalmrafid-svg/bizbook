from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_tenant, require_roles, CurrentTenant
from app.models.user_company import RoleEnum
from app.schemas.operations import (
    ProposalCreate,
    ProposalUpdate,
    ProposalResponse,
    InvoiceCreate,
    InvoiceUpdate,
    InvoicePaymentCreate,
    InvoiceResponse,
    PortfolioCaseStudyCreate,
    PortfolioCaseStudyResponse,
    GenerateSocialCopyRequest,
    SocialPostResponse,
    DashboardMetrics,
)
from app.services.operations_service import OperationsService

router = APIRouter(prefix="/operations", tags=["Business Operations"])


# 1. Dashboard Metrics
@router.get("/dashboard/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    tenant: CurrentTenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    return await OperationsService.get_dashboard_metrics(db, tenant.company_id)


# 2. Proposals
@router.post("/proposals", response_model=ProposalResponse, status_code=status.HTTP_201_CREATED)
async def create_proposal(
    data: ProposalCreate,
    tenant: CurrentTenant = Depends(require_roles([RoleEnum.OWNER, RoleEnum.ADMIN, RoleEnum.MANAGER, RoleEnum.TENDER_MANAGER])),
    db: AsyncSession = Depends(get_db),
):
    return await OperationsService.create_proposal(db, tenant.company_id, data)


@router.get("/proposals", response_model=List[ProposalResponse])
async def list_proposals(
    tenant: CurrentTenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    return await OperationsService.list_proposals(db, tenant.company_id)


@router.get("/proposals/{proposal_id}", response_model=ProposalResponse)
async def get_proposal(
    proposal_id: str,
    tenant: CurrentTenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    proposal = await OperationsService.get_proposal(db, tenant.company_id, proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return proposal


@router.patch("/proposals/{proposal_id}", response_model=ProposalResponse)
async def update_proposal(
    proposal_id: str,
    data: ProposalUpdate,
    tenant: CurrentTenant = Depends(require_roles([RoleEnum.OWNER, RoleEnum.ADMIN, RoleEnum.MANAGER, RoleEnum.TENDER_MANAGER])),
    db: AsyncSession = Depends(get_db),
):
    updated = await OperationsService.update_proposal(db, tenant.company_id, proposal_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return updated


# 3. Invoices
@router.post("/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    data: InvoiceCreate,
    tenant: CurrentTenant = Depends(require_roles([RoleEnum.OWNER, RoleEnum.ADMIN, RoleEnum.MANAGER])),
    db: AsyncSession = Depends(get_db),
):
    return await OperationsService.create_invoice(db, tenant.company_id, data)


@router.get("/invoices", response_model=List[InvoiceResponse])
async def list_invoices(
    tenant: CurrentTenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    return await OperationsService.list_invoices(db, tenant.company_id)


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: str,
    tenant: CurrentTenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    invoice = await OperationsService.get_invoice(db, tenant.company_id, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.patch("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: str,
    data: InvoiceUpdate,
    tenant: CurrentTenant = Depends(require_roles([RoleEnum.OWNER, RoleEnum.ADMIN, RoleEnum.MANAGER])),
    db: AsyncSession = Depends(get_db),
):
    updated = await OperationsService.update_invoice(db, tenant.company_id, invoice_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return updated


@router.post("/invoices/{invoice_id}/payments", response_model=InvoiceResponse)
async def record_payment(
    invoice_id: str,
    payment: InvoicePaymentCreate,
    tenant: CurrentTenant = Depends(require_roles([RoleEnum.OWNER, RoleEnum.ADMIN, RoleEnum.MANAGER])),
    db: AsyncSession = Depends(get_db),
):
    updated = await OperationsService.record_payment(db, tenant.company_id, invoice_id, payment.amount)
    if not updated:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return updated


# 4. Portfolio Case Studies
@router.post("/case-studies", response_model=PortfolioCaseStudyResponse, status_code=status.HTTP_201_CREATED)
async def create_case_study(
    data: PortfolioCaseStudyCreate,
    tenant: CurrentTenant = Depends(require_roles([RoleEnum.OWNER, RoleEnum.ADMIN, RoleEnum.MANAGER])),
    db: AsyncSession = Depends(get_db),
):
    return await OperationsService.create_case_study(db, tenant.company_id, data)


@router.get("/case-studies", response_model=List[PortfolioCaseStudyResponse])
async def list_case_studies(
    public_only: bool = Query(False, description="Filter for client-approved public case studies"),
    tenant: CurrentTenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    return await OperationsService.list_case_studies(db, tenant.company_id, public_only=public_only)


# 5. AI Social Copy Generator
@router.post("/social/generate", response_model=SocialPostResponse)
async def generate_social_copy(
    request: GenerateSocialCopyRequest,
    tenant: CurrentTenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    return await OperationsService.generate_social_copy(db, tenant.company_id, tenant.user.id, request)
