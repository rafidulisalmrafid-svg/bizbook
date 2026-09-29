import enum
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text, Integer, Float, JSON
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import TimestampMixin, generate_uuid

class PlanTier(str, enum.Enum):
    STARTER = "STARTER"
    PROFESSIONAL = "PROFESSIONAL"
    ENTERPRISE = "ENTERPRISE"

class NotificationType(str, enum.Enum):
    TENDER_DEADLINE = "TENDER_DEADLINE"
    DOCUMENT_EXPIRY = "DOCUMENT_EXPIRY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    MISSING_REQUIREMENT = "MISSING_REQUIREMENT"
    SIGNATURE_REQUIRED = "SIGNATURE_REQUIRED"

class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    plan_tier = Column(SQLEnum(PlanTier), default=PlanTier.PROFESSIONAL, nullable=False)
    monthly_token_quota = Column(Integer, default=500000, nullable=False)
    tokens_consumed = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    current_period_end = Column(DateTime, nullable=True)

class AIUsageLog(Base):
    __tablename__ = "ai_usage_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    provider = Column(String(50), nullable=False) # openai, anthropic, mock
    model = Column(String(100), nullable=False)
    operation = Column(String(100), nullable=False) # generate_text, analyze_document, etc.
    prompt_version = Column(String(50), default="v1.0", nullable=False)
    prompt_tokens = Column(Integer, default=0, nullable=False)
    completion_tokens = Column(Integer, default=0, nullable=False)
    total_tokens = Column(Integer, default=0, nullable=False)
    estimated_cost_usd = Column(Float, default=0.0, nullable=False)
    latency_ms = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    type = Column(SQLEnum(NotificationType), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(100), nullable=True)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
