from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.api.deps import require_permission, CurrentTenant
from app.models.user_company import PermissionEnum
from app.schemas.team import (
    TeamMemberCreate,
    TeamMemberUpdate,
    TeamMemberRead,
    TeamExperienceCreate,
    TeamExperienceRead,
    TeamCertificationCreate,
    TeamCertificationRead,
)
from app.services.team_service import TeamService
from app.services.audit_service import AuditService

router = APIRouter()

@router.get("", response_model=List[TeamMemberRead])
async def list_team_members(
    include_archived: bool = False,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.TEAM_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    return await TeamService.list_members(db, tenant.company_id, include_archived=include_archived)

@router.post("", response_model=TeamMemberRead, status_code=status.HTTP_201_CREATED)
async def create_team_member(
    data: TeamMemberCreate,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.TEAM_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    member = await TeamService.create_member(db, tenant.company_id, data)
    await AuditService.log(
        db=db,
        company_id=tenant.company_id,
        user_id=tenant.user.id,
        action="team.member_create",
        resource_type="team_member",
        resource_id=member.id,
    )
    return member

@router.get("/{member_id}", response_model=TeamMemberRead)
async def get_team_member(
    member_id: str,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.TEAM_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    return await TeamService.get_member(db, tenant.company_id, member_id)

@router.put("/{member_id}", response_model=TeamMemberRead)
async def update_team_member(
    member_id: str,
    data: TeamMemberUpdate,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.TEAM_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    updated = await TeamService.update_member(db, tenant.company_id, member_id, data)
    await AuditService.log(
        db=db,
        company_id=tenant.company_id,
        user_id=tenant.user.id,
        action="team.member_update",
        resource_type="team_member",
        resource_id=updated.id,
    )
    return updated

@router.delete("/{member_id}")
async def archive_team_member(
    member_id: str,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.TEAM_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    archived = await TeamService.archive_member(db, tenant.company_id, member_id)
    await AuditService.log(
        db=db,
        company_id=tenant.company_id,
        user_id=tenant.user.id,
        action="team.member_archive",
        resource_type="team_member",
        resource_id=archived.id,
    )
    return {"message": "Team member successfully archived"}

@router.post("/{member_id}/experience", response_model=TeamExperienceRead, status_code=status.HTTP_201_CREATED)
async def add_member_experience(
    member_id: str,
    data: TeamExperienceCreate,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.TEAM_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    return await TeamService.add_experience(db, tenant.company_id, member_id, data)

@router.post("/{member_id}/certification", response_model=TeamCertificationRead, status_code=status.HTTP_201_CREATED)
async def add_member_certification(
    member_id: str,
    data: TeamCertificationCreate,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.TEAM_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    return await TeamService.add_certification(db, tenant.company_id, member_id, data)
