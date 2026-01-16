"""Role and Permission Pydantic schemas."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field

from shared.models.role import ActionType, ResourceType
from shared.schemas.common import BaseSchema


class PermissionBase(BaseSchema):
    """Base permission schema."""
    
    code: str = Field(..., max_length=100)
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    resource: ResourceType
    action: ActionType
    module: Optional[str] = None
    category: Optional[str] = None


class PermissionResponse(PermissionBase):
    """Schema for permission response."""
    
    id: UUID
    is_active: bool


class PermissionGroupResponse(BaseSchema):
    """Permissions grouped by resource or module."""
    
    resource: str
    permissions: List[PermissionResponse]


class RoleBase(BaseSchema):
    """Base role schema."""
    
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=50, pattern="^[a-z0-9_]+$")
    description: Optional[str] = None


class RoleCreate(RoleBase):
    """Schema for creating a role."""
    
    permission_ids: Optional[List[UUID]] = None
    is_default: Optional[bool] = False
    hierarchy_level: Optional[int] = 0


class RoleUpdate(BaseSchema):
    """Schema for updating a role."""
    
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    description: Optional[str] = None
    is_default: Optional[bool] = None
    hierarchy_level: Optional[int] = None
    is_active: Optional[bool] = None


class RoleResponse(RoleBase):
    """Schema for role response."""
    
    id: UUID
    organization_id: Optional[UUID] = None
    is_system: bool
    is_default: bool
    is_active: bool
    hierarchy_level: int
    created_at: datetime
    updated_at: datetime
    
    # Permissions (optionally included)
    permissions: Optional[List[PermissionResponse]] = None
    permission_count: Optional[int] = None


class RoleDetailResponse(RoleResponse):
    """Detailed role response with permissions."""
    
    permissions: List[PermissionResponse]
    user_count: int = 0


class RolePermissionUpdate(BaseSchema):
    """Schema for updating role permissions."""
    
    permission_ids: List[UUID]


class RoleAssignment(BaseSchema):
    """Schema for assigning a role to a user."""
    
    user_id: UUID
    role_id: UUID


class RoleBulkAssignment(BaseSchema):
    """Schema for bulk role assignment."""
    
    user_ids: List[UUID]
    role_id: UUID


class RoleListFilter(BaseSchema):
    """Filter parameters for listing roles."""
    
    search: Optional[str] = None
    is_system: Optional[bool] = None
    is_active: Optional[bool] = None


class SystemRoleInfo(BaseSchema):
    """Information about system-defined roles."""
    
    code: str
    name: str
    description: str
    hierarchy_level: int
    default_permissions: List[str]


# Pre-defined system roles info
SYSTEM_ROLES = [
    SystemRoleInfo(
        code="owner",
        name="Owner",
        description="Organization owner with full access",
        hierarchy_level=100,
        default_permissions=["*:*"]
    ),
    SystemRoleInfo(
        code="admin",
        name="Administrator",
        description="Administrator with most permissions",
        hierarchy_level=90,
        default_permissions=[
            "user:*", "role:*", "team:*", "lead:*", "contact:*",
            "deal:*", "ticket:*", "product:*", "inventory:*",
            "report:*", "setting:read", "setting:update"
        ]
    ),
    SystemRoleInfo(
        code="manager",
        name="Manager",
        description="Team manager with elevated permissions",
        hierarchy_level=70,
        default_permissions=[
            "user:read", "user:list", "team:read", "team:list",
            "lead:*", "contact:*", "deal:*", "ticket:*",
            "product:read", "product:list", "report:read"
        ]
    ),
    SystemRoleInfo(
        code="member",
        name="Member",
        description="Regular team member",
        hierarchy_level=50,
        default_permissions=[
            "lead:create", "lead:read", "lead:update", "lead:list",
            "contact:create", "contact:read", "contact:update", "contact:list",
            "deal:create", "deal:read", "deal:update", "deal:list",
            "ticket:create", "ticket:read", "ticket:update", "ticket:list",
            "product:read", "product:list"
        ]
    ),
    SystemRoleInfo(
        code="viewer",
        name="Viewer",
        description="Read-only access",
        hierarchy_level=10,
        default_permissions=[
            "lead:read", "lead:list",
            "contact:read", "contact:list",
            "deal:read", "deal:list",
            "ticket:read", "ticket:list",
            "product:read", "product:list"
        ]
    )
]
