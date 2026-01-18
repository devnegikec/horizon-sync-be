"""Stock models for inventory tracking."""
import enum
from datetime import datetime
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from shared.database.base import Base, TimestampMixin, UUIDMixin, TenantMixin

class StockLevel(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Current stock levels per product per warehouse."""
    __tablename__ = "stock_levels"
    
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False, index=True)
    
    quantity_on_hand = Column(Integer, default=0)
    quantity_reserved = Column(Integer, default=0)  # Reserved for orders
    quantity_available = Column(Integer, default=0)  # on_hand - reserved
    
    last_counted_at = Column(DateTime(timezone=True), nullable=True)

class MovementType(str, enum.Enum):
    PURCHASE = "purchase"
    SALE = "sale"
    TRANSFER = "transfer"
    ADJUSTMENT = "adjustment"
    RETURN = "return"
    DAMAGE = "damage"

class StockMovement(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Stock movement history."""
    __tablename__ = "stock_movements"
    
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False)
    
    movement_type = Column(Enum(MovementType), nullable=False)
    quantity = Column(Integer, nullable=False)  # Positive for in, negative for out
    unit_cost = Column(Numeric(15, 2), nullable=True)
    
    reference_type = Column(String(50), nullable=True)  # order, purchase_order, etc.
    reference_id = Column(UUID(as_uuid=True), nullable=True)
    
    notes = Column(Text, nullable=True)
    performed_by = Column(UUID(as_uuid=True), nullable=True)
    performed_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class StockLedgerEntry(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Detailed stock ledger for all transactions."""
    __tablename__ = "stock_ledger_entries"
    
    item_id = Column(UUID(as_uuid=True), ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False, index=True)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("batches.id", ondelete="SET NULL"), nullable=True)
    
    voucher_type = Column(String(50), nullable=True)
    voucher_id = Column(UUID(as_uuid=True), nullable=True)
    qty = Column(Numeric(15, 4), nullable=True)
    valuation_rate = Column(Numeric(15, 4), nullable=True)
