from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.api.deps import require_permission, CurrentTenant
from app.models.user_company import PermissionEnum
from app.models.business import AuditLog
from app.schemas.service import AuditLogRead

router = APIRouter()

@router.get("", response_model=List[AuditLogRead])
async def list_audit_logs(
    limit: int = 50,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.AUDIT_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(AuditLog)
        .where(AuditLog.company_id == tenant.company_id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    return list(result.scalars().all())
