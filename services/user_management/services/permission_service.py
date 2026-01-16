"""Permission business logic service."""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models.role import Permission, ResourceType, ActionType
from shared.schemas.role import PermissionResponse, PermissionGroupResponse


class PermissionService:
    """Service for permission operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def list_permissions(
        self,
        resource: Optional[ResourceType] = None,
        module: Optional[str] = None,
    ) -> List[Permission]:
        """List all permissions with optional filtering."""
        query = select(Permission).where(Permission.is_active == True)
        
        if resource:
            query = query.where(Permission.resource == resource)
        
        if module:
            query = query.where(Permission.module == module)
        
        query = query.order_by(Permission.resource, Permission.action)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def list_permissions_grouped(
        self,
        group_by: str = "resource"
    ) -> List[PermissionGroupResponse]:
        """List permissions grouped by resource or module."""
        permissions = await self.list_permissions()
        
        groups = {}
        for perm in permissions:
            key = perm.resource.value if group_by == "resource" else perm.module
            if key not in groups:
                groups[key] = []
            groups[key].append(PermissionResponse.model_validate(perm))
        
        return [
            PermissionGroupResponse(
                resource=key,
                permissions=perms
            )
            for key, perms in groups.items()
        ]
    
    async def get_permission_by_code(self, code: str) -> Optional[Permission]:
        """Get permission by code."""
        query = select(Permission).where(Permission.code == code)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
