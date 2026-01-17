"""Deal/Opportunity model for CRM."""
import enum
from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, ForeignKey, Integer,
    Numeric, String, Text
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from shared.database.base import Base, TimestampMixin, UUIDMixin, TenantMixin, AuditMixin


class DealStage(str, enum.Enum):
    """Deal pipeline stages."""
    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    NEEDS_ANALYSIS = "needs_analysis"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class DealPriority(str, enum.Enum):
    """Deal priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Deal(Base, UUIDMixin, TimestampMixin, TenantMixin, AuditMixin):
    """
    Deal/Opportunity model - sales opportunity tracking.
    """
    __tablename__ = "deals"
    
    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Related entities
    contact_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    lead_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    company_name = Column(String(255), nullable=True)
    
    # Pipeline
    stage = Column(
        Enum(DealStage),
        default=DealStage.PROSPECTING,
        nullable=False,
        index=True
    )
    pipeline_id = Column(UUID(as_uuid=True), nullable=True)  # Custom pipeline
    
    # Priority
    priority = Column(
        Enum(DealPriority),
        default=DealPriority.MEDIUM,
        nullable=False
    )
    
    # Value
    amount = Column(Numeric(15, 2), nullable=True)
    currency = Column(String(3), default="USD")
    probability = Column(Integer, default=50)  # Win probability percentage
    expected_revenue = Column(Numeric(15, 2), nullable=True)  # amount * probability
    
    # Dates
    expected_close_date = Column(DateTime(timezone=True), nullable=True)
    actual_close_date = Column(DateTime(timezone=True), nullable=True)
    
    # Assignment
    assigned_to_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    team_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Win/Loss
    won_at = Column(DateTime(timezone=True), nullable=True)
    lost_at = Column(DateTime(timezone=True), nullable=True)
    lost_reason = Column(String(255), nullable=True)
    competitor_name = Column(String(255), nullable=True)
    
    # Quote reference
    quote_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Tags and custom fields
    tags = Column(JSONB, default=list)
    custom_fields = Column(JSONB, default=dict)
    
    # Metadata
    extra_data = Column(JSONB, default=dict)
    
    # Soft delete
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    @property
    def is_open(self) -> bool:
        """Check if deal is still open."""
        return self.stage not in [DealStage.CLOSED_WON, DealStage.CLOSED_LOST]
    
    @property
    def is_won(self) -> bool:
        """Check if deal was won."""
        return self.stage == DealStage.CLOSED_WON
    
    def __repr__(self):
        return f"<Deal(id={self.id}, name='{self.name}', stage={self.stage})>"
