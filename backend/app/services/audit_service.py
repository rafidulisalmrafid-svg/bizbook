from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
from app.models.business import AuditLog

class AuditService:
    @staticmethod
    async def log(
        db: AsyncSession,
        company_id: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        audit_entry = AuditLog(
            company_id=company_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
        )
        db.add(audit_entry)
        await db.commit()
        await db.refresh(audit_entry)
        return audit_entry
