"""Warehouse model."""
from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from shared.database.base import Base, TimestampMixin, UUIDMixin, TenantMixin

class Warehouse(Base, UUIDMixin, TimestampMixin, TenantMixin):
    __tablename__ = "warehouses"
    
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=True, index=True)
    description = Column(Text, nullable=True)
    
    # Location
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Contact
    contact_name = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    contact_email = Column(String(255), nullable=True)
    
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    extra_data = Column(JSONB, default=dict)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
