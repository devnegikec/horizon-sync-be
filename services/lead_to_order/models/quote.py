"""Quote model for CRM."""
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


class QuoteStatus(str, enum.Enum):
    """Quote status."""
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class Quote(Base, UUIDMixin, TimestampMixin, TenantMixin, AuditMixin):
    """
    Quote/Proposal model - formal price quote sent to customer.
    """
    __tablename__ = "quotes"
    
    # Reference
    quote_number = Column(String(50), nullable=False, unique=True, index=True)
    
    # Related entities
    deal_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    contact_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Customer info (snapshot at quote creation)
    customer_name = Column(String(255), nullable=False)
    customer_email = Column(String(255), nullable=True)
    customer_phone = Column(String(50), nullable=True)
    customer_company = Column(String(255), nullable=True)
    
    # Billing address
    billing_address = Column(Text, nullable=True)
    
    # Status
    status = Column(
        Enum(QuoteStatus),
        default=QuoteStatus.DRAFT,
        nullable=False,
        index=True
    )
    
    # Validity
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)
    
    # Amounts
    subtotal = Column(Numeric(15, 2), default=0)
    discount_percent = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    tax_percent = Column(Numeric(5, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    total = Column(Numeric(15, 2), default=0)
    currency = Column(String(3), default="USD")
    
    # Terms
    payment_terms = Column(Text, nullable=True)
    terms_and_conditions = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Dates
    sent_at = Column(DateTime(timezone=True), nullable=True)
    viewed_at = Column(DateTime(timezone=True), nullable=True)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(String(255), nullable=True)
    
    # Assignment
    assigned_to_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Converted to order
    order_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Tags and custom fields
    tags = Column(JSONB, default=list)
    custom_fields = Column(JSONB, default=dict)
    
    # Metadata
    extra_data = Column(JSONB, default=dict)
    
    # Soft delete
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    items: Mapped[List["QuoteItem"]] = relationship(
        "QuoteItem",
        back_populates="quote",
        cascade="all, delete-orphan"
    )
    
    def calculate_totals(self):
        """Calculate quote totals from items."""
        self.subtotal = sum(item.line_total for item in self.items)
        self.discount_amount = self.subtotal * (self.discount_percent / 100)
        after_discount = self.subtotal - self.discount_amount
        self.tax_amount = after_discount * (self.tax_percent / 100)
        self.total = after_discount + self.tax_amount
    
    def __repr__(self):
        return f"<Quote(number='{self.quote_number}', status={self.status})>"


class QuoteItem(Base, UUIDMixin, TimestampMixin):
    """Quote line item."""
    __tablename__ = "quote_items"
    
    # Parent quote
    quote_id = Column(
        UUID(as_uuid=True),
        ForeignKey("quotes.id", ondelete="CASCADE"),
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
    discount_percent = Column(Numeric(5, 2), default=0)
    line_total = Column(Numeric(15, 2), nullable=False)
    
    # Sort order
    sort_order = Column(Integer, default=0)
    
    # Relationships
    quote: Mapped["Quote"] = relationship("Quote", back_populates="items")
    
    def calculate_line_total(self):
        """Calculate line total."""
        discount = self.unit_price * self.quantity * (self.discount_percent / 100)
        self.line_total = (self.unit_price * self.quantity) - discount
    
    def __repr__(self):
        return f"<QuoteItem(name='{self.name}', quantity={self.quantity})>"
