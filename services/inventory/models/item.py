"""Item and Item Group models for inventory master data."""
import enum
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from shared.database.base import Base, TimestampMixin, UUIDMixin, TenantMixin, AuditMixin


class ValuationMethod(str, enum.Enum):
    """Valuation methods for inventory."""
    FIFO = "fifo"
    LIFO = "lifo"
    MOVING_AVERAGE = "moving_average"
    WEIGHTED_AVERAGE = "weighted_average"


class ItemType(str, enum.Enum):
    """Item types."""
    STOCK = "stock"
    SERVICE = "service"
    ASSET = "asset"


class ItemStatus(str, enum.Enum):
    """Item status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"


class ItemGroup(Base, UUIDMixin, TimestampMixin, TenantMixin, AuditMixin):
    """Item Group for hierarchical classification."""
    __tablename__ = "item_groups"
    
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=True, index=True)
    description = Column(Text, nullable=True)
    
    # Hierarchical structure
    parent_id = Column(UUID(as_uuid=True), ForeignKey("item_groups.id"), nullable=True)
    
    # Default settings for items in this group
    default_valuation_method = Column(Enum(ValuationMethod), default=ValuationMethod.FIFO)
    default_uom = Column(String(50), nullable=True)
    
    is_active = Column(Boolean, default=True)
    extra_data = Column(JSONB, default=dict)
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class Item(Base, UUIDMixin, TimestampMixin, TenantMixin, AuditMixin):
    """Item master for inventory management."""
    __tablename__ = "items"
    
    # Basic Information
    item_code = Column(String(100), nullable=False, unique=True, index=True)
    item_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Classification
    item_group_id = Column(UUID(as_uuid=True), ForeignKey("item_groups.id"), nullable=True)
    item_type = Column(Enum(ItemType), default=ItemType.STOCK, nullable=False)
    
    # Unit of Measure
    uom = Column(String(50), nullable=False)  # Unit of Measure (e.g., Nos, Kg, Meter)
    
    # Inventory Settings
    maintain_stock = Column(Boolean, default=True)
    valuation_method = Column(Enum(ValuationMethod), default=ValuationMethod.FIFO)
    allow_negative_stock = Column(Boolean, default=False)
    
    # Variant Settings
    has_variants = Column(Boolean, default=False)
    variant_of = Column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=True)  # Parent item if this is a variant
    variant_attributes = Column(JSONB, default=dict)  # e.g., {"color": "red", "size": "L"}
    
    # Batch and Serial
    has_batch_no = Column(Boolean, default=False)
    has_serial_no = Column(Boolean, default=False)
    batch_number_series = Column(String(100), nullable=True)
    serial_number_series = Column(String(100), nullable=True)
    
    # Pricing
    standard_rate = Column(Numeric(15, 2), nullable=True)
    valuation_rate = Column(Numeric(15, 2), nullable=True)
    
    # Reordering
    enable_auto_reorder = Column(Boolean, default=False)
    reorder_level = Column(Integer, default=0)
    reorder_qty = Column(Integer, default=0)
    min_order_qty = Column(Integer, default=1)
    max_order_qty = Column(Integer, nullable=True)
    
    # Physical Properties
    weight_per_unit = Column(Numeric(10, 3), nullable=True)
    weight_uom = Column(String(20), nullable=True)
    
    # Quality
    inspection_required_before_purchase = Column(Boolean, default=False)
    inspection_required_before_delivery = Column(Boolean, default=False)
    quality_inspection_template = Column(UUID(as_uuid=True), nullable=True)
    
    # Barcode
    barcode = Column(String(100), nullable=True, index=True)
    
    # Status
    status = Column(Enum(ItemStatus), default=ItemStatus.ACTIVE, nullable=False)
    
    # Media
    image_url = Column(String(500), nullable=True)
    images = Column(JSONB, default=list)
    
    # Additional
    tags = Column(JSONB, default=list)
    custom_fields = Column(JSONB, default=dict)
    extra_data = Column(JSONB, default=dict)
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class ItemPrice(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Item pricing for different price lists."""
    __tablename__ = "item_prices"
    
    item_id = Column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=False, index=True)
    price_list_id = Column(UUID(as_uuid=True), nullable=True)  # Reference to price list
    
    price = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="USD")
    
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_upto = Column(DateTime(timezone=True), nullable=True)
    
    min_qty = Column(Integer, default=1)
    
    extra_data = Column(JSONB, default=dict)


class ItemSupplier(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Item supplier mapping."""
    __tablename__ = "item_suppliers"
    
    item_id = Column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=False, index=True)
    supplier_id = Column(UUID(as_uuid=True), nullable=False)  # Reference to supplier
    
    supplier_part_no = Column(String(100), nullable=True)
    lead_time_days = Column(Integer, default=0)
    is_default = Column(Boolean, default=False)
    
    extra_data = Column(JSONB, default=dict)
