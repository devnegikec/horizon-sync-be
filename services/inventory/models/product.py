"""Product model for inventory."""
import enum
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Numeric, String, Text, Integer
from sqlalchemy.dialects.postgresql import JSONB, UUID
from shared.database.base import Base, TimestampMixin, UUIDMixin, TenantMixin, AuditMixin

class ProductStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"
    OUT_OF_STOCK = "out_of_stock"

class ProductCategory(Base, UUIDMixin, TimestampMixin, TenantMixin):
    __tablename__ = "product_categories"
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("product_categories.id"), nullable=True)
    is_active = Column(Boolean, default=True)

class Product(Base, UUIDMixin, TimestampMixin, TenantMixin, AuditMixin):
    __tablename__ = "products"
    
    name = Column(String(255), nullable=False)
    sku = Column(String(100), nullable=False, index=True)
    barcode = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    
    category_id = Column(UUID(as_uuid=True), ForeignKey("product_categories.id"), nullable=True)
    
    # Pricing
    unit_price = Column(Numeric(15, 2), nullable=False, default=0)
    cost_price = Column(Numeric(15, 2), nullable=True)
    currency = Column(String(3), default="USD")
    tax_rate = Column(Numeric(5, 2), default=0)
    
    # Inventory
    track_inventory = Column(Boolean, default=True)
    min_stock_level = Column(Integer, default=0)
    reorder_point = Column(Integer, default=0)
    reorder_quantity = Column(Integer, default=0)
    
    # Physical
    weight = Column(Numeric(10, 2), nullable=True)
    weight_unit = Column(String(10), default="kg")
    dimensions = Column(JSONB, nullable=True)  # {length, width, height, unit}
    
    status = Column(Enum(ProductStatus), default=ProductStatus.ACTIVE, nullable=False)
    
    # Media
    image_url = Column(String(500), nullable=True)
    images = Column(JSONB, default=list)
    
    tags = Column(JSONB, default=list)
    custom_fields = Column(JSONB, default=dict)
    extra_data = Column(JSONB, default=dict)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
