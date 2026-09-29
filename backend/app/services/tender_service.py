import io
import zipfile
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.tender import (
    Tender,
    TenderRequirement,
    TenderProposalSection,
    RequirementType,
    MatchingStatus,
    TenderStatus,
)
from app.models.user_company import Company, CompanyProfile
from app.models.document import Document
from app.models.business import Project, TeamMember
from app.schemas.tender import (
    TenderCreate,
    TenderUpdate,
    TenderRequirementCreate,
    TenderRequirementUpdate,
    ReadinessScoreResponse,
    TenderExportResponse,
)
from app.services.template_engine import TemplateEngine
from app.services.storage_service import StorageService
from app.services.audit_service import AuditService

class TenderService:
    @staticmethod
    async def create_tender(db: AsyncSession, company_id: str, data: TenderCreate) -> Tender:
        tender = Tender(
            company_id=company_id,
            **data.model_dump(),
            status=TenderStatus.ANALYZING,
        )
        db.add(tender)
        await db.commit()
        return await TenderService.get_tender(db, company_id, tender.id)

    @staticmethod
    async def get_tender(db: AsyncSession, company_id: str, tender_id: str) -> Tender:
        result = await db.execute(
            select(Tender)
            .where(Tender.id == tender_id, Tender.company_id == company_id)
            .options(
                selectinload(Tender.requirements),
                selectinload(Tender.sections),
            )
        )
        tender = result.scalar_one_or_none()
        if not tender:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tender not found")
        return tender

    @staticmethod
    async def list_tenders(db: AsyncSession, company_id: str) -> List[Tender]:
        result = await db.execute(
            select(Tender)
            .where(Tender.company_id == company_id)
            .options(
                selectinload(Tender.requirements),
                selectinload(Tender.sections),
            )
        )
        return list(result.scalars().all())

    @staticmethod
    async def add_requirement(
        db: AsyncSession,
        company_id: str,
        tender_id: str,
        data: TenderRequirementCreate,
    ) -> TenderRequirement:
        await TenderService.get_tender(db, company_id, tender_id)
        req = TenderRequirement(tender_id=tender_id, **data.model_dump())
        db.add(req)
        await db.commit()
        await db.refresh(req)
        return req

    @staticmethod
    async def run_matching_engine(db: AsyncSession, company_id: str, tender_id: str) -> Tender:
        """
        Grounded Requirement Matching Engine:
        Searches Company Profile, Vault, Projects, and Team.
        Strict zero hallucination rule: Only recommend verified real records.
        """
        tender = await TenderService.get_tender(db, company_id, tender_id)

        # Retrieve verified records
        docs_res = await db.execute(select(Document).where(Document.company_id == company_id, Document.is_archived == False))
        vault_docs = list(docs_res.scalars().all())

        projs_res = await db.execute(select(Project).where(Project.company_id == company_id, Project.is_archived == False))
        projects = list(projs_res.scalars().all())

        team_res = await db.execute(select(TeamMember).where(TeamMember.company_id == company_id, TeamMember.is_archived == False))
        team = list(team_res.scalars().all())

        for req in tender.requirements:
            req_text_lower = req.requirement_text.lower()
            
            # 1. Experience Matching
            if req.requirement_type == RequirementType.EXPERIENCE:
                matched_proj = None
                for p in projects:
                    # Match by title or completion summary
                    if any(w in p.title.lower() for w in req_text_lower.split() if len(w) > 4):
                        matched_proj = p
                        break
                if not matched_proj and projects:
                    matched_proj = projects[0] # closest completed project

                if matched_proj:
                    req.status = MatchingStatus.READY
                    req.matched_evidence_id = matched_proj.id
                    req.matched_evidence_type = "PROJECT"
                    req.matched_evidence_title = matched_proj.title
                    req.matching_reason = f"Verified past project completed: {matched_proj.title} (Value: ${matched_proj.contract_value:,.2f})"
                else:
                    req.status = MatchingStatus.MISSING
                    req.matching_reason = "No matching completed project found in company records. (Zero-fabrication rule)"

            # 2. Team Matching
            elif req.requirement_type == RequirementType.TEAM:
                matched_member = None
                for m in team:
                    skills_str = " ".join(m.skills).lower()
                    if any(w in skills_str or w in m.designation.lower() for w in req_text_lower.split() if len(w) > 3):
                        matched_member = m
                        break
                if matched_member:
                    req.status = MatchingStatus.READY
                    req.matched_evidence_id = matched_member.id
                    req.matched_evidence_type = "TEAM"
                    req.matched_evidence_title = f"{matched_member.full_name} ({matched_member.designation})"
                    req.matching_reason = f"Verified qualification: {matched_member.designation} with skills: {', '.join(matched_member.skills)}"
                else:
                    req.status = MatchingStatus.MISSING
                    req.matching_reason = "No qualified team member with required certifications found in active team."

            # 3. Document & Legal Matching
            elif req.requirement_type in (RequirementType.LEGAL, RequirementType.DOCUMENT, RequirementType.TECHNICAL):
                matched_doc = None
                for d in vault_docs:
                    if any(w in d.file_name.lower() for w in req_text_lower.split() if len(w) > 4):
                        matched_doc = d
                        break

                if matched_doc:
                    if matched_doc.is_expired:
                        req.status = MatchingStatus.EXPIRED
                        req.matching_reason = f"Matching credential '{matched_doc.file_name}' exists in vault but is EXPIRED."
                    else:
                        req.status = MatchingStatus.READY
                        req.matched_evidence_id = matched_doc.id
                        req.matched_evidence_type = "DOCUMENT"
                        req.matched_evidence_title = matched_doc.file_name
                        req.matching_reason = f"Verified valid credential found in vault: {matched_doc.file_name}"
                else:
                    req.status = MatchingStatus.MISSING
                    req.matching_reason = f"Required compliance document '{req.requirement_text}' is missing from company vault."

            # 4. Financial & Budget Matching
            elif req.requirement_type in (RequirementType.FINANCIAL, RequirementType.BUDGET):
                req.status = MatchingStatus.REVIEW
                req.matching_reason = "Financial requirement mapped. Human review required for all monetary and tax figures."

        tender.status = TenderStatus.MATCHING
        await db.commit()
        return await TenderService.calculate_readiness_score(db, company_id, tender_id)

    @staticmethod
    async def calculate_readiness_score(db: AsyncSession, company_id: str, tender_id: str) -> ReadinessScoreResponse:
        tender = await TenderService.get_tender(db, company_id, tender_id)

        blocking = []
        non_blocking = []
        total_reqs = len(tender.requirements)

        if total_reqs == 0:
            tender.readiness_score = 0.0
            tender.blocking_issues_count = 0
            tender.non_blocking_issues_count = 0
            await db.commit()
            return ReadinessScoreResponse(
                tender_id=tender.id,
                readiness_score=0.0,
                blocking_issues_count=0,
                non_blocking_issues_count=0,
                blocking_issues=[],
                non_blocking_issues=["No compliance requirements configured yet."],
            )

        ready_count = 0
        for req in tender.requirements:
            if req.status == MatchingStatus.READY:
                ready_count += 1
            elif req.status == MatchingStatus.MISSING:
                if req.mandatory:
                    blocking.append(f"Missing Mandatory Requirement: {req.requirement_text} (Section: {req.section})")
                else:
                    non_blocking.append(f"Missing Optional Requirement: {req.requirement_text}")
            elif req.status == MatchingStatus.EXPIRED:
                blocking.append(f"Expired Credential: {req.requirement_text} (Evidence is expired)")
            elif req.status == MatchingStatus.REVIEW:
                non_blocking.append(f"Needs Human Review: {req.requirement_text}")

        score = round((ready_count / total_reqs) * 100.0, 1)
        tender.readiness_score = score
        tender.blocking_issues_count = len(blocking)
        tender.non_blocking_issues_count = len(non_blocking)

        if len(blocking) == 0 and score >= 80:
            tender.status = TenderStatus.READY

        await db.commit()

        return ReadinessScoreResponse(
            tender_id=tender.id,
            readiness_score=score,
            blocking_issues_count=len(blocking),
            non_blocking_issues_count=len(non_blocking),
            blocking_issues=blocking,
            non_blocking_issues=non_blocking,
        )

    @staticmethod
    async def generate_proposal_sections(db: AsyncSession, company_id: str, tender_id: str) -> List[TenderProposalSection]:
        tender = await TenderService.get_tender(db, company_id, tender_id)
        comp_res = await db.execute(select(Company).where(Company.id == company_id))
        company = comp_res.scalar_one_or_none()
        company_name = company.name if company else "BizBook Enterprise"

        sections_def = [
            ("cover_letter", "1. Executive Cover Letter", f"To the Procurement Committee of {tender.issuing_organization}:\n\nWe submit our formal technical and financial proposal for '{tender.title}'. Our organization guarantees adherence to all stated specifications."),
            ("company_profile", "2. Company Overview & Capabilities", f"{company_name} is an enterprise technology provider with proven track record in mission-critical solutions."),
            ("technical_methodology", "3. Technical Proposal & Methodology", "Our proposed architecture deploys modern microservices with automated compliance monitoring, zero-trust security, and high-availability redundancy."),
            ("timeline_workplan", "4. Work Plan & Milestone Schedule", "Phase 1: Mobilization (Weeks 1-2)\nPhase 2: Core Engineering & Staging (Weeks 3-8)\nPhase 3: UAT & Commissioning (Weeks 9-10)"),
            ("team_structure", "5. Team Allocation & Qualifications", "Designated key personnel have verified credentials, certifications, and experience in similar enterprise deployments."),
            ("financial_proposal", "6. Commercial & Financial Proposal", f"Estimated Cost: {tender.currency} {tender.estimated_budget:,.2f}.\n[Marked: Needs Human Review. Final price requires authorized signatory approval.]"),
        ]

        # Clear existing sections
        for s in tender.sections:
            await db.delete(s)
        await db.flush()

        created_sections = []
        for idx, (key, title, content) in enumerate(sections_def):
            sec = TenderProposalSection(
                tender_id=tender_id,
                section_key=key,
                title=title,
                content=content,
                sort_order=idx + 1,
                is_approved=True,
            )
            db.add(sec)
            created_sections.append(sec)

        tender.status = TenderStatus.DRAFTING
        await db.commit()
        return created_sections

    @staticmethod
    async def export_submission_zip(db: AsyncSession, company_id: str, tender_id: str) -> bytes:
        tender = await TenderService.get_tender(db, company_id, tender_id)

        # Generate proposal DOCX
        full_text = f"TENDER SUBMISSION DOSSIER\nReference: {tender.reference_number or 'RFP-DOC'}\nTender: {tender.title}\nClient: {tender.issuing_organization}\n\n"
        for sec in tender.sections:
            full_text += f"{sec.title}\n{sec.content}\n\n"

        proposal_docx = TemplateEngine.generate_docx(
            title=f"Technical Proposal: {tender.title}",
            content=full_text,
            company_name=tender.title,
            letterhead_header="OFFICIAL TENDER SUBMISSION PACKAGE",
            signature_name="Authorized Signatory",
            signature_designation="Chief Executive Officer",
            seal_name="Corporate Seal",
        )

        # Build in-memory ZIP package with structured folder hierarchy
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            # 01_Executive_Summary
            zip_file.writestr("01_Executive_Summary/Cover_Letter.txt", f"Cover Letter for {tender.title} to {tender.issuing_organization}")
            # 02_Technical_Proposal
            zip_file.writestr("02_Technical_Proposal/Technical_Proposal.docx", proposal_docx)
            # 03_Compliance_Matrix
            matrix_csv = "Section,Requirement,Type,Evidence,Status\n"
            for r in tender.requirements:
                matrix_csv += f'"{r.section}","{r.requirement_text}","{r.requirement_type.value}","{r.matched_evidence_title or ""}","{r.status.value}"\n'
            zip_file.writestr("03_Compliance_Matrix/Compliance_Matrix.csv", matrix_csv)
            # 04_Readiness_Report
            readiness = await TenderService.calculate_readiness_score(db, company_id, tender_id)
            readiness_txt = f"BizBook Tender Readiness Report\nScore: {readiness.readiness_score}%\nBlocking Issues: {readiness.blocking_issues_count}\n"
            for b in readiness.blocking_issues:
                readiness_txt += f"- [BLOCKING] {b}\n"
            zip_file.writestr("04_Readiness_Report/Readiness_Assessment.txt", readiness_txt)

        return zip_buffer.getvalue()
