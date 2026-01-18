"""Permission checking utilities for RBAC."""
from functools import wraps
from typing import Callable, List, Optional, Set
from uuid import UUID

from fastapi import HTTPException, status




class PermissionChecker:
    """
    Utility class for checking user permissions.
    """
    
    def __init__(self, permissions: List[str]):
        """
        Initialize with a list of permission codes.
        
        Args:
            permissions: List of permission codes (e.g., ['lead:create', 'lead:read'])
        """
        self.permissions: Set[str] = set(permissions)
    
    def has(self, permission: str) -> bool:
        """
        Check if user has a specific permission.
        
        Args:
            permission: Permission code to check
        
        Returns:
            True if user has the permission
        """
        # Check exact match
        if permission in self.permissions:
            return True
        
        # Check wildcard permissions (e.g., 'lead:*' matches 'lead:create')
        resource = permission.split(':')[0] if ':' in permission else permission
        if f"{resource}:*" in self.permissions:
            return True
        
        # Check super admin (all permissions)
        if "*:*" in self.permissions or "admin:*" in self.permissions:
            return True
        
        return False
    
    def has_any(self, permissions: List[str]) -> bool:
        """
        Check if user has any of the specified permissions.
        
        Args:
            permissions: List of permission codes
        
        Returns:
            True if user has at least one permission
        """
        return any(self.has(p) for p in permissions)
    
    def has_all(self, permissions: List[str]) -> bool:
        """
        Check if user has all of the specified permissions.
        
        Args:
            permissions: List of permission codes
        
        Returns:
            True if user has all permissions
        """
        return all(self.has(p) for p in permissions)
    
    def can(self, resource: str, action: str) -> bool:
        """
        Check if user can perform an action on a resource.
        
        Args:
            resource: Resource type (string)
            action: Action type (string)
        
        Returns:
            True if user can perform the action
        """
        permission = f"{resource}:{action}"
        return self.has(permission)


def check_permission(
    permissions: List[str],
    required: str,
    raise_exception: bool = True
) -> bool:
    """
    Check if permissions list contains required permission.
    
    Args:
        permissions: List of user's permissions
        required: Required permission code
        raise_exception: Raise HTTPException if not permitted
    
    Returns:
        True if permitted
    
    Raises:
        HTTPException: If not permitted and raise_exception is True
    """
    checker = PermissionChecker(permissions)
    has_perm = checker.has(required)
    
    if not has_perm and raise_exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: {required}"
        )
    
    return has_perm


def has_permission(permissions: List[str], required: str) -> bool:
    """
    Check if permissions list contains required permission (no exception).
    
    Args:
        permissions: List of user's permissions
        required: Required permission code
    
    Returns:
        True if permitted
    """
    return check_permission(permissions, required, raise_exception=False)


def require_permission(permission: str):
    """
    Decorator to require a specific permission for an endpoint.
    Must be used after authentication dependency that sets request.state.permissions.
    
    Usage:
        @router.get("/leads")
        @require_permission("lead:list")
        async def list_leads(request: Request):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find the request object in args or kwargs
            request = kwargs.get('request')
            if request is None:
                for arg in args:
                    if hasattr(arg, 'state'):
                        request = arg
                        break
            
            if request is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Request object not found"
                )
            
            permissions = getattr(request.state, 'permissions', [])
            check_permission(permissions, permission)
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def build_permission_code(resource: str, action: str) -> str:
    """
    Build a permission code from resource and action strings.
    """
    return f"{resource}:{action}"


def get_all_permissions() -> List[str]:
    """
    Generate common permission codes.
    """
    resources = [
        "organization", "user", "role", "team", "lead", "contact",
        "deal", "ticket", "product", "inventory", "warehouse",
        "report", "setting", "subscription", "audit_log"
    ]
    actions = ["create", "read", "update", "delete", "list"]
    
    permissions = []
    for resource in resources:
        for action in actions:
            permissions.append(build_permission_code(resource, action))
    return permissions


# Pre-defined permission sets for common roles
OWNER_PERMISSIONS = ["*:*"]  # All permissions

ADMIN_PERMISSIONS = [
    "user:*",
    "role:*",
    "team:*",
    "lead:*",
    "contact:*",
    "deal:*",
    "ticket:*",
    "product:*",
    "inventory:*",
    "report:*",
    "setting:read",
    "setting:update",
    "audit_log:read",
]

MANAGER_PERMISSIONS = [
    "user:read",
    "user:list",
    "team:read",
    "team:list",
    "lead:*",
    "contact:*",
    "deal:*",
    "ticket:*",
    "product:read",
    "product:list",
    "inventory:read",
    "inventory:list",
    "report:read",
]

MEMBER_PERMISSIONS = [
    "lead:create",
    "lead:read",
    "lead:update",
    "lead:list",
    "contact:create",
    "contact:read",
    "contact:update",
    "contact:list",
    "deal:create",
    "deal:read",
    "deal:update",
    "deal:list",
    "ticket:create",
    "ticket:read",
    "ticket:update",
    "ticket:list",
    "product:read",
    "product:list",
]

VIEWER_PERMISSIONS = [
    "lead:read",
    "lead:list",
    "contact:read",
    "contact:list",
    "deal:read",
    "deal:list",
    "ticket:read",
    "ticket:list",
    "product:read",
    "product:list",
]
