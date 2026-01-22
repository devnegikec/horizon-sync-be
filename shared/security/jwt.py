"""JWT token handling utilities."""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union
from uuid import UUID

from jose import JWTError, jwt
from pydantic import BaseModel, Field, field_validator

from shared.config import settings


class TokenPayload(BaseModel):
    """JWT token payload schema."""
    sub: str  # User ID
    org_id: Optional[str] = None  # Organization ID
    role: Optional[str] = None  # Role code
    permissions: list[str] = Field(default_factory=list)
    type: str = "access"  # access or refresh
    exp: Optional[Union[datetime, int, float]] = None  # Can be datetime or Unix timestamp
    iat: Optional[Union[datetime, int, float]] = None  # Can be datetime or Unix timestamp
    jti: Optional[str] = None  # Token ID for revocation
    
    @field_validator('exp', 'iat', mode='before')
    @classmethod
    def convert_timestamp_to_datetime(cls, v):
        """Convert Unix timestamps to datetime objects."""
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return datetime.fromtimestamp(v)
        return v


def create_access_token(
    user_id: UUID,
    organization_id: Optional[UUID] = None,
    role: Optional[str] = None,
    permissions: list[str] = None,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Dict[str, Any] = None,
) -> str:
    """
    Create a new JWT access token.
    
    Args:
        user_id: User's UUID
        organization_id: Current organization context
        role: User's role code in the organization
        permissions: List of permission codes
        expires_delta: Custom expiration time
        additional_claims: Extra claims to include
    
    Returns:
        Encoded JWT token string
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    now = datetime.utcnow()
    expire = now + expires_delta
    
    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": now,
        "exp": expire,
    }
    
    if organization_id:
        payload["org_id"] = str(organization_id)
    
    if role:
        payload["role"] = role
    
    if permissions:
        payload["permissions"] = permissions
    
    if additional_claims:
        payload.update(additional_claims)
    
    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


def create_refresh_token(
    user_id: UUID,
    token_id: str,
    token_family: Optional[str] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a new JWT refresh token.
    
    Args:
        user_id: User's UUID
        token_id: Unique token ID for revocation tracking
        token_family: Token family for rotation detection
        expires_delta: Custom expiration time
    
    Returns:
        Encoded JWT refresh token string
    """
    if expires_delta is None:
        expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    now = datetime.utcnow()
    expire = now + expires_delta
    
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "jti": token_id,
        "iat": now,
        "exp": expire,
    }
    
    if token_family:
        payload["family"] = token_family
    
    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


def decode_token(token: str, verify_exp: bool = True) -> Optional[TokenPayload]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string
        verify_exp: Whether to verify expiration
    
    Returns:
        TokenPayload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_exp": verify_exp}
        )
        return TokenPayload(**payload)
    except JWTError:
        return None


def verify_token(token: str) -> bool:
    """
    Verify if a token is valid.
    
    Args:
        token: JWT token string
    
    Returns:
        True if valid, False otherwise
    """
    return decode_token(token) is not None


def extract_user_id(token: str) -> Optional[UUID]:
    """
    Extract user ID from token without full validation.
    
    Args:
        token: JWT token string
    
    Returns:
        User UUID if extractable, None otherwise
    """
    payload = decode_token(token, verify_exp=False)
    if payload:
        return UUID(payload.sub)
    return None


def extract_organization_id(token: str) -> Optional[UUID]:
    """
    Extract organization ID from token.
    
    Args:
        token: JWT token string
    
    Returns:
        Organization UUID if present, None otherwise
    """
    payload = decode_token(token, verify_exp=False)
    if payload and payload.org_id:
        return UUID(payload.org_id)
    return None
