"""Authentication middleware and dependencies."""
from typing import Callable, List, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware

from shared.security.jwt import decode_token, TokenPayload


# HTTP Bearer scheme for Swagger UI
security = HTTPBearer(auto_error=False)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract and validate JWT tokens.
    Sets user info in request state for downstream use.
    """
    
    def __init__(self, app, exclude_paths: list[str] = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/refresh",
            "/api/v1/auth/forgot-password",
            "/api/v1/auth/reset-password",
            "/api/v1/auth/verify-email",
            "/api/v1/organizations/onboard",
            "/api/v1/users/accept-invitation",
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip auth for excluded paths
        path = request.url.path
        if any(path.startswith(excluded) for excluded in self.exclude_paths):
            return await call_next(request)
        
        # Extract and validate token
        token_payload = await self._extract_token(request)
        
        if token_payload:
            # Set user info in request state
            request.state.user_id = UUID(token_payload.sub)
            request.state.permissions = token_payload.permissions
            request.state.role = token_payload.role
            if token_payload.org_id:
                request.state.tenant_id = UUID(token_payload.org_id)
        
        return await call_next(request)
    
    async def _extract_token(self, request: Request) -> Optional[TokenPayload]:
        """Extract and validate JWT from request."""
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header[7:]
        return decode_token(token)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenPayload:
    """
    Dependency to get current authenticated user.
    Raises 401 if not authenticated.
    """
    # Check if already processed by middleware
    user_id = getattr(request.state, 'user_id', None)
    if user_id:
        return TokenPayload(
            sub=str(user_id),
            org_id=str(getattr(request.state, 'tenant_id', None)) if getattr(request.state, 'tenant_id', None) else None,
            role=getattr(request.state, 'role', None),
            permissions=getattr(request.state, 'permissions', []),
            type="access",
            exp=None,
            iat=None,
        )
    
    # Try to extract from credentials
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


async def get_current_user_optional(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[TokenPayload]:
    """
    Dependency to optionally get current user.
    Returns None if not authenticated.
    """
    try:
        return await get_current_user(request, credentials)
    except HTTPException:
        return None


def require_permissions(*required_permissions: str):
    """
    Dependency factory to require specific permissions.
    
    Usage:
        @router.get("/admin")
        async def admin_route(
            user: TokenPayload = Depends(require_permissions("admin:read"))
        ):
            ...
    """
    async def permission_checker(
        current_user: TokenPayload = Depends(get_current_user)
    ) -> TokenPayload:
        from shared.security.permissions import PermissionChecker
        
        checker = PermissionChecker(current_user.permissions)
        
        if not checker.has_all(list(required_permissions)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permissions: {', '.join(required_permissions)}"
            )
        
        return current_user
    
    return permission_checker


def require_any_permission(*required_permissions: str):
    """
    Dependency factory to require any of the specified permissions.
    """
    async def permission_checker(
        current_user: TokenPayload = Depends(get_current_user)
    ) -> TokenPayload:
        from shared.security.permissions import PermissionChecker
        
        checker = PermissionChecker(current_user.permissions)
        
        if not checker.has_any(list(required_permissions)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires at least one of: {', '.join(required_permissions)}"
            )
        
        return current_user
    
    return permission_checker


def require_role(*allowed_roles: str):
    """
    Dependency factory to require specific role.
    
    Usage:
        @router.get("/admin")
        async def admin_route(
            user: TokenPayload = Depends(require_role("admin", "owner"))
        ):
            ...
    """
    async def role_checker(
        current_user: TokenPayload = Depends(get_current_user)
    ) -> TokenPayload:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role: {' or '.join(allowed_roles)}"
            )
        
        return current_user
    
    return role_checker


class CurrentUser:
    """
    Class-based dependency for getting current user with organization context.
    Provides convenient access to user ID, organization ID, and permissions.
    """
    
    def __init__(
        self,
        user_id: UUID,
        organization_id: Optional[UUID],
        role: Optional[str],
        permissions: List[str],
        email: Optional[str] = None,
    ):
        self.user_id = user_id
        self.organization_id = organization_id
        self.role = role
        self.permissions = permissions
        self.email = email
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission."""
        from shared.security.permissions import PermissionChecker
        return PermissionChecker(self.permissions).has(permission)
    
    def require_permission(self, permission: str):
        """Raise exception if user doesn't have permission."""
        if not self.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission}"
            )


async def get_current_user_context(
    current_user: TokenPayload = Depends(get_current_user)
) -> CurrentUser:
    """Get current user as CurrentUser object."""
    return CurrentUser(
        user_id=UUID(current_user.sub),
        organization_id=UUID(current_user.org_id) if current_user.org_id else None,
        role=current_user.role,
        permissions=current_user.permissions,
    )
