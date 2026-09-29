from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.business import (
    TeamMember,
    TeamMemberExperience,
    TeamMemberCertification,
    TeamMemberCV,
)
from app.schemas.team import (
    TeamMemberCreate,
    TeamMemberUpdate,
    TeamExperienceCreate,
    TeamCertificationCreate,
)

class TeamService:
    @staticmethod
    async def list_members(db: AsyncSession, company_id: str, include_archived: bool = False) -> List[TeamMember]:
        query = (
            select(TeamMember)
            .where(TeamMember.company_id == company_id)
            .options(
                selectinload(TeamMember.experiences),
                selectinload(TeamMember.certifications),
            )
        )
        if not include_archived:
            query = query.where(TeamMember.is_archived == False)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_member(db: AsyncSession, company_id: str, member_id: str) -> TeamMember:
        result = await db.execute(
            select(TeamMember)
            .where(TeamMember.id == member_id, TeamMember.company_id == company_id)
            .options(
                selectinload(TeamMember.experiences),
                selectinload(TeamMember.certifications),
            )
        )
        member = result.scalar_one_or_none()
        if not member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team member not found")
        return member

    @staticmethod
    async def create_member(db: AsyncSession, company_id: str, data: TeamMemberCreate) -> TeamMember:
        member = TeamMember(company_id=company_id, **data.model_dump())
        db.add(member)
        await db.commit()
        await db.refresh(member)
        return await TeamService.get_member(db, company_id, member.id)

    @staticmethod
    async def update_member(db: AsyncSession, company_id: str, member_id: str, data: TeamMemberUpdate) -> TeamMember:
        member = await TeamService.get_member(db, company_id, member_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(member, key, value)
        await db.commit()
        await db.refresh(member)
        return member

    @staticmethod
    async def archive_member(db: AsyncSession, company_id: str, member_id: str) -> TeamMember:
        member = await TeamService.get_member(db, company_id, member_id)
        member.is_archived = True
        member.is_active = False
        await db.commit()
        await db.refresh(member)
        return member

    @staticmethod
    async def add_experience(db: AsyncSession, company_id: str, member_id: str, data: TeamExperienceCreate) -> TeamMemberExperience:
        # Verify member belongs to company
        await TeamService.get_member(db, company_id, member_id)
        exp = TeamMemberExperience(team_member_id=member_id, **data.model_dump())
        db.add(exp)
        await db.commit()
        await db.refresh(exp)
        return exp

    @staticmethod
    async def add_certification(db: AsyncSession, company_id: str, member_id: str, data: TeamCertificationCreate) -> TeamMemberCertification:
        # Verify member belongs to company
        await TeamService.get_member(db, company_id, member_id)
        cert = TeamMemberCertification(team_member_id=member_id, **data.model_dump())
        db.add(cert)
        await db.commit()
        await db.refresh(cert)
        return cert
