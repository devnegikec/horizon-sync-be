"""Subscription and Plan models."""
import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, ForeignKey, Integer,
    Numeric, String, Text
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, relationship

from shared.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from shared.models.organization import Organization


class PlanType(str, enum.Enum):
    """Subscription plan types."""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class BillingCycle(str, enum.Enum):
    """Billing cycle options."""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    LIFETIME = "lifetime"


class SubscriptionStatus(str, enum.Enum):
    """Subscription status."""
    ACTIVE = "active"
    TRIAL = "trial"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    SUSPENDED = "suspended"


class SubscriptionPlan(Base, UUIDMixin):
    """
    Subscription plan definitions.
    """
    __tablename__ = "subscription_plans"
    
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=True, index=True)
    price = Column(Numeric(10, 2), nullable=True)
    billing_cycle = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    
    # Limits
    max_users = Column(Integer, default=0)
    max_teams = Column(Integer, default=0)
    max_storage_gb = Column(Integer, default=0)
    max_leads = Column(Integer, default=0)
    max_contacts = Column(Integer, default=0)
    max_deals = Column(Integer, default=0)
    max_tickets = Column(Integer, default=0)
    max_products = Column(Integer, default=0)
    max_api_calls_per_day = Column(Integer, default=0)
    
    features = Column(JSONB, default=list)
    
    # Relationships
    subscriptions: Mapped[List["Subscription"]] = relationship(
        "Subscription",
        back_populates="plan"
    )
    
    def __repr__(self):
        return f"<SubscriptionPlan(name='{self.name}')>"


class Subscription(Base, UUIDMixin):
    """
    Organization subscription.
    """
    __tablename__ = "subscriptions"
    
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    plan_id = Column(
        UUID(as_uuid=True),
        ForeignKey("subscription_plans.id"),
        nullable=False
    )
    
    stripe_subscription_id = Column(String(255), nullable=True)
    stripe_customer_id = Column(String(255), nullable=True)
    status = Column(String(50), nullable=True)
    starts_at = Column(DateTime(timezone=True), nullable=True)
    ends_at = Column(DateTime(timezone=True), nullable=True)
    trial_starts_at = Column(DateTime(timezone=True), nullable=True)
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    auto_renew = Column(Boolean, default=True)
    current_storage_mb = Column(Numeric(15, 2), default=0)
    extra_data = Column(JSONB, nullable=True)
    
    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="subscriptions"
    )
    plan: Mapped["SubscriptionPlan"] = relationship(
        "SubscriptionPlan",
        back_populates="subscriptions"
    )
    invoices: Mapped[List["SubscriptionInvoice"]] = relationship(
        "SubscriptionInvoice",
        back_populates="subscription",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Subscription(org_id={self.organization_id}, status={self.status})>"


class SubscriptionInvoice(Base, UUIDMixin):
    """
    Subscription invoices.
    """
    __tablename__ = "subscription_invoices"
    
    subscription_id = Column(
        UUID(as_uuid=True),
        ForeignKey("subscriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    stripe_invoice_id = Column(String(255), nullable=True)
    invoice_number = Column(String(100), nullable=True)
    amount = Column(Numeric(10, 2), nullable=True)
    status = Column(String(50), nullable=True)
    billing_period_start = Column(DateTime(timezone=True), nullable=True)
    billing_period_end = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    subscription: Mapped["Subscription"] = relationship("Subscription", back_populates="invoices")
    payments: Mapped[List["SubscriptionPayment"]] = relationship(
        "SubscriptionPayment",
        back_populates="invoice",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<SubscriptionInvoice(id={self.id}, number={self.invoice_number})>"


class SubscriptionPayment(Base, UUIDMixin):
    """
    Subscription payments.
    """
    __tablename__ = "subscription_payments"
    
    invoice_id = Column(
        UUID(as_uuid=True),
        ForeignKey("subscription_invoices.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    stripe_payment_intent_id = Column(String(255), nullable=True)
    amount = Column(Numeric(10, 2), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), nullable=True)
    
    # Relationships
    invoice: Mapped["SubscriptionInvoice"] = relationship("SubscriptionInvoice", back_populates="payments")
    
    def __repr__(self):
        return f"<SubscriptionPayment(id={self.id}, amount={self.amount})>"

