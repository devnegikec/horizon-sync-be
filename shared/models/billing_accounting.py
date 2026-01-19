"""Billing and Accounting models."""
import enum
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text, Numeric, Table
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, relationship

from shared.database.base import Base, TimestampMixin, UUIDMixin


class CustomerStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class SupplierStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class InvoiceStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class InvoiceType(str, enum.Enum):
    SALES = "sales"
    PURCHASE = "purchase"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentType(str, enum.Enum):
    RECEIVED = "received"
    SENT = "sent"


class AccountType(str, enum.Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


class JournalEntryStatus(str, enum.Enum):
    DRAFT = "draft"
    POSTED = "posted"
    CANCELLED = "cancelled"


class Customer(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "customers"
    
    organization_id = Column(PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_name = Column(String(255), nullable=False)
    customer_code = Column(String(50), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    tax_number = Column(String(100), nullable=True)
    status = Column(String(50), default=CustomerStatus.ACTIVE.value)
    
    created_by = Column(PG_UUID(as_uuid=True), nullable=True)
    updated_by = Column(PG_UUID(as_uuid=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    tags = Column(JSONB, nullable=True)
    custom_fields = Column(JSONB, nullable=True)
    extra_data = Column(JSONB, nullable=True)


class Supplier(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "suppliers"
    
    organization_id = Column(PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    supplier_name = Column(String(255), nullable=False)
    supplier_code = Column(String(50), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    tax_number = Column(String(100), nullable=True)
    status = Column(String(50), default=SupplierStatus.ACTIVE.value)
    
    created_by = Column(PG_UUID(as_uuid=True), nullable=True)
    updated_by = Column(PG_UUID(as_uuid=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    tags = Column(JSONB, nullable=True)
    custom_fields = Column(JSONB, nullable=True)
    extra_data = Column(JSONB, nullable=True)


class Invoice(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "invoices"
    
    organization_id = Column(PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    invoice_no = Column(String(100), nullable=False)
    invoice_date = Column(DateTime(timezone=True), default=datetime.utcnow)
    due_date = Column(DateTime(timezone=True), nullable=True)
    
    invoice_type = Column(String(50), default=InvoiceType.SALES.value)
    status = Column(String(50), default=InvoiceStatus.DRAFT.value)
    
    customer_id = Column(PG_UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True)
    supplier_id = Column(PG_UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=True)
    
    total_amount = Column(Numeric(15, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    total_paid = Column(Numeric(15, 2), default=0)
    balance_due = Column(Numeric(15, 2), default=0)
    
    currency = Column(String(10), default="USD")
    notes = Column(Text, nullable=True)
    
    created_by = Column(PG_UUID(as_uuid=True), nullable=True)
    updated_by = Column(PG_UUID(as_uuid=True), nullable=True)
    extra_data = Column(JSONB, nullable=True)
    
    items: Mapped[List["InvoiceItem"]] = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceItem(Base, UUIDMixin):
    __tablename__ = "invoice_items"
    
    organization_id = Column(PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    invoice_id = Column(PG_UUID(as_uuid=True), ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    
    item_id = Column(PG_UUID(as_uuid=True), nullable=True) # Link to Inventory Item
    description = Column(String(500), nullable=False)
    quantity = Column(Numeric(15, 2), default=1)
    unit_price = Column(Numeric(15, 2), default=0)
    tax_rate = Column(Numeric(5, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), default=0)
    
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="items")


class Payment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "payments"
    
    organization_id = Column(PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    payment_no = Column(String(100), nullable=False)
    payment_date = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    payment_type = Column(String(50), nullable=False) # RECEIVED or SENT
    status = Column(String(50), default=PaymentStatus.COMPLETED.value)
    
    customer_id = Column(PG_UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True)
    supplier_id = Column(PG_UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=True)
    
    amount = Column(Numeric(15, 2), nullable=False)
    payment_method = Column(String(100), nullable=True)
    bank_account_id = Column(PG_UUID(as_uuid=True), nullable=True)
    reference_no = Column(String(255), nullable=True)
    
    created_by = Column(PG_UUID(as_uuid=True), nullable=True)
    updated_by = Column(PG_UUID(as_uuid=True), nullable=True)
    extra_data = Column(JSONB, nullable=True)
    
    allocations: Mapped[List["PaymentAllocation"]] = relationship("PaymentAllocation", back_populates="payment")


class PaymentAllocation(Base, UUIDMixin):
    __tablename__ = "payment_allocations"
    
    organization_id = Column(PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    payment_id = Column(PG_UUID(as_uuid=True), ForeignKey("payments.id", ondelete="CASCADE"), nullable=False)
    invoice_id = Column(PG_UUID(as_uuid=True), ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    allocated_amount = Column(Numeric(15, 2), nullable=False)
    
    payment: Mapped["Payment"] = relationship("Payment", back_populates="allocations")


class ChartOfAccounts(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "chart_of_accounts"
    
    organization_id = Column(PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    account_code = Column(String(50), nullable=False)
    account_name = Column(String(255), nullable=False)
    account_type = Column(String(50), nullable=False) # ASSET, LIABILITY, etc.
    
    parent_account_id = Column(PG_UUID(as_uuid=True), ForeignKey("chart_of_accounts.id"), nullable=True)
    level = Column(Integer, default=0)
    is_group = Column(Boolean, default=False)
    
    opening_balance = Column(Numeric(15, 2), default=0)
    current_balance = Column(Numeric(15, 2), default=0)
    
    created_by = Column(PG_UUID(as_uuid=True), nullable=True)
    updated_by = Column(PG_UUID(as_uuid=True), nullable=True)
    tags = Column(JSONB, nullable=True)


class JournalEntry(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "journal_entries"
    
    organization_id = Column(PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    entry_no = Column(String(100), nullable=False)
    entry_date = Column(DateTime(timezone=True), default=datetime.utcnow)
    posting_date = Column(DateTime(timezone=True), nullable=True)
    
    reference_type = Column(String(100), nullable=True) # INVOICE, PAYMENT, etc.
    reference_id = Column(PG_UUID(as_uuid=True), nullable=True)
    reference_no = Column(String(100), nullable=True)
    
    description = Column(Text, nullable=True)
    total_debit = Column(Numeric(15, 2), default=0)
    total_credit = Column(Numeric(15, 2), default=0)
    
    status = Column(String(50), default=JournalEntryStatus.DRAFT.value)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    
    created_by = Column(PG_UUID(as_uuid=True), nullable=True)
    updated_by = Column(PG_UUID(as_uuid=True), nullable=True)
    
    lines: Mapped[List["JournalEntryLine"]] = relationship("JournalEntryLine", back_populates="journal_entry", cascade="all, delete-orphan")


class JournalEntryLine(Base, UUIDMixin):
    __tablename__ = "journal_entry_lines"
    
    organization_id = Column(PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    journal_entry_id = Column(PG_UUID(as_uuid=True), ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False)
    account_id = Column(PG_UUID(as_uuid=True), ForeignKey("chart_of_accounts.id"), nullable=False)
    
    debit_amount = Column(Numeric(15, 2), default=0)
    credit_amount = Column(Numeric(15, 2), default=0)
    description = Column(String(500), nullable=True)
    line_number = Column(Integer, nullable=True)
    
    journal_entry: Mapped["JournalEntry"] = relationship("JournalEntry", back_populates="lines")
    account: Mapped["ChartOfAccounts"] = relationship("ChartOfAccounts")
