"""Contact model for CRM."""
import enum
from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, ForeignKey, String, Text
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from shared.database.base import Base, TimestampMixin, UUIDMixin, TenantMixin, AuditMixin


class ContactType(str, enum.Enum):
    """Contact type."""
    CUSTOMER = "customer"
    PROSPECT = "prospect"
    PARTNER = "partner"
    VENDOR = "vendor"
    OTHER = "other"


class Contact(Base, UUIDMixin, TimestampMixin, TenantMixin, AuditMixin):
    """
    Contact model - customer/person record.
    """
    __tablename__ = "contacts"
    
    # Basic info
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    mobile = Column(String(50), nullable=True)
    
    # Company
    company_name = Column(String(255), nullable=True)
    job_title = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    
    # Contact type
    contact_type = Column(
        Enum(ContactType),
        default=ContactType.CUSTOMER,
        nullable=False
    )
    
    # Address
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Social
    linkedin_url = Column(String(255), nullable=True)
    twitter_handle = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Assignment
    assigned_to_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Source lead
    source_lead_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Communication preferences
    email_opt_in = Column(Boolean, default=True)
    phone_opt_in = Column(Boolean, default=True)
    preferred_contact_method = Column(String(20), default="email")
    
    # Tags and custom fields
    tags = Column(JSONB, default=list)
    custom_fields = Column(JSONB, default=dict)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Soft delete
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    @property
    def full_name(self) -> str:
        """Get contact's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.email or "Unknown"
    
    def __repr__(self):
        return f"<Contact(id={self.id}, name='{self.full_name}')>"
