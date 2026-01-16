"""User Pydantic schemas."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import EmailStr, Field, field_validator

from shared.models.user import UserStatus, UserType
from shared.schemas.common import BaseSchema


class UserBase(BaseSchema):
    """Base user schema."""
    
    email: EmailStr
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    display_name: Optional[str] = Field(default=None, max_length=200)
    phone: Optional[str] = Field(default=None, max_length=50)


class UserCreate(UserBase):
    """Schema for creating a user."""
    
    password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseSchema):
    """Schema for updating a user."""
    
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    display_name: Optional[str] = Field(default=None, max_length=200)
    phone: Optional[str] = Field(default=None, max_length=50)
    avatar_url: Optional[str] = Field(default=None, max_length=500)
    timezone: Optional[str] = None
    language: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class UserResponse(BaseSchema):
    """Schema for user response."""
    
    id: UUID
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    user_type: UserType
    status: UserStatus
    is_active: bool
    email_verified: bool
    mfa_enabled: bool
    timezone: str
    language: str
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.display_name:
            return self.display_name
        return self.email.split("@")[0]


class UserInvite(BaseSchema):
    """Schema for inviting a user to an organization."""
    
    email: EmailStr
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    role_id: Optional[UUID] = None
    team_ids: Optional[List[UUID]] = None
    message: Optional[str] = Field(default=None, max_length=500)


class UserInviteResponse(BaseSchema):
    """Response for user invitation."""
    
    invitation_id: UUID
    email: str
    expires_at: datetime
    invitation_url: str


class UserAcceptInvitation(BaseSchema):
    """Schema for accepting an invitation."""
    
    token: str
    password: str = Field(..., min_length=8, max_length=128)
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)


class UserMe(BaseSchema):
    """Current user profile with organization context."""
    
    id: UUID
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    user_type: UserType
    status: UserStatus
    is_active: bool
    email_verified: bool
    mfa_enabled: bool
    timezone: str
    language: str
    preferences: Dict[str, Any]
    last_login_at: Optional[datetime] = None
    created_at: datetime
    
    # Current organization context
    organization_id: Optional[UUID] = None
    organization_name: Optional[str] = None
    role_id: Optional[UUID] = None
    role_name: Optional[str] = None
    permissions: List[str] = []
    teams: List[Dict[str, Any]] = []
    
    # All organizations user belongs to
    organizations: List[Dict[str, Any]] = []


class UserOrganizationRoleUpdate(BaseSchema):
    """Schema for updating user's role in organization."""
    
    role_id: UUID


class UserOrganizationResponse(BaseSchema):
    """User's membership in an organization."""
    
    user_id: UUID
    organization_id: UUID
    organization_name: str
    role_id: Optional[UUID] = None
    role_name: Optional[str] = None
    is_primary: bool
    is_active: bool
    joined_at: Optional[datetime] = None


class UserListFilter(BaseSchema):
    """Filter parameters for listing users."""
    
    search: Optional[str] = None
    status: Optional[UserStatus] = None
    role_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    email_verified: Optional[bool] = None


class PasswordChangeRequest(BaseSchema):
    """Request to change password."""
    
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class UserBulkAction(BaseSchema):
    """Bulk action on users."""
    
    user_ids: List[UUID]
    action: str  # activate, deactivate, delete


class UserActivityResponse(BaseSchema):
    """User activity summary."""
    
    user_id: UUID
    total_logins: int
    last_login_at: Optional[datetime] = None
    total_actions: int
    recent_actions: List[Dict[str, Any]]
