"""Authentication endpoints."""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from shared.config import settings
from shared.database import get_async_session
from shared.models.user import User, UserOrganizationRole, UserStatus
from shared.models.auth import RefreshToken, PasswordReset
from shared.models.role import Role
from shared.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    RefreshRequest,
    RefreshResponse,
    LogoutRequest,
    PasswordResetRequest,
    PasswordResetResponse,
    PasswordResetConfirm,
    VerifyEmailRequest,
)
from shared.schemas.common import SuccessResponse
from shared.security.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from shared.security.password import hash_password, verify_password, generate_token
from shared.middleware.auth import get_current_user
from shared.security.jwt import TokenPayload
from services.auth.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    register_data: RegisterRequest,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Register a new user and create their organization.
    
    - Checks if email is already registered
    - Creates user account
    - Creates initial organization
    - Assigns owner role
    """
    auth_service = AuthService(db)
    
    # Check if user already exists
    existing_user = await auth_service.get_user_by_email(register_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Register user and organization
    user, organization = await auth_service.register_user(
        email=register_data.email,
        password=register_data.password,
        first_name=register_data.first_name,
        last_name=register_data.last_name,
        organization_name=register_data.organization_name
    )
    
    await db.commit()
    
    return RegisterResponse(
        user_id=user.id,
        email=user.email,
        organization_id=organization.id,
        message="Account created successfully. You can now login."
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Authenticate user and return access/refresh tokens.
    
    - Validates credentials
    - Checks account status
    - Handles MFA if enabled
    - Creates session and tokens
    """
    auth_service = AuthService(db)
    
    # Get user by email
    user = await auth_service.get_user_by_email(login_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if account is locked
    if user.is_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is temporarily locked. Please try again later."
        )
    
    # Verify password
    if not verify_password(login_data.password, user.password_hash):
        await auth_service.record_failed_login(user)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check account status
    if user.status == UserStatus.SUSPENDED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been suspended"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Check MFA
    if user.mfa_enabled:
        if not login_data.mfa_code:
            return LoginResponse(
                access_token="",
                refresh_token="",
                expires_in=0,
                user_id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                mfa_required=True,
                mfa_pending=True
            )
        
        # Verify MFA code
        if not await auth_service.verify_mfa_code(user, login_data.mfa_code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid MFA code"
            )
    
    # Get organization context
    org_id = None
    role_code = None
    permissions = []
    org_name = None
    
    # If no org specified, get primary or first org
    user_org_role = await auth_service.get_user_organization_context(user.id, org_id)
    
    if user_org_role:
        org_id = user_org_role.organization_id
        org_name = user_org_role.organization.name if user_org_role.organization else None
        if user_org_role.role:
            role_code = user_org_role.role.code
            permissions = await auth_service.get_role_permissions(user_org_role.role_id)
    
    # Create tokens
    token_id = str(uuid4())
    token_family = str(uuid4())
    
    access_token = create_access_token(
        user_id=user.id,
        organization_id=org_id,
        role=role_code,
        permissions=permissions,
    )
    
    refresh_token_str = create_refresh_token(
        user_id=user.id,
        token_id=token_id,
        token_family=token_family,
    )
    
    # Store refresh token
    await auth_service.store_refresh_token(
        user_id=user.id,
        token_id=token_id,
        token_hash=hash_password(refresh_token_str),
        token_family=token_family,
        device_info=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    
    # Update last login
    await auth_service.update_last_login(user, request.client.host if request.client else None)
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        organization_id=org_id,
        organization_name=org_name,
        role=role_code,
        permissions=permissions,
    )


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(
    refresh_data: RefreshRequest,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Refresh access token using refresh token.
    Implements token rotation for security.
    """
    auth_service = AuthService(db)
    
    # Decode refresh token
    payload = decode_token(refresh_data.refresh_token)
    if not payload or payload.type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Verify token exists and is valid
    stored_token = await auth_service.get_refresh_token(payload.jti)
    if not stored_token or not stored_token.is_valid:
        # Possible token reuse - revoke all tokens in family
        if stored_token:
            await auth_service.revoke_token_family(stored_token.token_family)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Get user
    user = await auth_service.get_user_by_id(UUID(payload.sub))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Revoke old token
    stored_token.revoke("rotated")
    
    # Get current organization context (same as original)
    user_org_role = await auth_service.get_user_organization_context(user.id)
    
    org_id = None
    role_code = None
    permissions = []
    
    if user_org_role:
        org_id = user_org_role.organization_id
        if user_org_role.role:
            role_code = user_org_role.role.code
            permissions = await auth_service.get_role_permissions(user_org_role.role_id)
    
    # Create new tokens
    new_token_id = str(uuid4())
    
    new_access_token = create_access_token(
        user_id=user.id,
        organization_id=org_id,
        role=role_code,
        permissions=permissions,
    )
    
    new_refresh_token = create_refresh_token(
        user_id=user.id,
        token_id=new_token_id,
        token_family=stored_token.token_family,
    )
    
    # Store new refresh token
    await auth_service.store_refresh_token(
        user_id=user.id,
        token_id=new_token_id,
        token_hash=hash_password(new_refresh_token),
        token_family=stored_token.token_family,
        device_info=stored_token.device_name,
        ip_address=stored_token.ip_address,
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    
    await db.commit()
    
    return RefreshResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/logout", response_model=SuccessResponse)
async def logout(
    logout_data: LogoutRequest,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Logout user - revoke refresh token(s).
    """
    auth_service = AuthService(db)
    
    if logout_data.all_devices:
        # Revoke all refresh tokens for user
        await auth_service.revoke_all_user_tokens(UUID(current_user.sub))
        message = "Logged out from all devices"
    elif logout_data.refresh_token:
        # Revoke specific refresh token
        payload = decode_token(logout_data.refresh_token, verify_exp=False)
        if payload and payload.jti:
            await auth_service.revoke_token(payload.jti)
        message = "Logged out successfully"
    else:
        message = "Logged out successfully"
    
    await db.commit()
    
    return SuccessResponse(message=message)


@router.post("/forgot-password", response_model=PasswordResetResponse)
async def forgot_password(
    request: Request,
    reset_data: PasswordResetRequest,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Request password reset email.
    Always returns success to prevent email enumeration.
    """
    auth_service = AuthService(db)
    
    user = await auth_service.get_user_by_email(reset_data.email)
    
    if user and user.is_active:
        # Generate reset token
        token = generate_token(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        # Store reset token
        await auth_service.create_password_reset(
            user_id=user.id,
            token_hash=hash_password(token),
            expires_at=expires_at,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        await db.commit()
        
        # TODO: Send email with reset link
        # The reset link should be: {frontend_url}/reset-password?token={token}
    
    # Always return success to prevent email enumeration
    return PasswordResetResponse(
        message="If an account exists with this email, a reset link will be sent",
        expires_in=3600
    )


@router.post("/reset-password", response_model=SuccessResponse)
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Reset password using token from email.
    """
    auth_service = AuthService(db)
    
    # Find valid reset token
    reset_token = await auth_service.find_valid_password_reset(reset_data.token)
    
    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Get user
    user = await auth_service.get_user_by_id(reset_token.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )
    
    # Update password
    user.password_hash = hash_password(reset_data.new_password)
    reset_token.used_at = datetime.utcnow()
    
    # Revoke all refresh tokens (force re-login)
    await auth_service.revoke_all_user_tokens(user.id)
    
    await db.commit()
    
    return SuccessResponse(message="Password reset successfully. Please login with your new password.")


@router.post("/verify-email", response_model=SuccessResponse)
async def verify_email(
    verify_data: VerifyEmailRequest,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Verify email address using token from email.
    """
    auth_service = AuthService(db)
    
    # Find valid verification token
    verification = await auth_service.find_valid_email_verification(verify_data.token)
    
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    # Get user
    user = await auth_service.get_user_by_id(verification.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )
    
    # Mark email as verified
    user.email_verified = True
    user.email_verified_at = datetime.utcnow()
    if user.status == UserStatus.PENDING_VERIFICATION:
        user.status = UserStatus.ACTIVE
    
    verification.verified_at = datetime.utcnow()
    
    await db.commit()
    
    return SuccessResponse(message="Email verified successfully")
