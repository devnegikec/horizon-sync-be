"""Audit logging middleware."""
import json
from datetime import datetime
from typing import Any, Callable, Dict, Optional
from uuid import UUID, uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from shared.models.audit import AuditAction


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware for automatic audit logging of requests.
    Logs significant operations for compliance and security.
    """
    
    # Methods that should be audited
    AUDITABLE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
    
    # Paths to exclude from auditing
    EXCLUDE_PATHS = {
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/v1/auth/login",  # Has its own audit
        "/api/v1/auth/refresh",
    }
    
    def __init__(self, app, audit_callback: Callable = None):
        super().__init__(app)
        self.audit_callback = audit_callback
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip non-auditable requests
        if request.method not in self.AUDITABLE_METHODS:
            return await call_next(request)
        
        path = request.url.path
        if path in self.EXCLUDE_PATHS:
            return await call_next(request)
        
        # Generate request ID for tracing
        request_id = str(uuid4())
        request.state.request_id = request_id
        
        # Capture request info before processing
        audit_data = await self._capture_request_info(request, request_id)
        
        # Process request
        response = await call_next(request)
        
        # Log audit event if callback provided
        if self.audit_callback and response.status_code < 400:
            audit_data["status_code"] = response.status_code
            await self._log_audit(audit_data)
        
        return response
    
    async def _capture_request_info(
        self,
        request: Request,
        request_id: str
    ) -> Dict[str, Any]:
        """Capture request information for audit."""
        
        # Get user info from request state (set by auth middleware)
        user_id = getattr(request.state, 'user_id', None)
        org_id = getattr(request.state, 'tenant_id', None)
        
        # Determine action from method
        action_map = {
            "POST": AuditAction.CREATE,
            "PUT": AuditAction.UPDATE,
            "PATCH": AuditAction.UPDATE,
            "DELETE": AuditAction.DELETE,
        }
        action = action_map.get(request.method, AuditAction.UPDATE)
        
        # Extract resource type from path
        resource_type, resource_id = self._parse_resource_from_path(request.url.path)
        
        return {
            "request_id": request_id,
            "user_id": str(user_id) if user_id else None,
            "organization_id": str(org_id) if org_id else None,
            "action": action.value,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "ip_address": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent"),
            "path": request.url.path,
            "method": request.method,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def _parse_resource_from_path(self, path: str) -> tuple[str, Optional[str]]:
        """Parse resource type and ID from URL path."""
        # Remove /api/v1 prefix
        clean_path = path.replace("/api/v1/", "").strip("/")
        parts = clean_path.split("/")
        
        if len(parts) >= 1:
            resource_type = parts[0].rstrip("s")  # leads -> lead
            resource_id = parts[1] if len(parts) > 1 else None
            return resource_type, resource_id
        
        return "unknown", None
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address, handling proxies."""
        # Check X-Forwarded-For header (from load balancer/proxy)
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fall back to direct client
        if request.client:
            return request.client.host
        
        return "unknown"
    
    async def _log_audit(self, audit_data: Dict[str, Any]):
        """Log audit event."""
        if self.audit_callback:
            try:
                await self.audit_callback(audit_data)
            except Exception:
                # Don't let audit failures affect the request
                pass


async def log_audit_event(
    organization_id: Optional[UUID],
    user_id: Optional[UUID],
    action: AuditAction,
    resource_type: str,
    resource_id: Optional[UUID] = None,
    resource_name: Optional[str] = None,
    old_values: Optional[Dict] = None,
    new_values: Optional[Dict] = None,
    changed_fields: Optional[list] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    request_id: Optional[str] = None,
    description: Optional[str] = None,
    metadata: Optional[Dict] = None,
    db_session = None
):
    """
    Log an audit event to the database.
    
    This function should be called directly for important operations
    that need explicit audit logging (like login, permission changes, etc.)
    """
    from shared.models.audit import AuditLog
    
    if db_session is None:
        # If no session provided, create one
        from shared.database import get_db
        async with get_db() as session:
            db_session = session
            await _create_audit_log(
                db_session, organization_id, user_id, action, resource_type,
                resource_id, resource_name, old_values, new_values,
                changed_fields, ip_address, user_agent, request_id,
                description, metadata
            )
    else:
        await _create_audit_log(
            db_session, organization_id, user_id, action, resource_type,
            resource_id, resource_name, old_values, new_values,
            changed_fields, ip_address, user_agent, request_id,
            description, metadata
        )


async def _create_audit_log(
    session,
    organization_id, user_id, action, resource_type,
    resource_id, resource_name, old_values, new_values,
    changed_fields, ip_address, user_agent, request_id,
    description, metadata
):
    """Create audit log entry in database."""
    from shared.models.audit import AuditLog
    
    audit_log = AuditLog(
        organization_id=organization_id,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        resource_name=resource_name,
        old_values=old_values,
        new_values=new_values,
        changed_fields=changed_fields,
        ip_address=ip_address,
        user_agent=user_agent,
        request_id=request_id,
        description=description,
        metadata=metadata or {},
    )
    
    session.add(audit_log)
    await session.flush()
