import re
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.user_company import User, Company, Membership, RoleEnum, CompanyProfile, CompanyBrand
from app.schemas.auth import UserRegister, UserLogin, TokenResponse
from app.core.security import get_password_hash, verify_password, create_access_token
from app.services.audit_service import AuditService

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text or "company"

class AuthService:
    @staticmethod
    async def register(db: AsyncSession, data: UserRegister, ip_address: Optional[str] = None) -> TokenResponse:
        # Check existing user
        result = await db.execute(select(User).where(User.email == data.email.lower()))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists."
            )

        # Create user
        user = User(
            email=data.email.lower(),
            hashed_password=get_password_hash(data.password),
            full_name=data.full_name,
            is_active=True,
            is_verified=True,
        )
        db.add(user)
        await db.flush()

        # Create company
        base_slug = slugify(data.company_name)
        slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
        company = Company(
            name=data.company_name,
            slug=slug,
            is_active=True,
        )
        db.add(company)
        await db.flush()

        # Create Owner membership
        membership = Membership(
            company_id=company.id,
            user_id=user.id,
            role=RoleEnum.OWNER,
            is_active=True,
        )
        db.add(membership)

        # Create initial profile and brand
        profile = CompanyProfile(company_id=company.id)
        brand = CompanyBrand(company_id=company.id)
        db.add(profile)
        db.add(brand)

        await db.commit()
        await db.refresh(user)
        await db.refresh(company)

        # Audit log
        await AuditService.log(
            db=db,
            company_id=company.id,
            user_id=user.id,
            action="auth.register",
            resource_type="company",
            resource_id=company.id,
            details={"company_name": company.name, "email": user.email},
            ip_address=ip_address,
        )

        # Token
        access_token = create_access_token({
            "sub": user.id,
            "company_id": company.id,
            "role": RoleEnum.OWNER.value,
            "email": user.email,
        })

        return TokenResponse(
            access_token=access_token,
            user_id=user.id,
            company_id=company.id,
            role=RoleEnum.OWNER.value,
            full_name=user.full_name,
            email=user.email,
        )

    @staticmethod
    async def login(db: AsyncSession, data: UserLogin, ip_address: Optional[str] = None) -> TokenResponse:
        result = await db.execute(select(User).where(User.email == data.email.lower()))
        user = result.scalar_one_or_none()
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password."
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account has been deactivated."
            )

        # Find primary or active membership
        mem_result = await db.execute(
            select(Membership).where(
                Membership.user_id == user.id,
                Membership.is_active == True,
            )
        )
        membership = mem_result.scalars().first()
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No active company membership found."
            )

        # Audit log
        await AuditService.log(
            db=db,
            company_id=membership.company_id,
            user_id=user.id,
            action="auth.login",
            resource_type="user",
            resource_id=user.id,
            ip_address=ip_address,
        )

        access_token = create_access_token({
            "sub": user.id,
            "company_id": membership.company_id,
            "role": membership.role.value,
            "email": user.email,
        })

        return TokenResponse(
            access_token=access_token,
            user_id=user.id,
            company_id=membership.company_id,
            role=membership.role.value,
            full_name=user.full_name,
            email=user.email,
        )
