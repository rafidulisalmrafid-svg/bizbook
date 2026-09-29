import enum
from typing import List, Optional
from datetime import datetime, date
from sqlalchemy import (
    String,
    Text,
    Boolean,
    ForeignKey,
    DateTime,
    Date,
    Numeric,
    Enum,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, generate_uuid


class ProposalStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SENT = "SENT"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class InvoiceStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SENT = "SENT"
    PAID = "PAID"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"


class SocialPlatform(str, enum.Enum):
    LINKEDIN = "LINKEDIN"
    TWITTER = "TWITTER"
    FACEBOOK = "FACEBOOK"


class Proposal(Base, TimestampMixin):
    __tablename__ = "proposals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("clients.id", ondelete="SET NULL"), nullable=True)
    project_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ProposalStatus] = mapped_column(Enum(ProposalStatus), default=ProposalStatus.DRAFT, nullable=False)
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)
    discount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)
    tax_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0, nullable=False)
    tax_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)
    
    terms_and_conditions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    line_items: Mapped[List["ProposalLineItem"]] = relationship(
        "ProposalLineItem", back_populates="proposal", cascade="all, delete-orphan", lazy="selectin"
    )
    invoices: Mapped[List["Invoice"]] = relationship("Invoice", back_populates="proposal", lazy="selectin")


class ProposalLineItem(Base, TimestampMixin):
    __tablename__ = "proposal_line_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    proposal_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposals.id", ondelete="CASCADE"), nullable=False, index=True)
    
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(10, 2), default=1.0, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)

    proposal: Mapped["Proposal"] = relationship("Proposal", back_populates="line_items")


class Invoice(Base, TimestampMixin):
    __tablename__ = "invoices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id: Mapped[str] = mapped_column(String(36), ForeignKey("clients.id", ondelete="RESTRICT"), nullable=False, index=True)
    project_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    proposal_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("proposals.id", ondelete="SET NULL"), nullable=True)
    
    invoice_number: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[InvoiceStatus] = mapped_column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT, nullable=False, index=True)
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)
    discount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)
    tax_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0, nullable=False)
    tax_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)
    paid_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)
    
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    line_items: Mapped[List["InvoiceLineItem"]] = relationship(
        "InvoiceLineItem", back_populates="invoice", cascade="all, delete-orphan", lazy="selectin"
    )
    proposal: Mapped[Optional["Proposal"]] = relationship("Proposal", back_populates="invoices")


class InvoiceLineItem(Base, TimestampMixin):
    __tablename__ = "invoice_line_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    invoice_id: Mapped[str] = mapped_column(String(36), ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(10, 2), default=1.0, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)

    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="line_items")


class PortfolioCaseStudy(Base, TimestampMixin):
    __tablename__ = "portfolio_case_studies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    headline: Mapped[str] = mapped_column(String(255), nullable=False)
    client_display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    challenge: Mapped[str] = mapped_column(Text, nullable=False)
    solution: Mapped[str] = mapped_column(Text, nullable=False)
    results_and_impact: Mapped[str] = mapped_column(Text, nullable=False)
    metrics: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    is_public_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    technologies: Mapped[list] = mapped_column(JSON, default=list, nullable=False)


class SocialPost(Base, TimestampMixin):
    __tablename__ = "social_posts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    
    platform: Mapped[SocialPlatform] = mapped_column(Enum(SocialPlatform), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    hashtags: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    call_to_action: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
