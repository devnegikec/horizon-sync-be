"""Warehouse model."""
import enum
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from shared.database.base import Base, TimestampMixin, UUIDMixin, TenantMixin, AuditMixin

class WarehouseType(str, enum.Enum):
    """Warehouse types."""
    STANDARD = "standard"
    TRANSIT = "transit"
    VIRTUAL = "virtual"
    CONSIGNMENT = "consignment"

class Warehouse(Base, UUIDMixin, TimestampMixin, TenantMixin, AuditMixin):
    __tablename__ = "warehouses"
    
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=True, unique=True, index=True)
    description = Column(Text, nullable=True)
    
    # Hierarchical structure
    parent_warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=True)
    warehouse_type = Column(Enum(WarehouseType), default=WarehouseType.STANDARD)
    
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
    
    # Capacity
    total_capacity = Column(Integer, nullable=True)  # Total capacity in units
    capacity_uom = Column(String(20), nullable=True)  # Unit of measure for capacity
    
    # Accounting
    stock_account_id = Column(UUID(as_uuid=True), nullable=True)  # GL account for stock
    
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    extra_data = Column(JSONB, default=dict)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

class PutAwayRule(Base, UUIDMixin, TimestampMixin, TenantMixin, AuditMixin):
    """Put-away rules for warehouse management."""
    __tablename__ = "put_away_rules"
    
    name = Column(String(255), nullable=False)
    
    # Item filters
    item_id = Column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=True)
    item_group_id = Column(UUID(as_uuid=True), ForeignKey("item_groups.id"), nullable=True)
    
    # Warehouse assignment
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False)
    
    # Capacity and priority
    capacity = Column(Integer, nullable=True)  # Max capacity for this rule
    priority = Column(Integer, default=1)  # Lower number = higher priority
    
    # Conditions
    min_qty = Column(Integer, default=0)
    max_qty = Column(Integer, nullable=True)
    
    is_active = Column(Boolean, default=True)
    extra_data = Column(JSONB, default=dict)

class PickList(Base, UUIDMixin, TimestampMixin, TenantMixin, AuditMixin):
    """Pick list for order fulfillment."""
    __tablename__ = "pick_lists"
    
    pick_list_no = Column(String(100), nullable=False, unique=True, index=True)
    
    # Reference
    reference_type = Column(String(50), nullable=True)  # sales_order, work_order
    reference_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Warehouse
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False)
    
    # Status
    status = Column(String(50), default="draft")  # draft, submitted, completed, cancelled
    
    # Dates
    pick_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Assignment
    assigned_to = Column(UUID(as_uuid=True), nullable=True)
    
    notes = Column(Text, nullable=True)
    extra_data = Column(JSONB, default=dict)

class PickListItem(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Pick list items."""
    __tablename__ = "pick_list_items"
    
    pick_list_id = Column(UUID(as_uuid=True), ForeignKey("pick_lists.id"), nullable=False, index=True)
    
    item_id = Column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=False)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False)
    
    qty_to_pick = Column(Integer, nullable=False)
    qty_picked = Column(Integer, default=0)
    
    # Batch/Serial
    batch_no = Column(String(100), nullable=True)
    serial_nos = Column(JSONB, default=list)
    
    # Location within warehouse
    bin_location = Column(String(100), nullable=True)
    
    extra_data = Column(JSONB, default=dict)
