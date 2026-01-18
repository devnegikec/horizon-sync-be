"""Role business logic service."""
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from shared.models.role import Role, Permission, RolePermission
from shared.models.user import User, UserRole


class RoleService:
    """Service for role operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def list_roles(
        self,
        organization_id: UUID,
        include_system: bool = True,
        is_active: Optional[bool] = None,
    ) -> List[Role]:
        """List roles for an organization."""
        # Custom roles for this org
        conditions = [
            Role.organization_id == organization_id
        ]
        
        if include_system:
            # Join with system roles
            conditions = [
                (Role.organization_id == organization_id) |
                (Role.is_system == True)
            ]
        
        query = select(Role).where(*conditions)
        
        if is_active is not None:
            query = query.where(Role.is_active == is_active)
        
        query = query.order_by(Role.hierarchy_level.desc(), Role.name)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_role(
        self,
        role_id: UUID,
        organization_id: UUID
    ) -> Optional[Role]:
        """Get a role by ID."""
        query = select(Role).where(
            Role.id == role_id,
            (Role.organization_id == organization_id) | (Role.is_system == True)
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_role_by_code(
        self,
        organization_id: UUID,
        code: str
    ) -> Optional[Role]:
        """Get a role by code."""
        query = select(Role).where(
            Role.code == code,
            (Role.organization_id == organization_id) | (Role.is_system == True)
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_role_with_permissions(
        self,
        role_id: UUID,
        organization_id: UUID
    ) -> Optional[Role]:
        """Get role with permissions loaded."""
        query = select(Role).options(
            selectinload(Role.role_permissions).selectinload(RolePermission.permission)
        ).where(
            Role.id == role_id,
            (Role.organization_id == organization_id) | (Role.is_system == True)
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_role(
        self,
        organization_id: UUID,
        name: str,
        code: str,
        description: Optional[str] = None,
        is_default: bool = False,
        hierarchy_level: int = 0,
    ) -> Role:
        """Create a new custom role."""
        role = Role(
            organization_id=organization_id,
            name=name,
            code=code,
            description=description,
            is_system=False,
            is_default=is_default,
            hierarchy_level=hierarchy_level,
        )
        
        self.db.add(role)
        await self.db.flush()
        
        return role
    
    async def update_role(self, role: Role, data: Dict[str, Any]) -> Role:
        """Update role fields."""
        for key, value in data.items():
            if hasattr(role, key) and value is not None:
                setattr(role, key, value)
        
        await self.db.flush()
        return role
    
    async def delete_role(self, role: Role) -> None:
        """Delete a role."""
        # Delete role permissions first
        await self.db.execute(
            delete(RolePermission).where(RolePermission.role_id == role.id)
        )
        
        # Delete role
        await self.db.delete(role)
        await self.db.flush()
    
    async def set_role_permissions(
        self,
        role_id: UUID,
        permission_ids: List[UUID]
    ) -> None:
        """Set permissions for a role (replaces existing)."""
        # Delete existing
        await self.db.execute(
            delete(RolePermission).where(RolePermission.role_id == role_id)
        )
        
        # Add new
        for perm_id in permission_ids:
            role_perm = RolePermission(
                role_id=role_id,
                permission_id=perm_id
            )
            self.db.add(role_perm)
        
        await self.db.flush()
    
    async def get_role_user_count(
        self,
        role_id: UUID,
        organization_id: UUID
    ) -> int:
        """Get number of users with this role in the organization."""
        query = select(func.count()).select_from(UserRole).join(User).where(
            UserRole.role_id == role_id,
            User.organization_id == organization_id,
            User.is_active == True
        )
        
        result = await self.db.execute(query)
        return result.scalar() or 0
