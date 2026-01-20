from uuid import UUID
from fastapi import Request, HTTPException, status, Depends
from shared.middleware.auth import get_current_user
from shared.security.jwt import TokenPayload

async def get_current_user_id(
    current_user: TokenPayload = Depends(get_current_user)
) -> UUID:
    """Dependency to get current user ID."""
    return UUID(current_user.sub)

async def get_current_org_id(
    current_user: TokenPayload = Depends(get_current_user)
) -> UUID:
    """Dependency to get current organization ID."""
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization context required"
        )
    return UUID(current_user.org_id)
