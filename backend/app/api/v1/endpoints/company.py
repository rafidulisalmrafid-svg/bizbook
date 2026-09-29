from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.api.deps import require_permission, CurrentTenant
from app.models.user_company import PermissionEnum
from app.schemas.company import (
    CompanyRead,
    CompanyProfileRead,
    CompanyProfileUpdate,
    CompanyBrandRead,
    CompanyBrandUpdate,
    CompanyContactCreate,
    CompanyContactRead,
    CompanyLetterheadCreate,
    CompanyLetterheadRead,
    CompanySignatureCreate,
    CompanySignatureRead,
    CompanySealCreate,
    CompanySealRead,
)
from app.services.company_service import CompanyService
from app.services.audit_service import AuditService

router = APIRouter()

@router.get("", response_model=CompanyRead)
async def get_current_company(
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.COMPANY_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    return await CompanyService.get_company(db, tenant.company_id)

@router.get("/profile", response_model=CompanyProfileRead)
async def get_company_profile(
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.COMPANY_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    return await CompanyService.get_profile(db, tenant.company_id)

@router.put("/profile", response_model=CompanyProfileRead)
async def update_company_profile(
    data: CompanyProfileUpdate,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.COMPANY_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    updated = await CompanyService.update_profile(db, tenant.company_id, data)
    await AuditService.log(
        db=db,
        company_id=tenant.company_id,
        user_id=tenant.user.id,
        action="company.profile_update",
        resource_type="company_profile",
        resource_id=updated.id,
    )
    return updated

@router.get("/brand", response_model=CompanyBrandRead)
async def get_company_brand(
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.COMPANY_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    return await CompanyService.get_brand(db, tenant.company_id)

@router.put("/brand", response_model=CompanyBrandRead)
async def update_company_brand(
    data: CompanyBrandUpdate,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.COMPANY_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    updated = await CompanyService.update_brand(db, tenant.company_id, data)
    await AuditService.log(
        db=db,
        company_id=tenant.company_id,
        user_id=tenant.user.id,
        action="company.brand_update",
        resource_type="company_brand",
        resource_id=updated.id,
    )
    return updated

# Contacts
@router.get("/contacts", response_model=List[CompanyContactRead])
async def list_contacts(
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.COMPANY_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    return await CompanyService.list_contacts(db, tenant.company_id)

@router.post("/contacts", response_model=CompanyContactRead, status_code=status.HTTP_201_CREATED)
async def create_contact(
    data: CompanyContactCreate,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.COMPANY_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    return await CompanyService.create_contact(db, tenant.company_id, data)

@router.delete("/contacts/{contact_id}")
async def delete_contact(
    contact_id: str,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.COMPANY_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    await CompanyService.delete_contact(db, tenant.company_id, contact_id)
    return {"message": "Contact deleted successfully"}

# Letterhead
@router.get("/letterheads", response_model=List[CompanyLetterheadRead])
async def list_letterheads(
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.COMPANY_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    return await CompanyService.list_letterheads(db, tenant.company_id)

@router.post("/letterheads", response_model=CompanyLetterheadRead, status_code=status.HTTP_201_CREATED)
async def create_letterhead(
    data: CompanyLetterheadCreate,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.COMPANY_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    return await CompanyService.create_letterhead(db, tenant.company_id, data)

# Signatures & Seals (Enforces SIGNATURE_USE / SEAL_USE permissions)
@router.get("/signatures", response_model=List[CompanySignatureRead])
async def list_signatures(
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.COMPANY_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    return await CompanyService.list_signatures(db, tenant.company_id)

@router.post("/signatures", response_model=CompanySignatureRead, status_code=status.HTTP_201_CREATED)
async def create_signature(
    data: CompanySignatureCreate,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.SIGNATURE_USE)),
    db: AsyncSession = Depends(get_db),
):
    sig = await CompanyService.create_signature(db, tenant.company_id, data, user_id=tenant.user.id)
    await AuditService.log(
        db=db,
        company_id=tenant.company_id,
        user_id=tenant.user.id,
        action="signature.create",
        resource_type="signature",
        resource_id=sig.id,
    )
    return sig

@router.get("/seals", response_model=List[CompanySealRead])
async def list_seals(
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.COMPANY_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    return await CompanyService.list_seals(db, tenant.company_id)

@router.post("/seals", response_model=CompanySealRead, status_code=status.HTTP_201_CREATED)
async def create_seal(
    data: CompanySealCreate,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.SEAL_USE)),
    db: AsyncSession = Depends(get_db),
):
    seal = await CompanyService.create_seal(db, tenant.company_id, data)
    await AuditService.log(
        db=db,
        company_id=tenant.company_id,
        user_id=tenant.user.id,
        action="seal.create",
        resource_type="seal",
        resource_id=seal.id,
    )
    return seal
