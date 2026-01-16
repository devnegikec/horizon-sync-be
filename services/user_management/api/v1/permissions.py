"""Permission management endpoints."""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_async_session
from shared.middleware.auth import get_current_user
from shared.models.role import Permission, ResourceType, ActionType
from shared.schemas.role import PermissionResponse, PermissionGroupResponse
from shared.security.jwt import TokenPayload
from services.user_management.services.permission_service import PermissionService

router = APIRouter()


@router.get("", response_model=List[PermissionResponse])
async def list_permissions(
    resource: Optional[ResourceType] = Query(None, description="Filter by resource type"),
    module: Optional[str] = Query(None, description="Filter by module"),
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """List all available permissions."""
    permission_service = PermissionService(db)
    
    permissions = await permission_service.list_permissions(
        resource=resource,
        module=module,
    )
    
    return [PermissionResponse.model_validate(p) for p in permissions]


@router.get("/grouped", response_model=List[PermissionGroupResponse])
async def list_permissions_grouped(
    group_by: str = Query("resource", pattern="^(resource|module)$"),
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """List permissions grouped by resource or module."""
    permission_service = PermissionService(db)
    
    grouped = await permission_service.list_permissions_grouped(group_by)
    
    return grouped


@router.get("/resources", response_model=List[str])
async def list_resource_types():
    """List all resource types."""
    return [r.value for r in ResourceType]


@router.get("/actions", response_model=List[str])
async def list_action_types():
    """List all action types."""
    return [a.value for a in ActionType]
