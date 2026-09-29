from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.api.deps import require_permission, CurrentTenant
from app.models.user_company import PermissionEnum
from app.models.ai import AIUsageLog, Subscription, Notification, NotificationType
from app.services.rag_service import RAGService
from app.services.ai.factory import AIFactory

router = APIRouter()

class DocumentGenerationRequest(BaseModel):
    document_type: str = "TENDER_PROPOSAL"
    user_instruction: str
    required_certifications: List[str] = []
    provider: Optional[str] = None

class AskMemoryRequest(BaseModel):
    query: str

class NotificationCreate(BaseModel):
    type: NotificationType
    title: str
    message: str
    resource_type: str
    resource_id: Optional[str] = None

@router.post("/generate-document")
async def generate_document(
    data: DocumentGenerationRequest,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.TENDER_CREATE)),
    db: AsyncSession = Depends(get_db),
):
    return await RAGService.generate_document(
        db=db,
        company_id=tenant.company_id,
        user_id=tenant.user.id,
        document_type=data.document_type,
        user_instruction=data.user_instruction,
        required_certifications=data.required_certifications,
        provider_name=data.provider,
    )

@router.post("/ask-memory")
async def ask_company_memory(
    data: AskMemoryRequest,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.COMPANY_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    # Rule 3: Strict cross-tenant isolation
    memory = await RAGService.retrieve_company_memory(db, tenant.company_id, data.query)
    ai = AIFactory.get_provider()
    ai_res = await ai.generate_text(
        prompt=f"User Query: {data.query}\nCompany Grounded Data: {memory}",
        system_message="Answer based only on verified company records. If missing, say MISSING."
    )
    return {
        "query": data.query,
        "answer": ai_res.content,
        "grounded_sources": len(memory["vault_documents"]) + len(memory["projects"]),
        "provider": ai_res.provider,
    }

@router.get("/usage")
async def get_usage_and_quotas(
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.AUDIT_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    sub_res = await db.execute(select(Subscription).where(Subscription.company_id == tenant.company_id))
    sub = sub_res.scalar_one_or_none()

    logs_res = await db.execute(
        select(AIUsageLog)
        .where(AIUsageLog.company_id == tenant.company_id)
        .order_by(AIUsageLog.created_at.desc())
        .limit(20)
    )
    logs = list(logs_res.scalars().all())

    return {
        "monthly_token_quota": sub.monthly_token_quota if sub else 500000,
        "tokens_consumed": sub.tokens_consumed if sub else 0,
        "plan_tier": sub.plan_tier if sub else "PROFESSIONAL",
        "recent_logs": [
            {
                "id": l.id,
                "model": l.model,
                "operation": l.operation,
                "total_tokens": l.total_tokens,
                "cost_usd": l.estimated_cost_usd,
                "created_at": l.created_at,
            }
            for l in logs
        ]
    }

@router.get("/notifications")
async def list_notifications(
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.COMPANY_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Notification)
        .where(Notification.company_id == tenant.company_id)
        .order_by(Notification.created_at.desc())
        .limit(30)
    )
    result = await db.execute(query)
    return list(result.scalars().all())

@router.post("/notifications", status_code=status.HTTP_201_CREATED)
async def create_notification(
    data: NotificationCreate,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.COMPANY_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    notif = Notification(
        company_id=tenant.company_id,
        user_id=tenant.user.id,
        **data.model_dump(),
    )
    db.add(notif)
    await db.commit()
    await db.refresh(notif)
    return notif
