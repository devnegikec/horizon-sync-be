"""MFA (Multi-Factor Authentication) endpoints."""
import io
from typing import List
from uuid import UUID

import pyotp
import qrcode
import qrcode.image.svg
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_async_session
from shared.middleware.auth import get_current_user
from shared.schemas.auth import (
    MFAEnableRequest,
    MFAEnableResponse,
    MFAVerifyRequest,
    MFADisableRequest,
)
from shared.schemas.common import SuccessResponse
from shared.security.jwt import TokenPayload
from shared.security.password import verify_password, generate_random_password
from services.auth.config import auth_settings
from services.auth.services.auth_service import AuthService

router = APIRouter()


@router.post("/enable", response_model=MFAEnableResponse)
async def enable_mfa(
    mfa_data: MFAEnableRequest,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Enable MFA for the current user.
    Returns the secret and QR code for authenticator app setup.
    """
    auth_service = AuthService(db)
    
    # Get user
    user = await auth_service.get_user_by_id(UUID(current_user.sub))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify password
    if not verify_password(mfa_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    # Check if MFA is already enabled
    if user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is already enabled"
        )
    
    # Generate secret
    secret = pyotp.random_base32()
    
    # Generate provisioning URI for authenticator app
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=user.email,
        issuer_name=auth_settings.MFA_ISSUER
    )
    
    # Generate QR code as data URL
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    
    # Create SVG image
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    import base64
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    qr_code_url = f"data:image/png;base64,{qr_code_base64}"
    
    # Generate backup codes
    backup_codes = [generate_random_password(8, include_special=False) for _ in range(10)]
    
    # Store secret and backup codes (not yet enabled)
    user.mfa_secret = secret
    user.mfa_backup_codes = backup_codes
    
    await db.commit()
    
    return MFAEnableResponse(
        secret=secret,
        qr_code_url=qr_code_url,
        backup_codes=backup_codes
    )


@router.post("/verify", response_model=SuccessResponse)
async def verify_mfa_setup(
    verify_data: MFAVerifyRequest,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Verify MFA setup by confirming the first code.
    This completes the MFA enablement process.
    """
    auth_service = AuthService(db)
    
    # Get user
    user = await auth_service.get_user_by_id(UUID(current_user.sub))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if secret exists (setup started)
    if not user.mfa_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA setup not started. Please call /enable first."
        )
    
    # Verify code
    totp = pyotp.TOTP(user.mfa_secret)
    if not totp.verify(verify_data.code, valid_window=1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
    
    # Enable MFA
    user.mfa_enabled = True
    
    await db.commit()
    
    return SuccessResponse(message="MFA enabled successfully")


@router.post("/disable", response_model=SuccessResponse)
async def disable_mfa(
    disable_data: MFADisableRequest,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Disable MFA for the current user.
    Requires password and current MFA code.
    """
    auth_service = AuthService(db)
    
    # Get user
    user = await auth_service.get_user_by_id(UUID(current_user.sub))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if MFA is enabled
    if not user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is not enabled"
        )
    
    # Verify password
    if not verify_password(disable_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    # Verify MFA code
    totp = pyotp.TOTP(user.mfa_secret)
    if not totp.verify(disable_data.code, valid_window=1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MFA code"
        )
    
    # Disable MFA
    user.mfa_enabled = False
    user.mfa_secret = None
    user.mfa_backup_codes = None
    
    await db.commit()
    
    return SuccessResponse(message="MFA disabled successfully")


@router.get("/backup-codes", response_model=List[str])
async def get_backup_codes(
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get current backup codes.
    For security, this should only show remaining unused codes.
    """
    auth_service = AuthService(db)
    
    # Get user
    user = await auth_service.get_user_by_id(UUID(current_user.sub))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.mfa_enabled or not user.mfa_backup_codes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is not enabled"
        )
    
    return user.mfa_backup_codes


@router.post("/backup-codes/regenerate", response_model=List[str])
async def regenerate_backup_codes(
    verify_data: MFAVerifyRequest,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Regenerate backup codes.
    Requires current MFA code to confirm.
    """
    auth_service = AuthService(db)
    
    # Get user
    user = await auth_service.get_user_by_id(UUID(current_user.sub))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is not enabled"
        )
    
    # Verify MFA code
    totp = pyotp.TOTP(user.mfa_secret)
    if not totp.verify(verify_data.code, valid_window=1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MFA code"
        )
    
    # Generate new backup codes
    backup_codes = [generate_random_password(8, include_special=False) for _ in range(10)]
    user.mfa_backup_codes = backup_codes
    
    await db.commit()
    
    return backup_codes
