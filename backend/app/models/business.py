import enum
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text, Integer, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from app.models.base import TimestampMixin, generate_uuid

class ClientStatusEnum(str, enum.Enum):
    LEAD = "LEAD"
    ACTIVE = "ACTIVE"
    CHURNED = "CHURNED"

class ProjectStatusEnum(str, enum.Enum):
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

# TEAM MODELS
class TeamMember(Base, TimestampMixin):
    __tablename__ = "team_members"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(100), nullable=True)
    designation = Column(String(255), nullable=False)
    department = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    skills = Column(JSON, default=list, nullable=False)
    joined_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)

    company = relationship("Company", back_populates="team_members")
    experiences = relationship("TeamMemberExperience", back_populates="member", cascade="all, delete-orphan")
    certifications = relationship("TeamMemberCertification", back_populates="member", cascade="all, delete-orphan")
    cvs = relationship("TeamMemberCV", back_populates="member", cascade="all, delete-orphan")
    project_associations = relationship("ProjectTeamMember", back_populates="member", cascade="all, delete-orphan")

class TeamMemberExperience(Base, TimestampMixin):
    __tablename__ = "team_member_experiences"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    team_member_id = Column(String(36), ForeignKey("team_members.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    organization = Column(String(255), nullable=False)
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    is_current = Column(Boolean, default=False, nullable=False)
    description = Column(Text, nullable=True)

    member = relationship("TeamMember", back_populates="experiences")

class TeamMemberCertification(Base, TimestampMixin):
    __tablename__ = "team_member_certifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    team_member_id = Column(String(36), ForeignKey("team_members.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    issuing_organization = Column(String(255), nullable=False)
    issue_date = Column(String(50), nullable=True)
    expiry_date = Column(String(50), nullable=True)
    credential_id = Column(String(255), nullable=True)
    credential_url = Column(String(512), nullable=True)

    member = relationship("TeamMember", back_populates="certifications")

class TeamMemberCV(Base, TimestampMixin):
    __tablename__ = "team_member_cvs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    team_member_id = Column(String(36), ForeignKey("team_members.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), default="Primary CV", nullable=False)
    file_url = Column(String(512), nullable=True)
    parsed_text = Column(Text, nullable=True)

    member = relationship("TeamMember", back_populates="cvs")

# CLIENT MODELS
class Client(Base, TimestampMixin):
    __tablename__ = "clients"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    industry = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    status = Column(SQLEnum(ClientStatusEnum), default=ClientStatusEnum.ACTIVE, nullable=False)
    address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    is_archived = Column(Boolean, default=False, nullable=False)

    company = relationship("Company", back_populates="clients")
    contacts = relationship("ClientContact", back_populates="client", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="client", cascade="all, delete-orphan")

class ClientContact(Base, TimestampMixin):
    __tablename__ = "client_contacts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    client_id = Column(String(36), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(100), nullable=True)
    role = Column(String(100), nullable=True)
    is_primary = Column(Boolean, default=False, nullable=False)

    client = relationship("Client", back_populates="contacts")

# PROJECT MODELS
class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id = Column(String(36), ForeignKey("clients.id", ondelete="SET NULL"), nullable=True, index=True)
    service_id = Column(String(36), ForeignKey("services.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(ProjectStatusEnum), default=ProjectStatusEnum.IN_PROGRESS, nullable=False)
    contract_value = Column(Float, default=0.0, nullable=False)
    currency = Column(String(10), default="USD", nullable=False)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    completion_summary = Column(Text, nullable=True)
    portfolio_draft_created = Column(Boolean, default=False, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)

    company = relationship("Company", back_populates="projects")
    client = relationship("Client", back_populates="projects")
    service = relationship("Service", back_populates="projects")
    team_members = relationship("ProjectTeamMember", back_populates="project", cascade="all, delete-orphan")
    documents = relationship("ProjectDocument", back_populates="project", cascade="all, delete-orphan")

class ProjectTeamMember(Base, TimestampMixin):
    __tablename__ = "project_team_members"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    team_member_id = Column(String(36), ForeignKey("team_members.id", ondelete="CASCADE"), nullable=False, index=True)
    role_in_project = Column(String(255), default="Contributor", nullable=False)

    project = relationship("Project", back_populates="team_members")
    member = relationship("TeamMember", back_populates="project_associations")

class ProjectDocument(Base, TimestampMixin):
    __tablename__ = "project_documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    document_url = Column(String(512), nullable=False)
    document_type = Column(String(100), default="EVIDENCE", nullable=False) # COMPLETION_CERTIFICATE, CONTRACT, DELIVERABLE, EVIDENCE
    notes = Column(Text, nullable=True)

    project = relationship("Project", back_populates="documents")

# SERVICE MODELS
class Service(Base, TimestampMixin):
    __tablename__ = "services"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), default="General", nullable=False)
    description = Column(Text, nullable=True)
    deliverables = Column(JSON, default=list, nullable=False)
    typical_duration = Column(String(100), nullable=True)
    standard_price = Column(Float, default=0.0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)

    company = relationship("Company", back_populates="services")
    projects = relationship("Project", back_populates="service")

# AUDIT LOG
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False) # login, upload, download, delete, generate, tender.create, export, signature.use, seal.use, permission.change
    resource_type = Column(String(100), nullable=False) # document, project, team, company, tender, proposal, etc.
    resource_id = Column(String(100), nullable=True)
    details = Column(JSON, default=dict, nullable=False)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    company = relationship("Company", back_populates="audit_logs")
