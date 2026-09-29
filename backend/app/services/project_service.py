from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.business import (
    Project,
    ProjectTeamMember,
    ProjectDocument,
    ProjectStatusEnum,
    Client,
)
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectTeamMemberCreate,
    ProjectDocumentCreate,
    PortfolioDraftResponse,
)

class ProjectService:
    @staticmethod
    async def list_projects(db: AsyncSession, company_id: str, include_archived: bool = False) -> List[Project]:
        query = (
            select(Project)
            .where(Project.company_id == company_id)
            .options(
                selectinload(Project.team_members),
                selectinload(Project.documents),
                selectinload(Project.client),
            )
        )
        if not include_archived:
            query = query.where(Project.is_archived == False)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_project(db: AsyncSession, company_id: str, project_id: str) -> Project:
        result = await db.execute(
            select(Project)
            .where(Project.id == project_id, Project.company_id == company_id)
            .options(
                selectinload(Project.team_members),
                selectinload(Project.documents),
                selectinload(Project.client),
            )
        )
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        return project

    @staticmethod
    async def create_project(db: AsyncSession, company_id: str, data: ProjectCreate) -> Project:
        project = Project(company_id=company_id, **data.model_dump())
        db.add(project)
        await db.commit()
        await db.refresh(project)
        return await ProjectService.get_project(db, company_id, project.id)

    @staticmethod
    async def update_project(db: AsyncSession, company_id: str, project_id: str, data: ProjectUpdate) -> Project:
        project = await ProjectService.get_project(db, company_id, project_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(project, key, value)
        await db.commit()
        await db.refresh(project)
        return project

    @staticmethod
    async def archive_project(db: AsyncSession, company_id: str, project_id: str) -> Project:
        project = await ProjectService.get_project(db, company_id, project_id)
        project.is_archived = True
        await db.commit()
        await db.refresh(project)
        return project

    @staticmethod
    async def assign_team_member(db: AsyncSession, company_id: str, project_id: str, data: ProjectTeamMemberCreate) -> ProjectTeamMember:
        await ProjectService.get_project(db, company_id, project_id)
        ptm = ProjectTeamMember(project_id=project_id, **data.model_dump())
        db.add(ptm)
        await db.commit()
        await db.refresh(ptm)
        return ptm

    @staticmethod
    async def add_document(db: AsyncSession, company_id: str, project_id: str, data: ProjectDocumentCreate) -> ProjectDocument:
        await ProjectService.get_project(db, company_id, project_id)
        doc = ProjectDocument(project_id=project_id, **data.model_dump())
        db.add(doc)
        await db.commit()
        await db.refresh(doc)
        return doc

    @staticmethod
    async def create_portfolio_draft(db: AsyncSession, company_id: str, project_id: str) -> PortfolioDraftResponse:
        project = await ProjectService.get_project(db, company_id, project_id)
        project.portfolio_draft_created = True
        await db.commit()

        client_name = project.client.name if project.client else "Confidential Enterprise Client"
        summary = project.completion_summary or project.description or "Successfully delivered enterprise solution."
        
        return PortfolioDraftResponse(
            project_id=project.id,
            title=f"Case Study: {project.title}",
            client_name=client_name,
            challenge=f"Client required execution of {project.title} within standard timeline and compliance guidelines.",
            solution=f"Deployed dedicated team utilizing enterprise architecture and best practices. {summary}",
            results_and_impact=f"Successfully fulfilled contract valued at {project.currency} {project.contract_value:,.2f} with all deliverables verified.",
            technologies_used=["Enterprise Architecture", "Cloud Delivery", "Quality Assurance"],
            evidence_count=len(project.documents),
            is_ready_for_review=True,
        )
