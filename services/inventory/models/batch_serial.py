"""Batch and Serial Number management models."""
import enum
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from shared.database.base import Base, TimestampMixin, UUIDMixin, TenantMixin


class BatchStatus(str, enum.Enum):
    """Batch status."""
    ACTIVE = "active"
    EXPIRED = "expired"
    RECALLED = "recalled"


class Batch(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Batch tracking for items."""
    __tablename__ = "batches"
    
    batch_no = Column(String(100), nullable=False, index=True)
    item_id = Column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=False, index=True)
    
    # Manufacturing details
    manufacturing_date = Column(DateTime(timezone=True), nullable=True)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    
    # Supplier
    supplier_id = Column(UUID(as_uuid=True), nullable=True)
    supplier_batch_no = Column(String(100), nullable=True)
    
    # Status
    status = Column(Enum(BatchStatus), default=BatchStatus.ACTIVE)
    
    # Reference
    reference_type = Column(String(50), nullable=True)  # purchase_receipt, stock_entry
    reference_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Additional
    description = Column(Text, nullable=True)
    extra_data = Column(JSONB, default=dict)


class SerialNo(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Serial number tracking for items."""
    __tablename__ = "serial_nos"
    
    serial_no = Column(String(100), nullable=False, unique=True, index=True)
    item_id = Column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=False, index=True)
    
    # Current location
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=True)
    
    # Status
    status = Column(String(50), default="available")  # available, delivered, expired, damaged
    
    # Purchase details
    purchase_date = Column(DateTime(timezone=True), nullable=True)
    purchase_rate = Column(Numeric(15, 2), nullable=True)
    supplier_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Delivery details
    delivery_date = Column(DateTime(timezone=True), nullable=True)
    customer_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Warranty
    warranty_period = Column(Integer, nullable=True)  # in days
    warranty_expiry_date = Column(DateTime(timezone=True), nullable=True)
    amc_expiry_date = Column(DateTime(timezone=True), nullable=True)
    
    # Batch reference
    batch_no = Column(String(100), nullable=True)
    
    # Additional
    description = Column(Text, nullable=True)
    extra_data = Column(JSONB, default=dict)


class SerialNoHistory(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Serial number movement history."""
    __tablename__ = "serial_no_history"
    
    serial_no_id = Column(UUID(as_uuid=True), ForeignKey("serial_nos.id"), nullable=False, index=True)
    
    # Transaction details
    transaction_type = Column(String(50), nullable=False)  # purchase, delivery, transfer, etc.
    transaction_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Movement
    from_warehouse_id = Column(UUID(as_uuid=True), nullable=True)
    to_warehouse_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Date
    transaction_date = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    remarks = Column(Text, nullable=True)
