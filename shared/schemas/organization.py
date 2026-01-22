"""Organization Pydantic schemas."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import EmailStr, Field, field_validator

from shared.models.organization import OrganizationStatus, OrganizationType
from shared.models.subscription import PlanType
from shared.schemas.common import BaseSchema


class OrganizationBase(BaseSchema):
    """Base organization schema."""
    
    name: str = Field(..., min_length=2, max_length=255)
    display_name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    
    # Contact
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    website: Optional[str] = Field(default=None, max_length=255)
    
    # Address
    address_line1: Optional[str] = Field(default=None, max_length=255)
    address_line2: Optional[str] = Field(default=None, max_length=255)
    city: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    postal_code: Optional[str] = Field(default=None, max_length=20)
    country: Optional[str] = Field(default=None, max_length=100)
    
    # Business
    organization_type: Optional[OrganizationType] = OrganizationType.SMB
    industry: Optional[str] = Field(default=None, max_length=100)
    tax_id: Optional[str] = Field(default=None, max_length=50)


class OrganizationCreate(OrganizationBase):
    """Schema for creating an organization."""
    
    slug: Optional[str] = Field(default=None, max_length=100, pattern="^[a-z0-9-]+$")
    
    @field_validator('slug', mode='before')
    @classmethod
    def generate_slug(cls, v, info):
        """Generate slug from name if not provided."""
        if v is None and 'name' in info.data:
            # Simple slug generation - can be improved
            return info.data['name'].lower().replace(' ', '-')[:100]
        return v


class OrganizationUpdate(BaseSchema):
    """Schema for updating an organization."""
    
    name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    display_name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    website: Optional[str] = Field(default=None, max_length=255)
    
    address_line1: Optional[str] = Field(default=None, max_length=255)
    address_line2: Optional[str] = Field(default=None, max_length=255)
    city: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    postal_code: Optional[str] = Field(default=None, max_length=20)
    country: Optional[str] = Field(default=None, max_length=100)
    
    organization_type: Optional[OrganizationType] = None
    industry: Optional[str] = Field(default=None, max_length=100)
    
    logo_url: Optional[str] = Field(default=None, max_length=500)
    primary_color: Optional[str] = Field(default=None, pattern="^#[0-9A-Fa-f]{6}$")


class OrganizationResponse(BaseSchema):
    """Schema for organization response."""
    
    id: UUID
    name: str
    slug: str
    status: OrganizationStatus
    is_active: bool
    owner_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime


class OrganizationOnboard(BaseSchema):
    """Schema for organization onboarding (signup)."""
    
    # Organization info
    organization_name: str = Field(..., min_length=2, max_length=255)
    organization_slug: Optional[str] = Field(default=None, max_length=100)
    organization_type: Optional[OrganizationType] = OrganizationType.SMB
    industry: Optional[str] = None
    
    # Owner info
    owner_email: EmailStr
    owner_password: str = Field(..., min_length=8, max_length=128)
    owner_first_name: str = Field(..., min_length=1, max_length=100)
    owner_last_name: str = Field(..., min_length=1, max_length=100)
    owner_phone: Optional[str] = None
    
    # Subscription
    plan: Optional[PlanType] = PlanType.FREE
    
    # Additional
    timezone: Optional[str] = "UTC"
    currency: Optional[str] = "USD"


class OrganizationOnboardResponse(BaseSchema):
    """Response for organization onboarding."""
    
    organization: OrganizationResponse
    user_id: UUID
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class OrganizationSettingsUpdate(BaseSchema):
    """Schema for updating organization settings."""
    
    timezone: Optional[str] = None
    date_format: Optional[str] = None
    time_format: Optional[str] = None
    currency: Optional[str] = None
    language: Optional[str] = None
    features: Optional[Dict[str, Any]] = None
    notifications: Optional[Dict[str, Any]] = None
    security: Optional[Dict[str, Any]] = None


class OrganizationStats(BaseSchema):
    """Organization statistics."""
    
    total_users: int
    active_users: int
    total_teams: int
    total_leads: int
    total_contacts: int
    total_deals: int
    total_tickets: int
    storage_used_mb: int
    
    # Subscription info
    plan_name: str
    plan_limits: Dict[str, int]
    usage_percentage: Dict[str, float]


class SubscriptionUpdateRequest(BaseSchema):
    """Request to update subscription."""
    
    plan_code: str
    billing_cycle: Optional[str] = "monthly"
