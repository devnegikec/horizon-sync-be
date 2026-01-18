"""Account model for CRM."""
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from shared.database.base import Base, TimestampMixin, UUIDMixin, TenantMixin, AuditMixin

class Account(Base, UUIDMixin, TimestampMixin, TenantMixin, AuditMixin):
    """Account model - represents a company or customer entity."""
    __tablename__ = "accounts"
    
    name = Column(String(255), nullable=False)
    industry = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    
    # Location
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    
    extra_data = Column(JSONB, default=dict)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
