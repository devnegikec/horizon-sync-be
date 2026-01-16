"""Role management endpoints."""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_async_session
from shared.middleware.auth import get_current_user, require_permissions
from shared.middleware.tenant import require_tenant
from shared.models.role import Role
from shared.schemas.role import (
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    RoleDetailResponse,
    RolePermissionUpdate,
    RoleListFilter,
    SYSTEM_ROLES,
)
from shared.schemas.common import SuccessResponse, PaginatedResponse
from shared.security.jwt import TokenPayload
from services.user_management.services.role_service import RoleService

router = APIRouter()


@router.get("", response_model=List[RoleResponse])
async def list_roles(
    include_system: bool = Query(True, description="Include system roles"),
    is_active: Optional[bool] = Query(None),
    current_user: TokenPayload = Depends(get_current_user),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """List all roles for the organization."""
    role_service = RoleService(db)
    
    roles = await role_service.list_roles(
        organization_id=tenant_id,
        include_system=include_system,
        is_active=is_active,
    )
    
    return [RoleResponse.model_validate(role) for role in roles]


@router.get("/system", response_model=List[dict])
async def list_system_roles():
    """List system role definitions."""
    return [role.model_dump() for role in SYSTEM_ROLES]


@router.post("", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreate,
    current_user: TokenPayload = Depends(require_permissions("role:create")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new custom role."""
    role_service = RoleService(db)
    
    # Check if code already exists
    existing = await role_service.get_role_by_code(tenant_id, role_data.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Role with code '{role_data.code}' already exists"
        )
    
    # Create role
    role = await role_service.create_role(
        organization_id=tenant_id,
        name=role_data.name,
        code=role_data.code,
        description=role_data.description,
        is_default=role_data.is_default,
        hierarchy_level=role_data.hierarchy_level,
    )
    
    # Assign permissions if provided
    if role_data.permission_ids:
        await role_service.set_role_permissions(role.id, role_data.permission_ids)
    
    await db.commit()
    
    return RoleResponse.model_validate(role)


@router.get("/{role_id}", response_model=RoleDetailResponse)
async def get_role(
    role_id: UUID,
    current_user: TokenPayload = Depends(get_current_user),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Get role details with permissions."""
    role_service = RoleService(db)
    
    role = await role_service.get_role_with_permissions(role_id, tenant_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Get user count
    user_count = await role_service.get_role_user_count(role_id, tenant_id)
    
    response = RoleDetailResponse.model_validate(role)
    response.user_count = user_count
    
    return response


@router.patch("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: UUID,
    update_data: RoleUpdate,
    current_user: TokenPayload = Depends(require_permissions("role:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Update a role."""
    role_service = RoleService(db)
    
    role = await role_service.get_role(role_id, tenant_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Can't update system roles
    if role.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify system roles"
        )
    
    # Update role
    updated_role = await role_service.update_role(
        role, update_data.model_dump(exclude_unset=True)
    )
    
    await db.commit()
    
    return RoleResponse.model_validate(updated_role)


@router.delete("/{role_id}", response_model=SuccessResponse)
async def delete_role(
    role_id: UUID,
    current_user: TokenPayload = Depends(require_permissions("role:delete")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Delete a custom role."""
    role_service = RoleService(db)
    
    role = await role_service.get_role(role_id, tenant_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Can't delete system roles
    if role.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete system roles"
        )
    
    # Check if role has users
    user_count = await role_service.get_role_user_count(role_id, tenant_id)
    if user_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete role with {user_count} assigned users. Reassign users first."
        )
    
    # Delete role
    await role_service.delete_role(role)
    
    await db.commit()
    
    return SuccessResponse(message="Role deleted successfully")


@router.put("/{role_id}/permissions", response_model=SuccessResponse)
async def update_role_permissions(
    role_id: UUID,
    permissions_data: RolePermissionUpdate,
    current_user: TokenPayload = Depends(require_permissions("role:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Update permissions for a role."""
    role_service = RoleService(db)
    
    role = await role_service.get_role(role_id, tenant_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Can't update system roles
    if role.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify system role permissions"
        )
    
    # Update permissions
    await role_service.set_role_permissions(role_id, permissions_data.permission_ids)
    
    await db.commit()
    
    return SuccessResponse(message="Role permissions updated successfully")
