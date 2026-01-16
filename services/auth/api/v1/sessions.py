"""Session management endpoints."""
from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_async_session
from shared.middleware.auth import get_current_user
from shared.models.auth import RefreshToken
from shared.schemas.auth import (
    SessionInfo,
    SessionListResponse,
    RevokeSessionRequest,
)
from shared.schemas.common import SuccessResponse
from shared.security.jwt import TokenPayload
from services.auth.services.auth_service import AuthService

router = APIRouter()


@router.get("", response_model=SessionListResponse)
async def list_sessions(
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    List all active sessions for the current user.
    """
    auth_service = AuthService(db)
    
    # Get all active refresh tokens for user
    sessions = await auth_service.get_user_sessions(UUID(current_user.sub))
    
    session_list = []
    for token in sessions:
        session_list.append(SessionInfo(
            id=token.id,
            device_name=token.device_name,
            device_type=token.device_type,
            browser=token.browser_info,
            os=token.os_info,
            ip_address=token.ip_address,
            last_active=token.last_used_at or token.created_at,
            created_at=token.created_at,
            is_current=str(token.id) == current_user.jti if current_user.jti else False
        ))
    
    return SessionListResponse(
        sessions=session_list,
        total=len(session_list)
    )


@router.delete("/{session_id}", response_model=SuccessResponse)
async def revoke_session(
    session_id: UUID,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Revoke a specific session (refresh token).
    """
    auth_service = AuthService(db)
    
    # Get the session
    query = select(RefreshToken).where(
        RefreshToken.id == session_id,
        RefreshToken.user_id == UUID(current_user.sub)
    )
    result = await db.execute(query)
    token = result.scalar_one_or_none()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Revoke the token
    token.revoke("user_revoked")
    await db.commit()
    
    return SuccessResponse(message="Session revoked successfully")


@router.delete("", response_model=SuccessResponse)
async def revoke_all_sessions(
    request: Request,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Revoke all sessions except the current one.
    """
    auth_service = AuthService(db)
    
    # Get current token ID from request
    current_token_jti = current_user.jti
    
    # Revoke all tokens except current
    await auth_service.revoke_all_user_tokens(
        UUID(current_user.sub),
        except_token_id=current_token_jti
    )
    
    await db.commit()
    
    return SuccessResponse(message="All other sessions revoked successfully")
