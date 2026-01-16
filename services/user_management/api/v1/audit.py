"""Audit log endpoints."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_async_session
from shared.middleware.auth import get_current_user, require_permissions
from shared.middleware.tenant import require_tenant
from shared.models.audit import AuditLog, AuditAction
from shared.schemas.common import PaginatedResponse, PaginationParams
from shared.security.jwt import TokenPayload
from services.user_management.services.audit_service import AuditService

router = APIRouter()


@router.get("")
async def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: Optional[UUID] = Query(None, description="Filter by user"),
    action: Optional[AuditAction] = Query(None, description="Filter by action"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    resource_id: Optional[UUID] = Query(None, description="Filter by resource ID"),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter to date"),
    current_user: TokenPayload = Depends(require_permissions("audit_log:read")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """List audit logs for the organization."""
    audit_service = AuditService(db)
    
    result = await audit_service.list_audit_logs(
        organization_id=tenant_id,
        page=page,
        page_size=page_size,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        start_date=start_date,
        end_date=end_date,
    )
    
    return result


@router.get("/entity/{entity_type}/{entity_id}")
async def get_entity_audit_logs(
    entity_type: str,
    entity_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: TokenPayload = Depends(require_permissions("audit_log:read")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Get audit logs for a specific entity."""
    audit_service = AuditService(db)
    
    result = await audit_service.list_audit_logs(
        organization_id=tenant_id,
        page=page,
        page_size=page_size,
        resource_type=entity_type,
        resource_id=entity_id,
    )
    
    return result


@router.get("/user/{user_id}")
async def get_user_audit_logs(
    user_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: TokenPayload = Depends(require_permissions("audit_log:read")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Get audit logs for a specific user."""
    audit_service = AuditService(db)
    
    result = await audit_service.list_audit_logs(
        organization_id=tenant_id,
        page=page,
        page_size=page_size,
        user_id=user_id,
    )
    
    return result
