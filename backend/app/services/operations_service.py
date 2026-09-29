import json
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload

from app.models.business import Client, Project, ProjectStatusEnum, AuditLog
from app.models.document import Document
from app.models.tender import Tender, TenderStatus
from app.models.operations import (
    Proposal,
    ProposalLineItem,
    ProposalStatus,
    Invoice,
    InvoiceLineItem,
    InvoiceStatus,
    PortfolioCaseStudy,
    SocialPost,
    SocialPlatform,
)
from app.schemas.operations import (
    ProposalCreate,
    ProposalUpdate,
    InvoiceCreate,
    InvoiceUpdate,
    PortfolioCaseStudyCreate,
    PortfolioCaseStudyUpdate,
    GenerateSocialCopyRequest,
    DashboardMetrics,
)
from app.services.ai.factory import AIFactory
from app.models.ai import AIUsageLog


class OperationsService:
    @staticmethod
    def _calculate_proposal_totals(line_items_data, discount: float, tax_rate: float):
        subtotal = sum(item.quantity * item.unit_price for item in line_items_data)
        taxable_amount = max(0.0, float(subtotal) - float(discount))
        tax_amount = taxable_amount * (float(tax_rate) / 100.0)
        total_amount = taxable_amount + tax_amount
        return float(subtotal), float(tax_amount), float(total_amount)

    @classmethod
    async def create_proposal(cls, db: AsyncSession, company_id: str, data: ProposalCreate) -> Proposal:
        subtotal, tax_amount, total_amount = cls._calculate_proposal_totals(
            data.line_items, data.discount, data.tax_rate
        )

        proposal = Proposal(
            company_id=company_id,
            client_id=data.client_id,
            project_id=data.project_id,
            title=data.title,
            description=data.description,
            status=ProposalStatus.DRAFT,
            valid_until=data.valid_until,
            currency=data.currency,
            subtotal=subtotal,
            discount=data.discount,
            tax_rate=data.tax_rate,
            tax_amount=tax_amount,
            total_amount=total_amount,
            terms_and_conditions=data.terms_and_conditions,
        )
        db.add(proposal)
        await db.flush()

        for item in data.line_items:
            line_item = ProposalLineItem(
                proposal_id=proposal.id,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                amount=item.quantity * item.unit_price,
            )
            db.add(line_item)

        await db.commit()

        # Re-query with eager load
        result = await db.execute(
            select(Proposal)
            .where(Proposal.id == proposal.id)
            .options(selectinload(Proposal.line_items))
        )
        return result.scalar_one()

    @classmethod
    async def get_proposal(cls, db: AsyncSession, company_id: str, proposal_id: str) -> Optional[Proposal]:
        result = await db.execute(
            select(Proposal)
            .where(and_(Proposal.id == proposal_id, Proposal.company_id == company_id))
            .options(selectinload(Proposal.line_items))
        )
        return result.scalar_one_or_none()

    @classmethod
    async def list_proposals(cls, db: AsyncSession, company_id: str) -> List[Proposal]:
        result = await db.execute(
            select(Proposal)
            .where(Proposal.company_id == company_id)
            .options(selectinload(Proposal.line_items))
            .order_by(desc(Proposal.created_at))
        )
        return list(result.scalars().all())

    @classmethod
    async def update_proposal(cls, db: AsyncSession, company_id: str, proposal_id: str, data: ProposalUpdate) -> Optional[Proposal]:
        proposal = await cls.get_proposal(db, company_id, proposal_id)
        if not proposal:
            return None

        update_dict = data.model_dump(exclude_unset=True)
        line_items_data = update_dict.pop("line_items", None)

        for field, value in update_dict.items():
            setattr(proposal, field, value)

        if line_items_data is not None:
            # Replace line items
            for existing in proposal.line_items:
                await db.delete(existing)
            await db.flush()

            for item_dict in line_items_data:
                li = ProposalLineItem(
                    proposal_id=proposal.id,
                    description=item_dict["description"],
                    quantity=item_dict["quantity"],
                    unit_price=item_dict["unit_price"],
                    amount=item_dict["quantity"] * item_dict["unit_price"],
                )
                db.add(li)
            await db.flush()

        # Recalculate totals
        result = await db.execute(
            select(ProposalLineItem).where(ProposalLineItem.proposal_id == proposal.id)
        )
        items = list(result.scalars().all())
        subtotal = sum(i.amount for i in items)
        taxable = max(0.0, float(subtotal) - float(proposal.discount))
        tax_amount = taxable * (float(proposal.tax_rate) / 100.0)
        proposal.subtotal = float(subtotal)
        proposal.tax_amount = float(tax_amount)
        proposal.total_amount = float(taxable + tax_amount)

        await db.commit()
        return await cls.get_proposal(db, company_id, proposal_id)

    # Invoices
    @classmethod
    async def create_invoice(cls, db: AsyncSession, company_id: str, data: InvoiceCreate) -> Invoice:
        subtotal = sum(item.quantity * item.unit_price for item in data.line_items)
        taxable = max(0.0, float(subtotal) - float(data.discount))
        tax_amount = taxable * (float(data.tax_rate) / 100.0)
        total_amount = taxable + tax_amount

        invoice = Invoice(
            company_id=company_id,
            client_id=data.client_id,
            project_id=data.project_id,
            proposal_id=data.proposal_id,
            invoice_number=data.invoice_number,
            status=InvoiceStatus.DRAFT,
            issue_date=data.issue_date,
            due_date=data.due_date,
            currency=data.currency,
            subtotal=subtotal,
            discount=data.discount,
            tax_rate=data.tax_rate,
            tax_amount=tax_amount,
            total_amount=total_amount,
            paid_amount=0.0,
            notes=data.notes,
        )
        db.add(invoice)
        await db.flush()

        for item in data.line_items:
            db.add(
                InvoiceLineItem(
                    invoice_id=invoice.id,
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    amount=item.quantity * item.unit_price,
                )
            )

        await db.commit()
        return await cls.get_invoice(db, company_id, invoice.id)

    @classmethod
    async def get_invoice(cls, db: AsyncSession, company_id: str, invoice_id: str) -> Optional[Invoice]:
        result = await db.execute(
            select(Invoice)
            .where(and_(Invoice.id == invoice_id, Invoice.company_id == company_id))
            .options(selectinload(Invoice.line_items))
        )
        return result.scalar_one_or_none()

    @classmethod
    async def list_invoices(cls, db: AsyncSession, company_id: str) -> List[Invoice]:
        result = await db.execute(
            select(Invoice)
            .where(Invoice.company_id == company_id)
            .options(selectinload(Invoice.line_items))
            .order_by(desc(Invoice.created_at))
        )
        return list(result.scalars().all())

    @classmethod
    async def record_payment(cls, db: AsyncSession, company_id: str, invoice_id: str, amount: float) -> Optional[Invoice]:
        invoice = await cls.get_invoice(db, company_id, invoice_id)
        if not invoice:
            return None

        invoice.paid_amount = float(invoice.paid_amount) + float(amount)
        if invoice.paid_amount >= invoice.total_amount:
            invoice.status = InvoiceStatus.PAID
        elif invoice.paid_amount > 0:
            invoice.status = InvoiceStatus.PARTIALLY_PAID

        await db.commit()
        await db.refresh(invoice)
        return invoice

    @classmethod
    async def update_invoice(cls, db: AsyncSession, company_id: str, invoice_id: str, data: InvoiceUpdate) -> Optional[Invoice]:
        invoice = await cls.get_invoice(db, company_id, invoice_id)
        if not invoice:
            return None

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(invoice, field, value)

        await db.commit()
        await db.refresh(invoice)
        return invoice

    # Portfolio Case Studies
    @classmethod
    async def create_case_study(cls, db: AsyncSession, company_id: str, data: PortfolioCaseStudyCreate) -> PortfolioCaseStudy:
        case_study = PortfolioCaseStudy(
            company_id=company_id,
            project_id=data.project_id,
            title=data.title,
            headline=data.headline,
            client_display_name=data.client_display_name,
            challenge=data.challenge,
            solution=data.solution,
            results_and_impact=data.results_and_impact,
            metrics=data.metrics,
            is_public_approved=data.is_public_approved,
            technologies=data.technologies,
        )
        db.add(case_study)
        await db.commit()
        await db.refresh(case_study)
        return case_study

    @classmethod
    async def list_case_studies(cls, db: AsyncSession, company_id: str, public_only: bool = False) -> List[PortfolioCaseStudy]:
        query = select(PortfolioCaseStudy).where(PortfolioCaseStudy.company_id == company_id)
        if public_only:
            query = query.where(PortfolioCaseStudy.is_public_approved == True)
        result = await db.execute(query.order_by(desc(PortfolioCaseStudy.created_at)))
        return list(result.scalars().all())

    # AI Social Copy Generator
    @classmethod
    async def generate_social_copy(cls, db: AsyncSession, company_id: str, user_id: str, request: GenerateSocialCopyRequest) -> SocialPost:
        # Fetch project details if provided
        context_text = ""
        if request.project_id:
            proj = await db.execute(
                select(Project).where(and_(Project.id == request.project_id, Project.company_id == company_id))
            )
            p = proj.scalar_one_or_none()
            if p:
                context_text += f"Project: {p.title}. Description: {p.description or ''}. Summary: {p.completion_summary or ''}."


        if request.case_study_id:
            cs = await db.execute(
                select(PortfolioCaseStudy).where(and_(PortfolioCaseStudy.id == request.case_study_id, PortfolioCaseStudy.company_id == company_id))
            )
            c = cs.scalar_one_or_none()
            if c:
                context_text += f" Case Study: {c.title}. Headline: {c.headline}. Impact: {c.results_and_impact}."

        if not context_text:
            context_text = f"Key takeaway: {request.key_takeaway or 'Delivering high quality digital transformation services'}"

        prompt = (
            f"Generate a professional, engaging {request.platform.value} marketing post based strictly on this context: {context_text}.\n"
            f"Tone: {request.tone}.\n"
            f"Return JSON with: content (the post body), hashtags (list of 3-5 tags), call_to_action (string)."
        )

        ai_provider = AIFactory.get_provider()
        res = await ai_provider.generate_text(prompt=prompt)

        # Parse output or fallback
        try:
            parsed = json.loads(res.content)
            content = parsed.get("content", res.content)
            hashtags = parsed.get("hashtags", ["#BizBook", "#Enterprise", "#Innovation"])
            cta = parsed.get("call_to_action", "Contact us to learn more.")
        except Exception:
            content = res.content
            hashtags = ["#BizBook", "#Enterprise", "#B2B"]
            cta = "Connect with our team today."


        # Log AI Usage
        usage_log = AIUsageLog(
            company_id=company_id,
            user_id=user_id,
            provider="mock" if "Mock" in ai_provider.__class__.__name__ else "openai",
            model="mock-gpt-4" if "Mock" in ai_provider.__class__.__name__ else "gpt-4o",
            operation="generate_social_copy",
            prompt_tokens=res.prompt_tokens,
            completion_tokens=res.completion_tokens,
            total_tokens=res.total_tokens,
            estimated_cost_usd=res.estimated_cost_usd,
            latency_ms=res.latency_ms,

        )
        db.add(usage_log)

        post = SocialPost(
            company_id=company_id,
            project_id=request.project_id,
            platform=request.platform,
            content=content,
            hashtags=hashtags,
            call_to_action=cta,
            is_published=False,
        )
        db.add(post)
        await db.commit()
        await db.refresh(post)
        return post

    # Executive Dashboard Metrics
    @classmethod
    async def get_dashboard_metrics(cls, db: AsyncSession, company_id: str) -> DashboardMetrics:
        # Clients count
        clients_res = await db.execute(
            select(func.count(Client.id)).where(Client.company_id == company_id)
        )
        total_clients = clients_res.scalar() or 0

        # Projects active vs completed
        active_proj_res = await db.execute(
            select(func.count(Project.id)).where(
                and_(Project.company_id == company_id, Project.status == ProjectStatusEnum.IN_PROGRESS)
            )
        )
        active_projects = active_proj_res.scalar() or 0

        comp_proj_res = await db.execute(
            select(func.count(Project.id)).where(
                and_(Project.company_id == company_id, Project.status == ProjectStatusEnum.COMPLETED)
            )
        )
        completed_projects = comp_proj_res.scalar() or 0

        # Proposals: open count and total value
        open_props_res = await db.execute(
            select(func.count(Proposal.id), func.coalesce(func.sum(Proposal.total_amount), 0.0)).where(
                and_(
                    Proposal.company_id == company_id,
                    Proposal.status.in_([ProposalStatus.DRAFT, ProposalStatus.SENT])
                )
            )
        )
        open_props_row = open_props_res.one()
        open_proposals_count = open_props_row[0] or 0
        open_proposals_value = float(open_props_row[1] or 0.0)

        # Invoices: total receivable (total_amount - paid_amount for non-cancelled and non-paid), total paid, overdue count
        inv_res = await db.execute(
            select(Invoice).where(
                and_(Invoice.company_id == company_id, Invoice.status != InvoiceStatus.CANCELLED)
            )
        )
        invoices = list(inv_res.scalars().all())
        today = date.today()
        
        invoices_total_receivable = sum(
            max(0.0, float(inv.total_amount) - float(inv.paid_amount))
            for inv in invoices if inv.status != InvoiceStatus.PAID
        )
        invoices_total_paid = sum(float(inv.paid_amount) for inv in invoices)
        invoices_overdue_count = sum(
            1 for inv in invoices
            if inv.status in [InvoiceStatus.SENT, InvoiceStatus.PARTIALLY_PAID, InvoiceStatus.OVERDUE]
            and inv.due_date < today
        )

        # Active Tenders count
        tenders_res = await db.execute(
            select(func.count(Tender.id)).where(
                and_(
                    Tender.company_id == company_id,
                    Tender.status.in_([
                        TenderStatus.ANALYZING,
                        TenderStatus.MATCHING,
                        TenderStatus.DRAFTING,
                        TenderStatus.READY,
                    ])
                )
            )
        )
        active_tenders_count = tenders_res.scalar() or 0

        # Expiring documents count (within 30 days or expired)
        thirty_days_ahead = datetime.utcnow() + timedelta(days=30)
        exp_docs_res = await db.execute(
            select(func.count(Document.id)).where(
                and_(
                    Document.company_id == company_id,
                    Document.expiry_date.isnot(None),
                    Document.expiry_date <= thirty_days_ahead,
                )
            )
        )
        expiring_documents_count = exp_docs_res.scalar() or 0

        # Recent activities
        audit_res = await db.execute(
            select(AuditLog)
            .where(AuditLog.company_id == company_id)
            .order_by(desc(AuditLog.created_at))
            .limit(10)
        )
        audit_logs = list(audit_res.scalars().all())
        recent_activity = [
            {
                "id": a.id,
                "action": a.action,
                "resource_type": a.resource_type,
                "resource_id": a.resource_id,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in audit_logs
        ]

        return DashboardMetrics(
            total_clients=total_clients,
            active_projects=active_projects,
            completed_projects=completed_projects,
            open_proposals_count=open_proposals_count,
            open_proposals_value=open_proposals_value,
            invoices_total_receivable=invoices_total_receivable,
            invoices_total_paid=invoices_total_paid,
            invoices_overdue_count=invoices_overdue_count,
            active_tenders_count=active_tenders_count,
            expiring_documents_count=expiring_documents_count,
            recent_activity=recent_activity,
        )
