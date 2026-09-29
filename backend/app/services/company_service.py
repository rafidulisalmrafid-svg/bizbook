from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.user_company import (
    Company,
    CompanyProfile,
    CompanyBrand,
    CompanyContact,
    CompanyLetterhead,
    CompanySignature,
    CompanySeal,
    PartnerLogo,
)
from app.schemas.company import (
    CompanyProfileUpdate,
    CompanyBrandUpdate,
    CompanyContactCreate,
    CompanyLetterheadCreate,
    CompanySignatureCreate,
    CompanySealCreate,
    PartnerLogoCreate,
)

class CompanyService:
    @staticmethod
    async def get_company(db: AsyncSession, company_id: str) -> Company:
        result = await db.execute(select(Company).where(Company.id == company_id))
        company = result.scalar_one_or_none()
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        return company

    @staticmethod
    async def get_profile(db: AsyncSession, company_id: str) -> CompanyProfile:
        result = await db.execute(select(CompanyProfile).where(CompanyProfile.company_id == company_id))
        profile = result.scalar_one_or_none()
        if not profile:
            profile = CompanyProfile(company_id=company_id)
            db.add(profile)
            await db.commit()
            await db.refresh(profile)
        return profile

    @staticmethod
    async def update_profile(db: AsyncSession, company_id: str, data: CompanyProfileUpdate) -> CompanyProfile:
        profile = await CompanyService.get_profile(db, company_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(profile, key, value)
        await db.commit()
        await db.refresh(profile)
        return profile

    @staticmethod
    async def get_brand(db: AsyncSession, company_id: str) -> CompanyBrand:
        result = await db.execute(select(CompanyBrand).where(CompanyBrand.company_id == company_id))
        brand = result.scalar_one_or_none()
        if not brand:
            brand = CompanyBrand(company_id=company_id)
            db.add(brand)
            await db.commit()
            await db.refresh(brand)
        return brand

    @staticmethod
    async def update_brand(db: AsyncSession, company_id: str, data: CompanyBrandUpdate) -> CompanyBrand:
        brand = await CompanyService.get_brand(db, company_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(brand, key, value)
        await db.commit()
        await db.refresh(brand)
        return brand

    # Contacts
    @staticmethod
    async def list_contacts(db: AsyncSession, company_id: str) -> List[CompanyContact]:
        result = await db.execute(select(CompanyContact).where(CompanyContact.company_id == company_id))
        return list(result.scalars().all())

    @staticmethod
    async def create_contact(db: AsyncSession, company_id: str, data: CompanyContactCreate) -> CompanyContact:
        contact = CompanyContact(company_id=company_id, **data.model_dump())
        db.add(contact)
        await db.commit()
        await db.refresh(contact)
        return contact

    @staticmethod
    async def delete_contact(db: AsyncSession, company_id: str, contact_id: str) -> None:
        result = await db.execute(
            select(CompanyContact).where(CompanyContact.id == contact_id, CompanyContact.company_id == company_id)
        )
        contact = result.scalar_one_or_none()
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        await db.delete(contact)
        await db.commit()

    # Letterhead
    @staticmethod
    async def list_letterheads(db: AsyncSession, company_id: str) -> List[CompanyLetterhead]:
        result = await db.execute(select(CompanyLetterhead).where(CompanyLetterhead.company_id == company_id))
        return list(result.scalars().all())

    @staticmethod
    async def create_letterhead(db: AsyncSession, company_id: str, data: CompanyLetterheadCreate) -> CompanyLetterhead:
        if data.is_default:
            # Unset existing defaults
            existing = await CompanyService.list_letterheads(db, company_id)
            for lh in existing:
                lh.is_default = False
        letterhead = CompanyLetterhead(company_id=company_id, **data.model_dump())
        db.add(letterhead)
        await db.commit()
        await db.refresh(letterhead)
        return letterhead

    # Signatures & Seals
    @staticmethod
    async def list_signatures(db: AsyncSession, company_id: str) -> List[CompanySignature]:
        result = await db.execute(select(CompanySignature).where(CompanySignature.company_id == company_id))
        return list(result.scalars().all())

    @staticmethod
    async def create_signature(db: AsyncSession, company_id: str, data: CompanySignatureCreate, user_id: Optional[str] = None) -> CompanySignature:
        sig = CompanySignature(company_id=company_id, user_id=user_id, **data.model_dump())
        db.add(sig)
        await db.commit()
        await db.refresh(sig)
        return sig

    @staticmethod
    async def list_seals(db: AsyncSession, company_id: str) -> List[CompanySeal]:
        result = await db.execute(select(CompanySeal).where(CompanySeal.company_id == company_id))
        return list(result.scalars().all())

    @staticmethod
    async def create_seal(db: AsyncSession, company_id: str, data: CompanySealCreate) -> CompanySeal:
        seal = CompanySeal(company_id=company_id, **data.model_dump())
        db.add(seal)
        await db.commit()
        await db.refresh(seal)
        return seal
