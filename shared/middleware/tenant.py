"""Tenant extraction middleware for multi-tenant isolation."""
from typing import Callable, Optional
from uuid import UUID

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from shared.database.multi_tenant import set_tenant_id, get_tenant_id
from shared.security.jwt import decode_token


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract tenant (organization) context from JWT token.
    Sets the tenant ID in context for automatic query filtering.
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
            "/api/v1/organizations/onboard",
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip tenant extraction for excluded paths
        path = request.url.path
        if any(path.startswith(excluded) for excluded in self.exclude_paths):
            return await call_next(request)
        
        # Try to extract tenant from JWT
        tenant_id = await self._extract_tenant_id(request)
        
        # Set tenant context
        set_tenant_id(tenant_id)
        
        # Store in request state for easy access
        request.state.tenant_id = tenant_id
        
        try:
            response = await call_next(request)
            return response
        finally:
            # Clear tenant context after request
            set_tenant_id(None)
    
    async def _extract_tenant_id(self, request: Request) -> Optional[UUID]:
        """Extract tenant ID from request."""
        
        # Try Authorization header first
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            payload = decode_token(token)
            if payload and payload.org_id:
                return UUID(payload.org_id)
        
        # Try X-Organization-ID header (for service-to-service calls)
        org_header = request.headers.get("X-Organization-ID")
        if org_header:
            try:
                return UUID(org_header)
            except ValueError:
                pass
        
        # Try query parameter (for some GET requests)
        org_param = request.query_params.get("organization_id")
        if org_param:
            try:
                return UUID(org_param)
            except ValueError:
                pass
        
        return None


def get_current_tenant(request: Request) -> Optional[UUID]:
    """
    Get current tenant ID from request state.
    Use as a dependency in FastAPI routes.
    """
    return getattr(request.state, 'tenant_id', None)


async def require_tenant(request: Request) -> UUID:
    """
    Dependency that requires a tenant context.
    Raises 400 if no tenant context.
    """
    from fastapi import HTTPException, status
    
    tenant_id = get_current_tenant(request)
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization context required. Please provide organization_id."
        )
    return tenant_id
