"""Organization management endpoints."""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_async_session
from shared.middleware.auth import get_current_user, require_permissions
from shared.middleware.tenant import require_tenant
from shared.models.organization import Organization, OrganizationStatus
from shared.models.subscription import Subscription, SubscriptionStatus
from shared.models.user import User, UserOrganizationRole, UserStatus
from shared.models.role import Role
from shared.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationOnboard,
    OrganizationOnboardResponse,
    OrganizationStats,
    OrganizationSettingsUpdate,
)
from shared.schemas.common import SuccessResponse, PaginatedResponse, PaginationParams
from shared.security.jwt import TokenPayload, create_access_token, create_refresh_token
from shared.security.password import hash_password
from shared.utils.helpers import generate_slug
from services.user_management.services.organization_service import OrganizationService
from services.user_management.services.user_service import UserService

router = APIRouter()


@router.post("/onboard", response_model=OrganizationOnboardResponse)
async def onboard_organization(
    request: Request,
    onboard_data: OrganizationOnboard,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Onboard a new organization with owner account.
    
    This is the main signup endpoint that:
    1. Creates the organization
    2. Creates the owner user
    3. Sets up default subscription
    4. Creates default roles
    5. Returns auth tokens
    """
    org_service = OrganizationService(db)
    user_service = UserService(db)
    
    # Check if email already exists
    existing_user = await user_service.get_user_by_email(onboard_data.owner_email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # Generate slug
    slug = onboard_data.organization_slug or generate_slug(onboard_data.organization_name)
    
    # Check if slug is taken
    existing_org = await org_service.get_organization_by_slug(slug)
    if existing_org:
        # Append random suffix
        slug = f"{slug}-{uuid4().hex[:6]}"
    
    # Create organization
    organization = await org_service.create_organization(
        name=onboard_data.organization_name,
        slug=slug,
        organization_type=onboard_data.organization_type,
        industry=onboard_data.industry,
    )
    
    # Create owner user
    owner = await user_service.create_user(
        email=onboard_data.owner_email,
        password=onboard_data.owner_password,
        first_name=onboard_data.owner_first_name,
        last_name=onboard_data.owner_last_name,
        phone=onboard_data.owner_phone,
        timezone=onboard_data.timezone,
    )
    
    # Set organization owner
    organization.owner_id = owner.id
    
    # Create default subscription (free/trial)
    subscription = await org_service.create_subscription(
        organization_id=organization.id,
        plan_code=onboard_data.plan.value if onboard_data.plan else "free",
    )
    
    # Create default roles for organization
    roles = await org_service.create_default_roles(organization.id)
    
    # Get owner role
    owner_role = next((r for r in roles if r.code == "owner"), roles[0])
    
    # Link user to organization with owner role
    user_org_role = await user_service.add_user_to_organization(
        user_id=owner.id,
        organization_id=organization.id,
        role_id=owner_role.id,
        is_primary=True,
    )
    
    # Activate organization
    organization.status = OrganizationStatus.ACTIVE
    
    # Get permissions for token
    permissions = await org_service.get_role_permissions(owner_role.id)
    
    # Create tokens
    access_token = create_access_token(
        user_id=owner.id,
        organization_id=organization.id,
        role=owner_role.code,
        permissions=permissions,
    )
    
    refresh_token = create_refresh_token(
        user_id=owner.id,
        token_id=str(uuid4()),
        token_family=str(uuid4()),
    )
    
    await db.commit()
    
    return OrganizationOnboardResponse(
        organization=OrganizationResponse.model_validate(organization),
        user_id=owner.id,
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: UUID,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Get organization details."""
    org_service = OrganizationService(db)
    
    organization = await org_service.get_organization(org_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Check access
    if current_user.org_id and UUID(current_user.org_id) != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return OrganizationResponse.model_validate(organization)


@router.patch("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: UUID,
    update_data: OrganizationUpdate,
    current_user: TokenPayload = Depends(require_permissions("organization:update")),
    db: AsyncSession = Depends(get_async_session)
):
    """Update organization details."""
    org_service = OrganizationService(db)
    
    organization = await org_service.get_organization(org_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Update fields
    organization = await org_service.update_organization(
        organization, update_data.model_dump(exclude_unset=True)
    )
    
    await db.commit()
    
    return OrganizationResponse.model_validate(organization)


@router.delete("/{org_id}", response_model=SuccessResponse)
async def delete_organization(
    org_id: UUID,
    current_user: TokenPayload = Depends(require_permissions("organization:delete")),
    db: AsyncSession = Depends(get_async_session)
):
    """Soft delete organization."""
    org_service = OrganizationService(db)
    
    organization = await org_service.get_organization(org_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Only owner can delete
    if organization.owner_id != UUID(current_user.sub):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization owner can delete the organization"
        )
    
    # Soft delete
    organization.deleted_at = datetime.utcnow()
    organization.status = OrganizationStatus.INACTIVE
    organization.is_active = False
    
    await db.commit()
    
    return SuccessResponse(message="Organization deleted successfully")


@router.get("/{org_id}/stats", response_model=OrganizationStats)
async def get_organization_stats(
    org_id: UUID,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Get organization statistics and usage."""
    org_service = OrganizationService(db)
    
    # Check access
    if current_user.org_id and UUID(current_user.org_id) != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    stats = await org_service.get_organization_stats(org_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    return stats


@router.patch("/{org_id}/settings", response_model=SuccessResponse)
async def update_organization_settings(
    org_id: UUID,
    settings_data: OrganizationSettingsUpdate,
    current_user: TokenPayload = Depends(require_permissions("setting:update")),
    db: AsyncSession = Depends(get_async_session)
):
    """Update organization settings."""
    org_service = OrganizationService(db)
    
    await org_service.update_organization_settings(
        org_id, settings_data.model_dump(exclude_unset=True)
    )
    
    await db.commit()
    
    return SuccessResponse(message="Settings updated successfully")
