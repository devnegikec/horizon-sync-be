"""Lead model for CRM."""
import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, ForeignKey, Integer,
    Numeric, String, Text
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, relationship

from shared.database.base import Base, TimestampMixin, UUIDMixin, TenantMixin, AuditMixin


class LeadStatus(str, enum.Enum):
    """Lead status stages."""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"
    DISQUALIFIED = "disqualified"


class LeadSource(str, enum.Enum):
    """Lead source channels."""
    WEBSITE = "website"
    REFERRAL = "referral"
    SOCIAL_MEDIA = "social_media"
    ADVERTISING = "advertising"
    EMAIL_CAMPAIGN = "email_campaign"
    COLD_CALL = "cold_call"
    TRADE_SHOW = "trade_show"
    PARTNER = "partner"
    OTHER = "other"


class LeadPriority(str, enum.Enum):
    """Lead priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Lead(Base, UUIDMixin, TimestampMixin, TenantMixin, AuditMixin):
    """
    Lead model - potential customer/opportunity.
    Multi-tenant isolated by organization_id.
    """
    __tablename__ = "leads"
    
    # Basic info
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Contact info
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    company_name = Column(String(255), nullable=True)
    job_title = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Address
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Status & Source
    status = Column(
        Enum(LeadStatus),
        default=LeadStatus.NEW,
        nullable=False,
        index=True
    )
    source = Column(
        Enum(LeadSource),
        default=LeadSource.OTHER,
        nullable=False
    )
    source_details = Column(String(255), nullable=True)
    
    # Priority & Score
    priority = Column(
        Enum(LeadPriority),
        default=LeadPriority.MEDIUM,
        nullable=False
    )
    score = Column(Integer, default=0)  # Lead scoring
    
    # Value
    estimated_value = Column(Numeric(15, 2), nullable=True)
    currency = Column(String(3), default="USD")
    
    # Assignment
    assigned_to_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    team_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Conversion
    converted_at = Column(DateTime(timezone=True), nullable=True)
    converted_to_contact_id = Column(UUID(as_uuid=True), nullable=True)
    converted_to_deal_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Loss info
    lost_reason = Column(String(255), nullable=True)
    lost_at = Column(DateTime(timezone=True), nullable=True)
    
    # Follow-up
    next_follow_up = Column(DateTime(timezone=True), nullable=True)
    last_contacted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Tags and custom fields
    tags = Column(JSONB, default=list)
    custom_fields = Column(JSONB, default=dict)
    
    # Metadata
    metadata = Column(JSONB, default=dict)
    
    # Soft delete
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    @property
    def full_name(self) -> str:
        """Get lead's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.company_name:
            return self.company_name
        return self.email or "Unknown"
    
    def __repr__(self):
        return f"<Lead(id={self.id}, title='{self.title}', status={self.status})>"
