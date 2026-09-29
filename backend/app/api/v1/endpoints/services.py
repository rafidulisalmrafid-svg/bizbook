from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.api.deps import require_permission, CurrentTenant
from app.models.user_company import PermissionEnum
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceRead
from app.services.service_service import ServiceCatalogService
from app.services.audit_service import AuditService

router = APIRouter()

@router.get("", response_model=List[ServiceRead])
async def list_services(
    include_archived: bool = False,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.SERVICE_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    return await ServiceCatalogService.list_services(db, tenant.company_id, include_archived=include_archived)

@router.post("", response_model=ServiceRead, status_code=status.HTTP_201_CREATED)
async def create_service(
    data: ServiceCreate,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.SERVICE_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = await ServiceCatalogService.create_service(db, tenant.company_id, data)
    await AuditService.log(
        db=db,
        company_id=tenant.company_id,
        user_id=tenant.user.id,
        action="service.create",
        resource_type="service",
        resource_id=service.id,
    )
    return service

@router.get("/{service_id}", response_model=ServiceRead)
async def get_service(
    service_id: str,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.SERVICE_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    return await ServiceCatalogService.get_service(db, tenant.company_id, service_id)

@router.put("/{service_id}", response_model=ServiceRead)
async def update_service(
    service_id: str,
    data: ServiceUpdate,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.SERVICE_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    updated = await ServiceCatalogService.update_service(db, tenant.company_id, service_id, data)
    await AuditService.log(
        db=db,
        company_id=tenant.company_id,
        user_id=tenant.user.id,
        action="service.update",
        resource_type="service",
        resource_id=updated.id,
    )
    return updated

@router.delete("/{service_id}")
async def archive_service(
    service_id: str,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.SERVICE_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    archived = await ServiceCatalogService.archive_service(db, tenant.company_id, service_id)
    await AuditService.log(
        db=db,
        company_id=tenant.company_id,
        user_id=tenant.user.id,
        action="service.archive",
        resource_type="service",
        resource_id=archived.id,
    )
    return {"message": "Service archived successfully"}
