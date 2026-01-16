"""Ticket Comment model."""
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, relationship
from shared.database.base import Base, TimestampMixin, UUIDMixin

class TicketComment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ticket_comments"
    
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    user_name = Column(String(255), nullable=True)
    
    content = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)  # Internal notes not visible to customer
    is_resolution = Column(Boolean, default=False)
    
    attachments = Column(JSONB, default=list)
    metadata = Column(JSONB, default=dict)
    
    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="comments")
