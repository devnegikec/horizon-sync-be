"""Multi-tenant database utilities."""
from contextvars import ContextVar
from typing import Optional
from uuid import UUID

from sqlalchemy import event
from sqlalchemy.orm import Query, Session

# Context variable for current tenant
_tenant_id: ContextVar[Optional[UUID]] = ContextVar("tenant_id", default=None)


def get_tenant_id() -> Optional[UUID]:
    """Get current tenant ID from context."""
    return _tenant_id.get()


def set_tenant_id(tenant_id: Optional[UUID]) -> None:
    """Set current tenant ID in context."""
    _tenant_id.set(tenant_id)


class TenantContext:
    """Context manager for tenant scope."""
    
    def __init__(self, tenant_id: UUID):
        self.tenant_id = tenant_id
        self.previous_tenant_id: Optional[UUID] = None
    
    def __enter__(self):
        self.previous_tenant_id = get_tenant_id()
        set_tenant_id(self.tenant_id)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        set_tenant_id(self.previous_tenant_id)


async def tenant_context(tenant_id: UUID):
    """Async context manager for tenant scope."""
    previous_tenant_id = get_tenant_id()
    set_tenant_id(tenant_id)
    try:
        yield
    finally:
        set_tenant_id(previous_tenant_id)


def apply_tenant_filter(query: Query, model_class) -> Query:
    """Apply tenant filter to query if model has organization_id."""
    tenant_id = get_tenant_id()
    if tenant_id and hasattr(model_class, 'organization_id'):
        return query.filter(model_class.organization_id == tenant_id)
    return query


class TenantQuery(Query):
    """Custom query class that automatically applies tenant filtering."""
    
    def __init__(self, entities, session=None):
        super().__init__(entities, session)
        self._apply_tenant_filter()
    
    def _apply_tenant_filter(self):
        """Apply tenant filter if applicable."""
        tenant_id = get_tenant_id()
        if tenant_id:
            for entity in self._entities:
                if hasattr(entity, 'organization_id'):
                    self = self.filter(entity.organization_id == tenant_id)


def validate_tenant_access(organization_id: UUID) -> bool:
    """
    Validate that current context has access to the specified organization.
    Returns True if access is allowed, False otherwise.
    """
    current_tenant = get_tenant_id()
    if current_tenant is None:
        # No tenant context - might be super admin or system operation
        return True
    return current_tenant == organization_id


class TenantIsolationError(Exception):
    """Raised when tenant isolation is violated."""
    
    def __init__(self, message: str = "Tenant isolation violation detected"):
        self.message = message
        super().__init__(self.message)
