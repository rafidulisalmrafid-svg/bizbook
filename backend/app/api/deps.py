from typing import List, Optional, Set
from fastapi import Depends, HTTPException, status, Header, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.core.security import decode_access_token
from app.models.user_company import (
    User,
    Company,
    Membership,
    RoleEnum,
    PermissionEnum,
    ROLE_PERMISSIONS,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

class CurrentTenant:
    def __init__(
        self,
        user: User,
        company_id: str,
        role: RoleEnum,
        permissions: Set[str],
    ):
        self.user = user
        self.company_id = company_id
        self.role = role
        self.permissions = permissions

    def has_permission(self, permission: PermissionEnum) -> bool:
        return permission.value in self.permissions or self.role == RoleEnum.OWNER

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id, User.is_active == True))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or account disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_tenant(
    token: str = Depends(oauth2_scheme),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID"),
) -> CurrentTenant:
    payload = decode_access_token(token)
    token_company_id = payload.get("company_id") if payload else None
    
    # Priority: Header (if user has membership in that company) else Token company_id
    target_company_id = x_company_id or token_company_id
    if not target_company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No tenant context provided",
        )

    # Server-side verification of membership in this company
    result = await db.execute(
        select(Membership).where(
            Membership.company_id == target_company_id,
            Membership.user_id == user.id,
            Membership.is_active == True,
        )
    )
    membership = result.scalar_one_or_none()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this company or access has been revoked.",
        )

    role_perms = set(p.value for p in ROLE_PERMISSIONS.get(membership.role, []))

    return CurrentTenant(
        user=user,
        company_id=membership.company_id,
        role=membership.role,
        permissions=role_perms,
    )

def require_permission(required_perm: PermissionEnum):
    async def permission_checker(
        tenant: CurrentTenant = Depends(get_current_tenant),
    ) -> CurrentTenant:
        if not tenant.has_permission(required_perm):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required permission: {required_perm.value}",
            )
        return tenant
    return permission_checker

def require_roles(allowed_roles: List[RoleEnum]):
    async def role_checker(
        tenant: CurrentTenant = Depends(get_current_tenant),
    ) -> CurrentTenant:
        if tenant.role not in allowed_roles and tenant.role != RoleEnum.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Insufficient role privileges.",
            )
        return tenant
    return role_checker
