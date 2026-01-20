"""User management endpoints."""
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_async_session
from shared.middleware.auth import get_current_user, get_current_user_context, require_permissions, CurrentUser
from shared.middleware.tenant import require_tenant
from shared.models.user import User, UserOrganizationRole, UserStatus
from shared.models.auth import Invitation, InvitationStatus
from shared.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserInvite,
    UserInviteResponse,
    UserAcceptInvitation,
    UserMe,
    UserRoleUpdate,
    UserListFilter,
)
from shared.schemas.common import SuccessResponse, PaginatedResponse, PaginationParams
from shared.security.jwt import TokenPayload
from shared.security.password import hash_password, generate_token
from services.user_management.services.user_service import UserService
from services.user_management.config import user_management_settings

router = APIRouter()


@router.get("/me", response_model=UserMe)
async def get_current_user_profile(
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Get current user's profile with organization context."""
    user_service = UserService(db)
    
    user = await user_service.get_user_by_id(UUID(current_user.sub))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get all organizations for user
    organizations = await user_service.get_user_organizations(user.id)
    
    # Get current organization context
    current_org = None
    current_role = None
    teams = []
    
    if current_user.org_id:
        org_id = UUID(current_user.org_id)
        for org_info in organizations:
            if org_info["organization_id"] == org_id:
                current_org = org_info
                break
        
        # Get teams in current org
        teams = await user_service.get_user_teams(user.id, org_id)
    
    return UserMe(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        display_name=user.display_name,
        phone=user.phone,
        avatar_url=user.avatar_url,
        user_type=user.user_type,
        status=user.status,
        is_active=user.is_active,
        email_verified=user.email_verified,
        mfa_enabled=user.mfa_enabled,
        timezone=user.timezone,
        language=user.language,
        preferences=user.preferences or {},
        last_login_at=user.last_login_at,
        created_at=user.created_at,
        organization_id=UUID(current_user.org_id) if current_user.org_id else None,
        organization_name=current_org["organization_name"] if current_org else None,
        role_id=UUID(current_org["role_id"]) if current_org and current_org.get("role_id") else None,
        role_name=current_org["role_name"] if current_org else None,
        permissions=current_user.permissions,
        teams=teams,
        organizations=organizations,
    )


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    update_data: UserUpdate,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Update current user's profile."""
    user_service = UserService(db)
    
    user = await user_service.get_user_by_id(UUID(current_user.sub))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user
    updated_user = await user_service.update_user(
        user, update_data.model_dump(exclude_unset=True)
    )
    
    await db.commit()
    
    return UserResponse.model_validate(updated_user)


@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[UserStatus] = None,
    role_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
    current_user: TokenPayload = Depends(require_permissions("user:list")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """List users in the current organization."""
    user_service = UserService(db)
    
    filters = UserListFilter(
        search=search,
        status=status,
        role_id=role_id,
        is_active=is_active,
    )
    
    result = await user_service.list_organization_users(
        organization_id=tenant_id,
        page=page,
        page_size=page_size,
        filters=filters,
    )
    
    return result


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: TokenPayload = Depends(require_permissions("user:read")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Get user details."""
    user_service = UserService(db)
    
    # Check user is in same organization
    user = await user_service.get_organization_user(tenant_id, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.model_validate(user)


@router.post("/invite", response_model=UserInviteResponse)
async def invite_user(
    invite_data: UserInvite,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user_context),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Invite a user to join the organization."""
    current_user.require_permission("user:create")
    
    user_service = UserService(db)
    
    # Check if user already in org
    existing = await user_service.get_user_by_email(invite_data.email)
    if existing:
        # Check if already in this org
        org_role = await user_service.get_user_organization_role(
            existing.id, tenant_id
        )
        if org_role:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User is already a member of this organization"
            )
    
    # Check for pending invitation
    pending = await user_service.get_pending_invitation(tenant_id, invite_data.email)
    if pending:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An invitation is already pending for this email"
        )
    
    # Generate invitation token
    token = generate_token(32)
    expires_at = datetime.utcnow() + timedelta(days=user_management_settings.INVITATION_EXPIRE_DAYS)
    
    # Create invitation
    invitation = await user_service.create_invitation(
        organization_id=tenant_id,
        email=invite_data.email,
        first_name=invite_data.first_name,
        last_name=invite_data.last_name,
        role_id=invite_data.role_id,
        team_ids=invite_data.team_ids,
        invited_by_id=current_user.user_id,
        token_hash=hash_password(token),
        expires_at=expires_at,
        message=invite_data.message,
    )
    
    await db.commit()
    
    # TODO: Send invitation email
    invitation_url = f"https://app.horizonsync.com/accept-invitation?token={token}"
    
    return UserInviteResponse(
        invitation_id=invitation.id,
        email=invitation.email,
        expires_at=invitation.expires_at,
        invitation_url=invitation_url,
    )


@router.post("/accept-invitation", response_model=SuccessResponse)
async def accept_invitation(
    accept_data: UserAcceptInvitation,
    db: AsyncSession = Depends(get_async_session)
):
    """Accept an invitation to join an organization."""
    user_service = UserService(db)
    
    # Find valid invitation
    invitation = await user_service.find_valid_invitation(accept_data.token)
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired invitation"
        )
    
    # Check if email already registered
    existing_user = await user_service.get_user_by_email(invitation.email)
    
    if existing_user:
        # Add to organization
        user = existing_user
    else:
        # Create new user
        user = await user_service.create_user(
            email=invitation.email,
            password=accept_data.password,
            organization_id=invitation.organization_id,
            first_name=accept_data.first_name or invitation.first_name,
            last_name=accept_data.last_name or invitation.last_name,
        )
        user.email_verified = True
        user.email_verified_at = datetime.utcnow()
        user.status = UserStatus.ACTIVE
    
    # Add user to organization with role
    await user_service.add_user_to_organization(
        user_id=user.id,
        organization_id=invitation.organization_id,
        role_id=invitation.role_id,
    )
    
    # Add to teams if specified
    if invitation.team_ids:
        for team_id in invitation.team_ids:
            await user_service.add_user_to_team(user.id, team_id)
    
    # Mark invitation as accepted
    invitation.accept(user.id)
    
    await db.commit()
    
    return SuccessResponse(message="Invitation accepted successfully. You can now login.")


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    update_data: UserUpdate,
    current_user: TokenPayload = Depends(require_permissions("user:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Update a user in the organization."""
    user_service = UserService(db)
    
    # Get user in organization
    user = await user_service.get_organization_user(tenant_id, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user
    updated_user = await user_service.update_user(
        user, update_data.model_dump(exclude_unset=True)
    )
    
    await db.commit()
    
    return UserResponse.model_validate(updated_user)


@router.delete("/{user_id}", response_model=SuccessResponse)
async def deactivate_user(
    user_id: UUID,
    current_user: TokenPayload = Depends(require_permissions("user:delete")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Deactivate/remove a user from the organization."""
    user_service = UserService(db)
    
    # Can't remove yourself
    if user_id == UUID(current_user.sub):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove yourself from the organization"
        )
    
    # Get user's org role
    org_role = await user_service.get_user_organization_role(user_id, tenant_id)
    if not org_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in organization"
        )
    
    # Deactivate membership
    org_role.is_active = False
    org_role.status = "removed"
    
    await db.commit()
    
    return SuccessResponse(message="User removed from organization")


@router.put("/{user_id}/roles", response_model=SuccessResponse)
async def update_user_role(
    user_id: UUID,
    role_data: UserRoleUpdate,
    current_user: TokenPayload = Depends(require_permissions("user:update", "role:assign")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Update a user's role in the organization."""
    user_service = UserService(db)
    
    # Get user's org role
    org_role = await user_service.get_user_organization_role(user_id, tenant_id)
    if not org_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in organization"
        )
    
    # Update role
    org_role.role_id = role_data.role_id
    
    await db.commit()
    
    return SuccessResponse(message="User role updated successfully")
