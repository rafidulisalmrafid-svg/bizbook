from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.api.deps import require_permission, CurrentTenant
from app.models.user_company import PermissionEnum, Company, CompanyProfile
from app.models.document import DocumentTemplate
from app.schemas.document import (
    DocumentTemplateCreate,
    DocumentTemplateUpdate,
    DocumentTemplateRead,
    TemplateRenderRequest,
    TemplateRenderResponse,
)
from app.services.template_engine import TemplateEngine

router = APIRouter()

@router.get("", response_model=List[DocumentTemplateRead])
async def list_templates(
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.DOCUMENT_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    query = select(DocumentTemplate).where(
        DocumentTemplate.company_id == tenant.company_id,
        DocumentTemplate.is_archived == False,
    )
    result = await db.execute(query)
    return list(result.scalars().all())

@router.post("", response_model=DocumentTemplateRead, status_code=status.HTTP_201_CREATED)
async def create_template(
    data: DocumentTemplateCreate,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.DOCUMENT_UPLOAD)),
    db: AsyncSession = Depends(get_db),
):
    template = DocumentTemplate(company_id=tenant.company_id, **data.model_dump())
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template

@router.post("/{template_id}/render", response_model=TemplateRenderResponse)
async def render_template(
    template_id: str,
    data: TemplateRenderRequest,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.DOCUMENT_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DocumentTemplate).where(
            DocumentTemplate.id == template_id,
            DocumentTemplate.company_id == tenant.company_id,
        )
    )
    tmpl = result.scalar_one_or_none()
    if not tmpl:
        raise HTTPException(status_code=404, detail="Template not found")

    # Fetch company variables for defaults
    comp_res = await db.execute(select(Company).where(Company.id == tenant.company_id))
    company = comp_res.scalar_one_or_none()

    merged_vars = {
        "company.name": company.name if company else "BizBook Enterprise",
        "company.email": tenant.user.email,
        "company.address": "Headquarters, Tech Park",
        "company.phone": "+1 (555) 019-2831",
        "ceo.name": tenant.user.full_name,
        "ceo.designation": "Managing Director",
        "client.name": "Valued Enterprise Client",
        "project.name": "Enterprise Digital Transformation",
        "project.value": "$250,000",
    }
    merged_vars.update(data.variables)

    rendered = TemplateEngine.render_text(tmpl.content, merged_vars)

    return TemplateRenderResponse(
        template_id=tmpl.id,
        rendered_content=rendered,
        variables_applied=merged_vars,
    )

@router.post("/{template_id}/export-docx")
async def export_template_docx(
    template_id: str,
    tenant: CurrentTenant = Depends(require_permission(PermissionEnum.DOCUMENT_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DocumentTemplate).where(
            DocumentTemplate.id == template_id,
            DocumentTemplate.company_id == tenant.company_id,
        )
    )
    tmpl = result.scalar_one_or_none()
    if not tmpl:
        raise HTTPException(status_code=404, detail="Template not found")

    comp_res = await db.execute(select(Company).where(Company.id == tenant.company_id))
    company = comp_res.scalar_one_or_none()

    docx_bytes = TemplateEngine.generate_docx(
        title=tmpl.title,
        content=tmpl.content,
        company_name=company.name if company else "BizBook Enterprise",
        signature_name=tenant.user.full_name,
        signature_designation="Authorized Signatory",
        seal_name="Official Corporate Seal",
    )

    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={tmpl.title.replace(' ', '_')}.docx"}
    )
