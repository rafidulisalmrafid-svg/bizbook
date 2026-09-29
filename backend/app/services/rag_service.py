from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.ai import Subscription, AIUsageLog, PlanTier, Notification, NotificationType
from app.models.user_company import Company, CompanyProfile
from app.models.document import Document
from app.models.business import Project, TeamMember, Client
from app.services.ai.factory import AIFactory
from app.services.audit_service import AuditService

class RAGService:
    @staticmethod
    async def check_quota_and_log_usage(
        db: AsyncSession,
        company_id: str,
        user_id: str,
        ai_res: Any,
        operation: str,
    ) -> None:
        # Check / create subscription
        sub_res = await db.execute(select(Subscription).where(Subscription.company_id == company_id))
        sub = sub_res.scalar_one_or_none()
        if not sub:
            sub = Subscription(company_id=company_id, plan_tier=PlanTier.PROFESSIONAL, monthly_token_quota=500000)
            db.add(sub)
            await db.flush()

        if sub.tokens_consumed + ai_res.total_tokens > sub.monthly_token_quota:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Monthly AI token quota exceeded ({sub.tokens_consumed}/{sub.monthly_token_quota} tokens used). Please upgrade plan."
            )

        sub.tokens_consumed += ai_res.total_tokens

        # Record usage log
        usage_log = AIUsageLog(
            company_id=company_id,
            user_id=user_id,
            provider=ai_res.provider,
            model=ai_res.model,
            operation=operation,
            prompt_version=ai_res.prompt_version,
            prompt_tokens=ai_res.prompt_tokens,
            completion_tokens=ai_res.completion_tokens,
            total_tokens=ai_res.total_tokens,
            estimated_cost_usd=ai_res.estimated_cost_usd,
            latency_ms=ai_res.latency_ms,
        )
        db.add(usage_log)
        await db.commit()

    @staticmethod
    async def retrieve_company_memory(
        db: AsyncSession,
        company_id: str,
        query: str,
    ) -> Dict[str, Any]:
        """
        Retrieves grounded company records strictly scoped by company_id.
        Only approved/verified records are retrieved.
        """
        # 1. Company Profile
        prof_res = await db.execute(select(CompanyProfile).where(CompanyProfile.company_id == company_id))
        profile = prof_res.scalar_one_or_none()

        # 2. Authorized Vault documents
        docs_res = await db.execute(
            select(Document).where(Document.company_id == company_id, Document.is_archived == False)
        )
        vault_docs = list(docs_res.scalars().all())

        # 3. Verified Projects
        proj_res = await db.execute(
            select(Project).where(Project.company_id == company_id, Project.is_archived == False)
        )
        projects = list(proj_res.scalars().all())

        # 4. Verified Team
        team_res = await db.execute(
            select(TeamMember).where(TeamMember.company_id == company_id, TeamMember.is_archived == False)
        )
        team = list(team_res.scalars().all())

        return {
            "company_name": profile.company.name if profile and profile.company else "Company",
            "overview": profile.overview if profile else None,
            "annual_turnover": profile.annual_turnover if profile else None,
            "vault_documents": [{"id": d.id, "file_name": d.file_name, "category": d.category.value, "is_final": d.is_final} for d in vault_docs],
            "projects": [{"id": p.id, "title": p.title, "value": p.contract_value, "status": p.status.value} for p in projects],
            "team_members": [{"id": m.id, "name": m.full_name, "designation": m.designation, "skills": m.skills} for m in team],
        }

    @staticmethod
    async def generate_document(
        db: AsyncSession,
        company_id: str,
        user_id: str,
        document_type: str,
        user_instruction: str,
        required_certifications: Optional[List[str]] = None,
        provider_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        # 1. Retrieve tenant-scoped memory
        memory = await RAGService.retrieve_company_memory(db, company_id, user_instruction)

        # 2. Zero-Hallucination rule verification
        # Check if required certifications actually exist in company vault
        missing_information = []
        sources = []
        warnings = []

        if required_certifications:
            existing_doc_names = " ".join([d["file_name"].lower() for d in memory["vault_documents"]])
            for req_cert in required_certifications:
                if req_cert.lower() not in existing_doc_names:
                    # Explicitly flag missing requirement instead of fabricating!
                    missing_information.append(f"Missing Certification: '{req_cert}' not found in company vault.")
                else:
                    sources.append(f"Vault Document: {req_cert}")

        # Add verified projects to sources
        for p in memory["projects"]:
            sources.append(f"Project: {p['title']} (${p['value']:,.2f})")

        warnings.append("AI-generated content requires human review before legal or financial submission.")

        # 3. Call AI Provider
        prompt = f"""
        Document Type: {document_type}
        Instructions: {user_instruction}
        Company Memory: {memory}
        Missing Items: {missing_information}
        """
        ai = AIFactory.get_provider(provider_name)
        ai_res = await ai.generate_text(
            prompt=prompt,
            system_message="You are BizBook Grounded Proposal Engine. Never fabricate unverified claims."
        )

        # 4. Check quota and record usage log
        await RAGService.check_quota_and_log_usage(db, company_id, user_id, ai_res, f"generate_{document_type}")

        # 5. Format structured response
        response = {
            "title": f"Draft: {document_type.replace('_', ' ').title()}",
            "sections": [
                {"heading": "Executive Summary", "content": f"Proposal prepared for {memory['company_name']}."},
                {"heading": "Technical Methodology", "content": ai_res.content},
            ],
            "content": ai_res.content,
            "sources": sources,
            "warnings": warnings,
            "missing_information": missing_information,
            "token_usage": {
                "total_tokens": ai_res.total_tokens,
                "estimated_cost_usd": ai_res.estimated_cost_usd,
            }
        }

        # 6. Audit log
        await AuditService.log(
            db=db,
            company_id=company_id,
            user_id=user_id,
            action="ai.generate_document",
            resource_type="ai_generation",
            details={
                "document_type": document_type,
                "tokens": ai_res.total_tokens,
                "missing_count": len(missing_information),
            }
        )

        return response
