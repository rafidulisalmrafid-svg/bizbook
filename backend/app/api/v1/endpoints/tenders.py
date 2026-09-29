from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.api.deps import require_permission, CurrentTenant
from app.models.user_company import PermissionEnum
from app.schemas.tender import (
    TenderCreate,
    TenderUpdate,
    TenderRead,
    TenderRequirementCreate,
    TenderRequirementRead,
    TenderProposalSectionRead,
    ReadinessScoreResponse,
)
from app.services.tender_service import TenderService

router = APIRouter()

@router.get("", response_model=List[TenderRead])
async def list_tenders(
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.TENDER_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    return await TenderService.list_tenders(db, tenant.company_id)

@router.post("", response_model=TenderRead, status_code=status.HTTP_201_CREATED)
async def create_tender(
    data: TenderCreate,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.TENDER_CREATE)),
    db: AsyncSession = Depends(get_db),
):
    return await TenderService.create_tender(db, tenant.company_id, data)

@router.get("/{tender_id}", response_model=TenderRead)
async def get_tender(
    tender_id: str,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.TENDER_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    return await TenderService.get_tender(db, tenant.company_id, tender_id)

@router.post("/{tender_id}/requirements", response_model=TenderRequirementRead, status_code=status.HTTP_201_CREATED)
async def add_tender_requirement(
    tender_id: str,
    data: TenderRequirementCreate,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.TENDER_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    return await TenderService.add_requirement(db, tenant.company_id, tender_id, data)

@router.post("/{tender_id}/match", response_model=ReadinessScoreResponse)
async def run_requirement_matching(
    tender_id: str,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.TENDER_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    return await TenderService.run_matching_engine(db, tenant.company_id, tender_id)

@router.get("/{tender_id}/readiness", response_model=ReadinessScoreResponse)
async def get_readiness_score(
    tender_id: str,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.TENDER_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    return await TenderService.calculate_readiness_score(db, tenant.company_id, tender_id)

@router.post("/{tender_id}/generate-proposal", response_model=List[TenderProposalSectionRead])
async def generate_proposal(
    tender_id: str,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.TENDER_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    return await TenderService.generate_proposal_sections(db, tenant.company_id, tender_id)

@router.get("/{tender_id}/export-zip")
async def export_tender_submission_zip(
    tender_id: str,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.TENDER_EXPORT)),
    db: AsyncSession = Depends(get_db),
):
    zip_bytes = await TenderService.export_submission_zip(db, tenant.company_id, tender_id)
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=Tender_Submission_Package_{tender_id[:8]}.zip"}
    )
