from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.api.deps import require_permission, CurrentTenant
from app.models.user_company import PermissionEnum
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectRead,
    ProjectTeamMemberCreate,
    ProjectTeamMemberRead,
    ProjectDocumentCreate,
    ProjectDocumentRead,
    PortfolioDraftResponse,
)
from app.services.project_service import ProjectService
from app.services.audit_service import AuditService

router = APIRouter()

@router.get("", response_model=List[ProjectRead])
async def list_projects(
    include_archived: bool = False,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.PROJECT_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    return await ProjectService.list_projects(db, tenant.company_id, include_archived=include_archived)

@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.PROJECT_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    project = await ProjectService.create_project(db, tenant.company_id, data)
    await AuditService.log(
        db=db,
        company_id=tenant.company_id,
        user_id=tenant.user.id,
        action="project.create",
        resource_type="project",
        resource_id=project.id,
    )
    return project

@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: str,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.PROJECT_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    return await ProjectService.get_project(db, tenant.company_id, project_id)

@router.put("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: str,
    data: ProjectUpdate,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.PROJECT_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    updated = await ProjectService.update_project(db, tenant.company_id, project_id, data)
    await AuditService.log(
        db=db,
        company_id=tenant.company_id,
        user_id=tenant.user.id,
        action="project.update",
        resource_type="project",
        resource_id=updated.id,
    )
    return updated

@router.delete("/{project_id}")
async def archive_project(
    project_id: str,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.PROJECT_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    archived = await ProjectService.archive_project(db, tenant.company_id, project_id)
    await AuditService.log(
        db=db,
        company_id=tenant.company_id,
        user_id=tenant.user.id,
        action="project.archive",
        resource_type="project",
        resource_id=archived.id,
    )
    return {"message": "Project archived successfully"}

@router.post("/{project_id}/team", response_model=ProjectTeamMemberRead, status_code=status.HTTP_201_CREATED)
async def assign_team_member(
    project_id: str,
    data: ProjectTeamMemberCreate,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.PROJECT_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    return await ProjectService.assign_team_member(db, tenant.company_id, project_id, data)

@router.post("/{project_id}/documents", response_model=ProjectDocumentRead, status_code=status.HTTP_201_CREATED)
async def add_project_document(
    project_id: str,
    data: ProjectDocumentCreate,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.PROJECT_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    return await ProjectService.add_document(db, tenant.company_id, project_id, data)

@router.post("/{project_id}/portfolio-draft", response_model=PortfolioDraftResponse)
async def create_portfolio_draft(
    project_id: str,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.PROJECT_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    draft = await ProjectService.create_portfolio_draft(db, tenant.company_id, project_id)
    await AuditService.log(
        db=db,
        company_id=tenant.company_id,
        user_id=tenant.user.id,
        action="portfolio.draft_created",
        resource_type="project",
        resource_id=project_id,
    )
    return draft
