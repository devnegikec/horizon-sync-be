"""Ticket management endpoints."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from shared.database import get_async_session
from shared.middleware.auth import require_permissions
from shared.middleware.tenant import require_tenant
from shared.schemas.common import PaginatedResponse, SuccessResponse
from shared.security.jwt import TokenPayload
from shared.utils.helpers import generate_reference_number
from services.support_ticket.models.ticket import Ticket, TicketStatus, TicketPriority, TicketCategory
from services.support_ticket.models.comment import TicketComment

router = APIRouter()

class TicketCreate(BaseModel):
    subject: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    contact_id: Optional[UUID] = None
    requester_name: Optional[str] = None
    requester_email: Optional[EmailStr] = None
    priority: Optional[TicketPriority] = TicketPriority.MEDIUM
    category: Optional[TicketCategory] = TicketCategory.GENERAL
    assigned_to_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None

class TicketUpdate(BaseModel):
    subject: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    category: Optional[TicketCategory] = None
    assigned_to_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None

class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1)
    is_internal: bool = False
    is_resolution: bool = False

class TicketResponse(BaseModel):
    id: UUID
    organization_id: UUID
    ticket_number: str
    subject: str
    description: Optional[str]
    requester_name: Optional[str]
    requester_email: Optional[str]
    status: TicketStatus
    priority: TicketPriority
    category: TicketCategory
    assigned_to_id: Optional[UUID]
    team_id: Optional[UUID]
    due_date: Optional[datetime]
    first_response_at: Optional[datetime]
    resolved_at: Optional[datetime]
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

@router.get("", response_model=PaginatedResponse[TicketResponse])
async def list_tickets(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None, status: Optional[TicketStatus] = None,
    priority: Optional[TicketPriority] = None, assigned_to_id: Optional[UUID] = None,
    current_user: TokenPayload = Depends(require_permissions("ticket:list")),
    tenant_id: UUID = Depends(require_tenant), db: AsyncSession = Depends(get_async_session)
):
    query = select(Ticket).where(Ticket.organization_id == tenant_id, Ticket.deleted_at.is_(None))
    if search:
        query = query.where(or_(Ticket.subject.ilike(f"%{search}%"), Ticket.ticket_number.ilike(f"%{search}%")))
    if status: query = query.where(Ticket.status == status)
    if priority: query = query.where(Ticket.priority == priority)
    if assigned_to_id: query = query.where(Ticket.assigned_to_id == assigned_to_id)
    
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    query = query.order_by(Ticket.created_at.desc()).offset((page-1)*page_size).limit(page_size)
    tickets = (await db.execute(query)).scalars().all()
    return PaginatedResponse.create([TicketResponse.model_validate(t) for t in tickets], total, page, page_size)

@router.post("", response_model=TicketResponse)
async def create_ticket(
    data: TicketCreate,
    current_user: TokenPayload = Depends(require_permissions("ticket:create")),
    tenant_id: UUID = Depends(require_tenant), db: AsyncSession = Depends(get_async_session)
):
    ticket = Ticket(organization_id=tenant_id, ticket_number=generate_reference_number("TKT"),
                    created_by=UUID(current_user.sub), **data.model_dump(exclude_unset=True))
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    return TicketResponse.model_validate(ticket)

@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: UUID, current_user: TokenPayload = Depends(require_permissions("ticket:read")),
                     tenant_id: UUID = Depends(require_tenant), db: AsyncSession = Depends(get_async_session)):
    ticket = (await db.execute(select(Ticket).where(Ticket.id == ticket_id, Ticket.organization_id == tenant_id, Ticket.deleted_at.is_(None)))).scalar_one_or_none()
    if not ticket: raise HTTPException(status_code=404, detail="Ticket not found")
    return TicketResponse.model_validate(ticket)

@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(ticket_id: UUID, data: TicketUpdate, current_user: TokenPayload = Depends(require_permissions("ticket:update")),
                        tenant_id: UUID = Depends(require_tenant), db: AsyncSession = Depends(get_async_session)):
    ticket = (await db.execute(select(Ticket).where(Ticket.id == ticket_id, Ticket.organization_id == tenant_id, Ticket.deleted_at.is_(None)))).scalar_one_or_none()
    if not ticket: raise HTTPException(status_code=404, detail="Ticket not found")
    for k, v in data.model_dump(exclude_unset=True).items(): setattr(ticket, k, v)
    if data.status == TicketStatus.RESOLVED and not ticket.resolved_at: ticket.resolved_at = datetime.utcnow()
    if data.status == TicketStatus.CLOSED and not ticket.closed_at: ticket.closed_at = datetime.utcnow()
    ticket.updated_by = UUID(current_user.sub)
    await db.commit()
    await db.refresh(ticket)
    return TicketResponse.model_validate(ticket)

@router.post("/{ticket_id}/comments", response_model=dict)
async def add_comment(ticket_id: UUID, data: CommentCreate, current_user: TokenPayload = Depends(require_permissions("ticket:update")),
                      tenant_id: UUID = Depends(require_tenant), db: AsyncSession = Depends(get_async_session)):
    ticket = (await db.execute(select(Ticket).where(Ticket.id == ticket_id, Ticket.organization_id == tenant_id))).scalar_one_or_none()
    if not ticket: raise HTTPException(status_code=404, detail="Ticket not found")
    comment = TicketComment(ticket_id=ticket_id, user_id=UUID(current_user.sub), **data.model_dump())
    if not ticket.first_response_at: ticket.first_response_at = datetime.utcnow()
    if data.is_resolution: ticket.status = TicketStatus.RESOLVED; ticket.resolved_at = datetime.utcnow(); ticket.resolution_notes = data.content
    db.add(comment)
    await db.commit()
    return {"id": str(comment.id), "message": "Comment added"}

@router.delete("/{ticket_id}", response_model=SuccessResponse)
async def delete_ticket(ticket_id: UUID, current_user: TokenPayload = Depends(require_permissions("ticket:delete")),
                        tenant_id: UUID = Depends(require_tenant), db: AsyncSession = Depends(get_async_session)):
    ticket = (await db.execute(select(Ticket).where(Ticket.id == ticket_id, Ticket.organization_id == tenant_id))).scalar_one_or_none()
    if not ticket: raise HTTPException(status_code=404, detail="Ticket not found")
    ticket.deleted_at = datetime.utcnow()
    await db.commit()
    return SuccessResponse(message="Ticket deleted")
