import enum
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text, Integer, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from app.models.base import TimestampMixin, generate_uuid

class RoleEnum(str, enum.Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    MEMBER = "MEMBER"
    VIEWER = "VIEWER"
    TENDER_MANAGER = "TENDER_MANAGER"

class PermissionEnum(str, enum.Enum):
    COMPANY_VIEW = "company.view"
    COMPANY_EDIT = "company.edit"
    TEAM_VIEW = "team.view"
    TEAM_EDIT = "team.edit"
    CLIENT_VIEW = "client.view"
    CLIENT_EDIT = "client.edit"
    PROJECT_VIEW = "project.view"
    PROJECT_EDIT = "project.edit"
    SERVICE_VIEW = "service.view"
    SERVICE_EDIT = "service.edit"
    DOCUMENT_VIEW = "document.view"
    DOCUMENT_UPLOAD = "document.upload"
    DOCUMENT_DELETE = "document.delete"
    TENDER_VIEW = "tender.view"
    TENDER_CREATE = "tender.create"
    TENDER_EDIT = "tender.edit"
    TENDER_APPROVE = "tender.approve"
    TENDER_EXPORT = "tender.export"
    INVOICE_VIEW = "invoice.view"
    INVOICE_CREATE = "invoice.create"
    INVOICE_EDIT = "invoice.edit"
    SIGNATURE_USE = "signature.use"
    SEAL_USE = "seal.use"
    AUDIT_VIEW = "audit.view"

# Mapping roles to default permissions
ROLE_PERMISSIONS = {
    RoleEnum.OWNER: list(PermissionEnum),
    RoleEnum.ADMIN: [p for p in PermissionEnum if p not in []],
    RoleEnum.MANAGER: [
        PermissionEnum.COMPANY_VIEW,
        PermissionEnum.TEAM_VIEW, PermissionEnum.TEAM_EDIT,
        PermissionEnum.CLIENT_VIEW, PermissionEnum.CLIENT_EDIT,
        PermissionEnum.PROJECT_VIEW, PermissionEnum.PROJECT_EDIT,
        PermissionEnum.SERVICE_VIEW, PermissionEnum.SERVICE_EDIT,
        PermissionEnum.DOCUMENT_VIEW, PermissionEnum.DOCUMENT_UPLOAD,
        PermissionEnum.TENDER_VIEW, PermissionEnum.TENDER_CREATE, PermissionEnum.TENDER_EDIT,
        PermissionEnum.INVOICE_VIEW, PermissionEnum.INVOICE_CREATE,
        PermissionEnum.AUDIT_VIEW,
    ],
    RoleEnum.TENDER_MANAGER: [
        PermissionEnum.COMPANY_VIEW,
        PermissionEnum.TEAM_VIEW,
        PermissionEnum.CLIENT_VIEW,
        PermissionEnum.PROJECT_VIEW,
        PermissionEnum.SERVICE_VIEW,
        PermissionEnum.DOCUMENT_VIEW, PermissionEnum.DOCUMENT_UPLOAD,
        PermissionEnum.TENDER_VIEW, PermissionEnum.TENDER_CREATE, PermissionEnum.TENDER_EDIT, PermissionEnum.TENDER_APPROVE, PermissionEnum.TENDER_EXPORT,
        PermissionEnum.AUDIT_VIEW,
    ],
    RoleEnum.MEMBER: [
        PermissionEnum.COMPANY_VIEW,
        PermissionEnum.TEAM_VIEW,
        PermissionEnum.CLIENT_VIEW,
        PermissionEnum.PROJECT_VIEW,
        PermissionEnum.SERVICE_VIEW,
        PermissionEnum.DOCUMENT_VIEW, PermissionEnum.DOCUMENT_UPLOAD,
        PermissionEnum.TENDER_VIEW,
    ],
    RoleEnum.VIEWER: [
        PermissionEnum.COMPANY_VIEW,
        PermissionEnum.TEAM_VIEW,
        PermissionEnum.CLIENT_VIEW,
        PermissionEnum.PROJECT_VIEW,
        PermissionEnum.SERVICE_VIEW,
        PermissionEnum.DOCUMENT_VIEW,
        PermissionEnum.TENDER_VIEW,
    ],
}

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=True, nullable=False)
    avatar_url = Column(String(512), nullable=True)

    memberships = relationship("Membership", back_populates="user", cascade="all, delete-orphan")

class Company(Base, TimestampMixin):
    __tablename__ = "companies"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    domain = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    memberships = relationship("Membership", back_populates="company", cascade="all, delete-orphan")
    profile = relationship("CompanyProfile", back_populates="company", uselist=False, cascade="all, delete-orphan")
    brand = relationship("CompanyBrand", back_populates="company", uselist=False, cascade="all, delete-orphan")
    contacts = relationship("CompanyContact", back_populates="company", cascade="all, delete-orphan")
    letterheads = relationship("CompanyLetterhead", back_populates="company", cascade="all, delete-orphan")
    signatures = relationship("CompanySignature", back_populates="company", cascade="all, delete-orphan")
    seals = relationship("CompanySeal", back_populates="company", cascade="all, delete-orphan")
    partner_logos = relationship("PartnerLogo", back_populates="company", cascade="all, delete-orphan")
    team_members = relationship("TeamMember", back_populates="company", cascade="all, delete-orphan")
    clients = relationship("Client", back_populates="company", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="company", cascade="all, delete-orphan")
    services = relationship("Service", back_populates="company", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="company", cascade="all, delete-orphan")

class Membership(Base, TimestampMixin):
    __tablename__ = "memberships"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(SQLEnum(RoleEnum), default=RoleEnum.MEMBER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    user = relationship("User", back_populates="memberships")
    company = relationship("Company", back_populates="memberships")

class CompanyProfile(Base, TimestampMixin):
    __tablename__ = "company_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    registration_number = Column(String(100), nullable=True)
    tax_id = Column(String(100), nullable=True)
    established_year = Column(Integer, nullable=True)
    legal_structure = Column(String(100), nullable=True)
    primary_industry = Column(String(100), nullable=True)
    overview = Column(Text, nullable=True)
    mission = Column(Text, nullable=True)
    vision = Column(Text, nullable=True)
    website = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)
    annual_turnover = Column(String(100), nullable=True)

    company = relationship("Company", back_populates="profile")

class CompanyBrand(Base, TimestampMixin):
    __tablename__ = "company_brands"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    primary_color = Column(String(50), default="#2563eb", nullable=False)
    secondary_color = Column(String(50), default="#1e293b", nullable=False)
    font_family = Column(String(100), default="Inter", nullable=False)
    logo_url = Column(String(512), nullable=True)
    dark_logo_url = Column(String(512), nullable=True)
    icon_url = Column(String(512), nullable=True)

    company = relationship("Company", back_populates="brand")

class CompanyContact(Base, TimestampMixin):
    __tablename__ = "company_contacts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_type = Column(String(50), default="email", nullable=False) # email, phone, address, social
    label = Column(String(100), nullable=False)
    value = Column(String(255), nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)

    company = relationship("Company", back_populates="contacts")

class CompanyLetterhead(Base, TimestampMixin):
    __tablename__ = "company_letterheads"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(100), default="Default Letterhead", nullable=False)
    header_html = Column(Text, nullable=True)
    footer_html = Column(Text, nullable=True)
    margin_top_mm = Column(Integer, default=25, nullable=False)
    margin_bottom_mm = Column(Integer, default=25, nullable=False)
    is_default = Column(Boolean, default=True, nullable=False)

    company = relationship("Company", back_populates="letterheads")

class CompanySignature(Base, TimestampMixin):
    __tablename__ = "company_signatures"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(255), nullable=False)
    designation = Column(String(255), nullable=False)
    signature_image_url = Column(String(512), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    company = relationship("Company", back_populates="signatures")

class CompanySeal(Base, TimestampMixin):
    __tablename__ = "company_seals"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    seal_image_url = Column(String(512), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    company = relationship("Company", back_populates="seals")

class PartnerLogo(Base, TimestampMixin):
    __tablename__ = "partner_logos"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    partner_name = Column(String(255), nullable=False)
    logo_url = Column(String(512), nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)

    company = relationship("Company", back_populates="partner_logos")
