"""Authentication Pydantic schemas."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import EmailStr, Field, field_validator

from shared.schemas.common import BaseSchema


class LoginRequest(BaseSchema):
    """Login request schema."""
    
    email: EmailStr
    password: str = Field(..., min_length=1)
    remember_me: bool = False
    mfa_code: Optional[str] = None


class RegisterRequest(BaseSchema):
    """User registration request schema."""
    
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    organization_name: str = Field(..., min_length=1, max_length=255)


class RegisterResponse(BaseSchema):
    """User registration response schema."""
    
    user_id: UUID
    email: str
    organization_id: UUID
    message: str = "User registered successfully"


class LoginResponse(BaseSchema):
    """Login response schema."""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Seconds until access token expires
    
    # User info
    user_id: UUID
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    # Organization context
    organization_name: Optional[str] = None
    role: Optional[str] = None
    permissions: List[str] = []
    
    # MFA
    mfa_required: bool = False
    mfa_pending: bool = False


class TokenResponse(BaseSchema):
    """Token response schema."""
    
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshRequest(BaseSchema):
    """Token refresh request schema."""
    
    refresh_token: str


class RefreshResponse(BaseSchema):
    """Token refresh response schema."""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class LogoutRequest(BaseSchema):
    """Logout request schema."""
    
    refresh_token: Optional[str] = None
    all_devices: bool = False


class PasswordResetRequest(BaseSchema):
    """Password reset request schema."""
    
    email: EmailStr


class PasswordResetResponse(BaseSchema):
    """Password reset response schema."""
    
    message: str = "If an account exists with this email, a reset link will be sent"
    expires_in: int = 3600  # 1 hour
    token: Optional[str] = None


class PasswordResetConfirm(BaseSchema):
    """Password reset confirmation schema."""
    
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator('new_password')
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


class VerifyEmailRequest(BaseSchema):
    """Email verification request schema."""
    
    token: str


class ResendVerificationRequest(BaseSchema):
    """Resend verification email request schema."""
    
    email: EmailStr


class MFAEnableRequest(BaseSchema):
    """MFA enable request schema."""
    
    password: str  # Require password to enable MFA


class MFAEnableResponse(BaseSchema):
    """MFA enable response schema."""
    
    secret: str
    qr_code_url: str
    backup_codes: List[str]


class MFAVerifyRequest(BaseSchema):
    """MFA verification request schema."""
    
    code: str = Field(..., min_length=6, max_length=6)


class MFADisableRequest(BaseSchema):
    """MFA disable request schema."""
    
    password: str
    code: str  # MFA code to confirm


class SessionInfo(BaseSchema):
    """Active session information."""
    
    id: UUID
    device_name: Optional[str] = None
    device_type: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    ip_address: Optional[str] = None
    location: Optional[str] = None
    last_active: datetime
    created_at: datetime
    is_current: bool = False


class SessionListResponse(BaseSchema):
    """List of active sessions."""
    
    sessions: List[SessionInfo]
    total: int


class RevokeSessionRequest(BaseSchema):
    """Request to revoke a session."""
    
    session_id: UUID


class SwitchOrganizationRequest(BaseSchema):
    """Request to switch current organization context."""
    
    organization_id: UUID


class SwitchOrganizationResponse(BaseSchema):
    """Response after switching organization."""
    
    access_token: str
    organization_id: UUID
    organization_name: str
    role: str
    permissions: List[str]
