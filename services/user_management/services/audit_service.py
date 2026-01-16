"""Audit log service."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models.audit import AuditLog, AuditAction
from shared.schemas.common import PaginatedResponse


class AuditService:
    """Service for audit log operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def list_audit_logs(
        self,
        organization_id: UUID,
        page: int = 1,
        page_size: int = 20,
        user_id: Optional[UUID] = None,
        action: Optional[AuditAction] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """List audit logs with filtering and pagination."""
        # Base query
        query = select(AuditLog).where(
            AuditLog.organization_id == organization_id
        )
        
        # Apply filters
        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        
        if action:
            query = query.where(AuditLog.action == action)
        
        if resource_type:
            query = query.where(AuditLog.resource_type == resource_type)
        
        if resource_id:
            query = query.where(AuditLog.resource_id == resource_id)
        
        if start_date:
            query = query.where(AuditLog.created_at >= start_date)
        
        if end_date:
            query = query.where(AuditLog.created_at <= end_date)
        
        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0
        
        # Apply pagination and ordering
        offset = (page - 1) * page_size
        query = query.order_by(AuditLog.created_at.desc())
        query = query.offset(offset).limit(page_size)
        
        result = await self.db.execute(query)
        logs = result.scalars().all()
        
        pages = (total + page_size - 1) // page_size if total > 0 else 1
        
        return {
            "items": [
                {
                    "id": str(log.id),
                    "user_id": str(log.user_id) if log.user_id else None,
                    "user_email": log.user_email,
                    "action": log.action.value,
                    "resource_type": log.resource_type,
                    "resource_id": str(log.resource_id) if log.resource_id else None,
                    "resource_name": log.resource_name,
                    "old_values": log.old_values,
                    "new_values": log.new_values,
                    "changed_fields": log.changed_fields,
                    "ip_address": log.ip_address,
                    "description": log.description,
                    "created_at": log.created_at.isoformat(),
                }
                for log in logs
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages,
            "has_next": page < pages,
            "has_prev": page > 1,
        }
    
    async def create_audit_log(
        self,
        organization_id: UUID,
        user_id: Optional[UUID],
        action: AuditAction,
        resource_type: str,
        resource_id: Optional[UUID] = None,
        resource_name: Optional[str] = None,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None,
        changed_fields: Optional[List[str]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> AuditLog:
        """Create an audit log entry."""
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
            description=description,
            metadata=metadata or {},
        )
        
        self.db.add(audit_log)
        await self.db.flush()
        
        return audit_log
