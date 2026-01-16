"""Order model for CRM."""
import enum
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, ForeignKey, Integer,
    Numeric, String, Text
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, relationship

from shared.database.base import Base, TimestampMixin, UUIDMixin, TenantMixin, AuditMixin


class OrderStatus(str, enum.Enum):
    """Order status."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, enum.Enum):
    """Payment status."""
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    OVERDUE = "overdue"
    REFUNDED = "refunded"


class Order(Base, UUIDMixin, TimestampMixin, TenantMixin, AuditMixin):
    """
    Order model - confirmed sales order.
    """
    __tablename__ = "orders"
    
    # Reference
    order_number = Column(String(50), nullable=False, unique=True, index=True)
    
    # Related entities
    quote_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    deal_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    contact_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Customer info
    customer_name = Column(String(255), nullable=False)
    customer_email = Column(String(255), nullable=True)
    customer_phone = Column(String(50), nullable=True)
    customer_company = Column(String(255), nullable=True)
    
    # Addresses
    billing_address = Column(Text, nullable=True)
    shipping_address = Column(Text, nullable=True)
    
    # Status
    status = Column(
        Enum(OrderStatus),
        default=OrderStatus.PENDING,
        nullable=False,
        index=True
    )
    payment_status = Column(
        Enum(PaymentStatus),
        default=PaymentStatus.PENDING,
        nullable=False,
        index=True
    )
    
    # Amounts
    subtotal = Column(Numeric(15, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    shipping_amount = Column(Numeric(15, 2), default=0)
    total = Column(Numeric(15, 2), default=0)
    amount_paid = Column(Numeric(15, 2), default=0)
    amount_due = Column(Numeric(15, 2), default=0)
    currency = Column(String(3), default="USD")
    
    # Payment
    payment_method = Column(String(50), nullable=True)
    payment_reference = Column(String(255), nullable=True)
    payment_due_date = Column(DateTime(timezone=True), nullable=True)
    
    # Shipping
    shipping_method = Column(String(100), nullable=True)
    tracking_number = Column(String(255), nullable=True)
    shipped_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    
    # Dates
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(String(255), nullable=True)
    
    # Notes
    internal_notes = Column(Text, nullable=True)
    customer_notes = Column(Text, nullable=True)
    
    # Assignment
    assigned_to_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Tags and custom fields
    tags = Column(JSONB, default=list)
    custom_fields = Column(JSONB, default=dict)
    
    # Metadata
    metadata = Column(JSONB, default=dict)
    
    # Soft delete
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )
    
    def calculate_totals(self):
        """Calculate order totals from items."""
        self.subtotal = sum(item.line_total for item in self.items)
        self.total = self.subtotal - self.discount_amount + self.tax_amount + self.shipping_amount
        self.amount_due = self.total - self.amount_paid
    
    def __repr__(self):
        return f"<Order(number='{self.order_number}', status={self.status})>"


class OrderItem(Base, UUIDMixin, TimestampMixin):
    """Order line item."""
    __tablename__ = "order_items"
    
    # Parent order
    order_id = Column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Product reference (optional)
    product_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Item details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    sku = Column(String(50), nullable=True)
    
    # Quantity and pricing
    quantity = Column(Numeric(10, 2), default=1)
    unit_price = Column(Numeric(15, 2), nullable=False)
    discount_amount = Column(Numeric(15, 2), default=0)
    line_total = Column(Numeric(15, 2), nullable=False)
    
    # Fulfillment
    quantity_shipped = Column(Numeric(10, 2), default=0)
    quantity_delivered = Column(Numeric(10, 2), default=0)
    
    # Sort order
    sort_order = Column(Integer, default=0)
    
    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    
    def calculate_line_total(self):
        """Calculate line total."""
        self.line_total = (self.unit_price * self.quantity) - self.discount_amount
    
    def __repr__(self):
        return f"<OrderItem(name='{self.name}', quantity={self.quantity})>"
