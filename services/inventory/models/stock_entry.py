"""Stock entry and transaction models."""
import enum
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from shared.database.base import Base, TimestampMixin, UUIDMixin, TenantMixin, AuditMixin


class StockEntryType(str, enum.Enum):
    """Stock entry types."""
    MATERIAL_RECEIPT = "material_receipt"
    MATERIAL_ISSUE = "material_issue"
    MATERIAL_TRANSFER = "material_transfer"
    MANUFACTURE = "manufacture"
    REPACK = "repack"


class StockEntryStatus(str, enum.Enum):
    """Stock entry status."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    CANCELLED = "cancelled"


class StockEntry(Base, UUIDMixin, TimestampMixin, TenantMixin, AuditMixin):
    """Stock entry for material movements."""
    __tablename__ = "stock_entries"
    
    stock_entry_no = Column(String(100), nullable=False, unique=True, index=True)
    stock_entry_type = Column(Enum(StockEntryType), nullable=False)
    
    # Warehouses
    from_warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=True)
    to_warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=True)
    
    # Dates
    posting_date = Column(DateTime(timezone=True), default=datetime.utcnow)
    posting_time = Column(String(10), nullable=True)
    
    # Status
    status = Column(Enum(StockEntryStatus), default=StockEntryStatus.DRAFT)
    
    # Reference
    reference_type = Column(String(50), nullable=True)  # purchase_order, sales_order, etc.
    reference_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Additional
    remarks = Column(Text, nullable=True)
    total_value = Column(Numeric(15, 2), default=0)
    
    # Accounting
    expense_account_id = Column(UUID(as_uuid=True), nullable=True)
    cost_center_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Backflush for manufacturing
    is_backflush = Column(Boolean, default=False)
    bom_id = Column(UUID(as_uuid=True), nullable=True)  # Bill of Materials reference
    
    extra_data = Column(JSONB, default=dict)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)


class StockEntryItem(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Stock entry items."""
    __tablename__ = "stock_entry_items"
    
    stock_entry_id = Column(UUID(as_uuid=True), ForeignKey("stock_entries.id"), nullable=False, index=True)
    
    item_id = Column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=False)
    
    # Warehouses (can override header)
    source_warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=True)
    target_warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=True)
    
    # Quantity
    qty = Column(Numeric(15, 3), nullable=False)
    uom = Column(String(50), nullable=False)
    
    # Valuation
    basic_rate = Column(Numeric(15, 2), nullable=True)
    basic_amount = Column(Numeric(15, 2), nullable=True)
    valuation_rate = Column(Numeric(15, 2), nullable=True)
    
    # Batch/Serial
    batch_no = Column(String(100), nullable=True)
    serial_nos = Column(JSONB, default=list)
    
    # Quality
    quality_inspection_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Additional
    description = Column(Text, nullable=True)
    extra_data = Column(JSONB, default=dict)


class StockReconciliation(Base, UUIDMixin, TimestampMixin, TenantMixin, AuditMixin):
    """Stock reconciliation for physical count adjustments."""
    __tablename__ = "stock_reconciliations"
    
    reconciliation_no = Column(String(100), nullable=False, unique=True, index=True)
    
    # Purpose
    purpose = Column(String(50), default="opening_stock")  # opening_stock, stock_reconciliation
    
    # Dates
    posting_date = Column(DateTime(timezone=True), default=datetime.utcnow)
    posting_time = Column(String(10), nullable=True)
    
    # Status
    status = Column(Enum(StockEntryStatus), default=StockEntryStatus.DRAFT)
    
    # Accounting
    expense_account_id = Column(UUID(as_uuid=True), nullable=True)
    difference_account_id = Column(UUID(as_uuid=True), nullable=True)
    
    remarks = Column(Text, nullable=True)
    extra_data = Column(JSONB, default=dict)
    submitted_at = Column(DateTime(timezone=True), nullable=True)


class StockReconciliationItem(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Stock reconciliation items."""
    __tablename__ = "stock_reconciliation_items"
    
    reconciliation_id = Column(UUID(as_uuid=True), ForeignKey("stock_reconciliations.id"), nullable=False, index=True)
    
    item_id = Column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=False)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False)
    
    # Quantities
    current_qty = Column(Numeric(15, 3), default=0)
    qty = Column(Numeric(15, 3), nullable=False)  # New quantity after reconciliation
    qty_difference = Column(Numeric(15, 3), default=0)
    
    # Valuation
    current_valuation_rate = Column(Numeric(15, 2), nullable=True)
    valuation_rate = Column(Numeric(15, 2), nullable=True)
    
    # Batch/Serial
    batch_no = Column(String(100), nullable=True)
    serial_nos = Column(JSONB, default=list)
    
    extra_data = Column(JSONB, default=dict)
