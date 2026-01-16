"""Ticket model for support system."""
import enum
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, relationship
from shared.database.base import Base, TimestampMixin, UUIDMixin, TenantMixin, AuditMixin

class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_ON_CUSTOMER = "waiting_on_customer"
    WAITING_ON_THIRD_PARTY = "waiting_on_third_party"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"

class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class TicketCategory(str, enum.Enum):
    GENERAL = "general"
    TECHNICAL = "technical"
    BILLING = "billing"
    SALES = "sales"
    FEATURE_REQUEST = "feature_request"
    BUG_REPORT = "bug_report"
    OTHER = "other"

class Ticket(Base, UUIDMixin, TimestampMixin, TenantMixin, AuditMixin):
    __tablename__ = "tickets"
    
    ticket_number = Column(String(50), nullable=False, unique=True, index=True)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Requester
    contact_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    requester_name = Column(String(255), nullable=True)
    requester_email = Column(String(255), nullable=True, index=True)
    requester_phone = Column(String(50), nullable=True)
    
    # Classification
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN, nullable=False, index=True)
    priority = Column(Enum(TicketPriority), default=TicketPriority.MEDIUM, nullable=False)
    category = Column(Enum(TicketCategory), default=TicketCategory.GENERAL, nullable=False)
    
    # Assignment
    assigned_to_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    team_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # SLA
    due_date = Column(DateTime(timezone=True), nullable=True)
    first_response_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Resolution
    resolution_notes = Column(Text, nullable=True)
    satisfaction_rating = Column(Integer, nullable=True)  # 1-5
    
    # Related
    related_deal_id = Column(UUID(as_uuid=True), nullable=True)
    related_order_id = Column(UUID(as_uuid=True), nullable=True)
    
    tags = Column(JSONB, default=list)
    custom_fields = Column(JSONB, default=dict)
    metadata = Column(JSONB, default=dict)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    comments: Mapped[list["TicketComment"]] = relationship("TicketComment", back_populates="ticket", cascade="all, delete-orphan")
