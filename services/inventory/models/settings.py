"""Stock settings and configuration models."""
from sqlalchemy import Boolean, Column, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from shared.database.base import Base, TimestampMixin, UUIDMixin, TenantMixin, AuditMixin


class StockSettings(Base, UUIDMixin, TimestampMixin, TenantMixin, AuditMixin):
    """Global stock settings per organization."""
    __tablename__ = "stock_settings"
    
    # Naming series defaults
    item_naming_by = Column(String(50), default="naming_series")  # naming_series, item_code
    item_naming_series = Column(String(100), nullable=True)
    
    stock_entry_naming_series = Column(String(100), nullable=True)
    delivery_note_naming_series = Column(String(100), nullable=True)
    purchase_receipt_naming_series = Column(String(100), nullable=True)
    
    # Default warehouse
    default_warehouse_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Stock allowances
    allow_negative_stock = Column(Boolean, default=False)
    over_delivery_receipt_allowance = Column(Numeric(5, 2), default=0)  # Percentage
    over_billing_allowance = Column(Numeric(5, 2), default=0)
    
    # Auto reordering
    auto_indent = Column(Boolean, default=False)  # Auto create material request
    auto_indent_notification = Column(JSONB, default=list)  # List of roles to notify
    
    # Valuation
    default_valuation_method = Column(String(50), default="fifo")
    
    # Batch and serial
    auto_create_serial_no = Column(Boolean, default=False)
    
    # Quality
    default_quality_inspection_template_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Freeze stock entries
    stock_frozen_upto = Column(String(20), nullable=True)  # Date in YYYY-MM-DD format
    stock_frozen_upto_days = Column(Integer, default=0)
    
    # Additional settings
    show_barcode_field = Column(Boolean, default=True)
    convert_item_desc_to_transaction_desc = Column(Boolean, default=False)
    
    extra_data = Column(JSONB, default=dict)
