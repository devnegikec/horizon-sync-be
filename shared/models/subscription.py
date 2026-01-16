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


class SubscriptionPlan(Base, UUIDMixin, TimestampMixin):
    """
    Subscription plan definitions.
    Defines what features and limits are available for each plan tier.
    """
    __tablename__ = "subscription_plans"
    
    # Plan info
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    plan_type = Column(Enum(PlanType), nullable=False, index=True)
    
    # Pricing
    price_monthly = Column(Numeric(10, 2), nullable=True)
    price_yearly = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(3), default="USD")
    
    # Limits
    max_users = Column(Integer, default=5)
    max_teams = Column(Integer, default=3)
    max_leads = Column(Integer, default=1000)
    max_contacts = Column(Integer, default=5000)
    max_deals = Column(Integer, default=500)
    max_tickets = Column(Integer, default=1000)
    max_products = Column(Integer, default=500)
    max_storage_gb = Column(Integer, default=5)
    max_api_calls_per_day = Column(Integer, default=10000)
    
    # Features as JSON (more flexible than columns)
    features = Column(JSONB, default=dict)
    # Example features:
    # {
    #     "email_integration": true,
    #     "calendar_sync": true,
    #     "custom_fields": true,
    #     "api_access": false,
    #     "advanced_reporting": false,
    #     "sso": false,
    #     "audit_logs": false,
    #     "dedicated_support": false
    # }
    
    # Status
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)  # Show in pricing page
    
    # Trial
    trial_days = Column(Integer, default=14)
    
    # Sort order for display
    sort_order = Column(Integer, default=0)
    
    # Relationships
    subscriptions: Mapped[List["Subscription"]] = relationship(
        "Subscription",
        back_populates="plan"
    )
    
    def __repr__(self):
        return f"<SubscriptionPlan(code='{self.code}', type={self.plan_type})>"


class Subscription(Base, UUIDMixin, TimestampMixin):
    """
    Organization subscription - links organization to a plan.
    """
    __tablename__ = "subscriptions"
    
    # Relations
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
    
    # Status
    status = Column(
        Enum(SubscriptionStatus),
        default=SubscriptionStatus.TRIAL,
        nullable=False,
        index=True
    )
    
    # Dates
    trial_starts_at = Column(DateTime(timezone=True), nullable=True)
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)
    starts_at = Column(DateTime(timezone=True), nullable=True)
    ends_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Billing
    billing_cycle = Column(
        Enum(BillingCycle),
        default=BillingCycle.MONTHLY,
        nullable=False
    )
    next_billing_date = Column(DateTime(timezone=True), nullable=True)
    
    # Payment provider info
    stripe_subscription_id = Column(String(255), nullable=True)
    stripe_customer_id = Column(String(255), nullable=True)
    
    # Current usage (updated periodically)
    current_users = Column(Integer, default=0)
    current_teams = Column(Integer, default=0)
    current_storage_mb = Column(Integer, default=0)
    
    # Metadata
    metadata = Column(JSONB, default=dict)
    
    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="subscriptions"
    )
    plan: Mapped["SubscriptionPlan"] = relationship(
        "SubscriptionPlan",
        back_populates="subscriptions"
    )
    
    @property
    def is_active(self) -> bool:
        """Check if subscription is currently active."""
        return self.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL]
    
    @property
    def is_trial(self) -> bool:
        """Check if subscription is in trial period."""
        return self.status == SubscriptionStatus.TRIAL
    
    def __repr__(self):
        return f"<Subscription(org_id={self.organization_id}, status={self.status})>"


class SubscriptionUsage(Base, UUIDMixin, TimestampMixin):
    """
    Track subscription usage over time for billing and analytics.
    """
    __tablename__ = "subscription_usage"
    
    subscription_id = Column(
        UUID(as_uuid=True),
        ForeignKey("subscriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Period
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Usage metrics
    users_count = Column(Integer, default=0)
    teams_count = Column(Integer, default=0)
    leads_created = Column(Integer, default=0)
    contacts_created = Column(Integer, default=0)
    deals_created = Column(Integer, default=0)
    tickets_created = Column(Integer, default=0)
    storage_used_mb = Column(Integer, default=0)
    api_calls = Column(Integer, default=0)
    
    # Status
    is_finalized = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<SubscriptionUsage(sub_id={self.subscription_id}, period={self.period_start})>"
