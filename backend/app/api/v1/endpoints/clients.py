from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.api.deps import require_permission, CurrentTenant
from app.models.user_company import PermissionEnum
from app.schemas.client import (
    ClientCreate,
    ClientUpdate,
    ClientRead,
    ClientContactCreate,
    ClientContactRead,
)
from app.services.client_service import ClientService
from app.services.audit_service import AuditService

router = APIRouter()

@router.get("", response_model=List[ClientRead])
async def list_clients(
    include_archived: bool = False,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.CLIENT_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    return await ClientService.list_clients(db, tenant.company_id, include_archived=include_archived)

@router.post("", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
async def create_client(
    data: ClientCreate,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.CLIENT_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    client = await ClientService.create_client(db, tenant.company_id, data)
    await AuditService.log(
        db=db,
        company_id=tenant.company_id,
        user_id=tenant.user.id,
        action="client.create",
        resource_type="client",
        resource_id=client.id,
    )
    return client

@router.get("/{client_id}", response_model=ClientRead)
async def get_client(
    client_id: str,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.CLIENT_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    return await ClientService.get_client(db, tenant.company_id, client_id)

@router.put("/{client_id}", response_model=ClientRead)
async def update_client(
    client_id: str,
    data: ClientUpdate,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.CLIENT_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    updated = await ClientService.update_client(db, tenant.company_id, client_id, data)
    await AuditService.log(
        db=db,
        company_id=tenant.company_id,
        user_id=tenant.user.id,
        action="client.update",
        resource_type="client",
        resource_id=updated.id,
    )
    return updated

@router.delete("/{client_id}")
async def archive_client(
    client_id: str,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.CLIENT_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    archived = await ClientService.archive_client(db, tenant.company_id, client_id)
    await AuditService.log(
        db=db,
        company_id=tenant.company_id,
        user_id=tenant.user.id,
        action="client.archive",
        resource_type="client",
        resource_id=archived.id,
    )
    return {"message": "Client archived successfully"}

@router.post("/{client_id}/contacts", response_model=ClientContactRead, status_code=status.HTTP_201_CREATED)
async def add_client_contact(
    client_id: str,
    data: ClientContactCreate,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.CLIENT_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    return await ClientService.add_contact(db, tenant.company_id, client_id, data)
