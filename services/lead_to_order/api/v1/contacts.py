"""Contact management endpoints."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_async_session
from shared.middleware.auth import require_permissions
from shared.middleware.tenant import require_tenant
from shared.schemas.common import PaginatedResponse, SuccessResponse
from shared.security.jwt import TokenPayload
from services.lead_to_order.models.contact import Contact, ContactType

router = APIRouter()


class ContactCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    mobile: Optional[str] = Field(default=None, max_length=50)
    company_name: Optional[str] = Field(default=None, max_length=255)
    job_title: Optional[str] = Field(default=None, max_length=100)
    contact_type: Optional[ContactType] = ContactType.CUSTOMER
    assigned_to_id: Optional[UUID] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[dict] = None


class ContactUpdate(BaseModel):
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    mobile: Optional[str] = Field(default=None, max_length=50)
    company_name: Optional[str] = Field(default=None, max_length=255)
    job_title: Optional[str] = Field(default=None, max_length=100)
    contact_type: Optional[ContactType] = None
    assigned_to_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[dict] = None


class ContactResponse(BaseModel):
    id: UUID
    organization_id: UUID
    first_name: str
    last_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    mobile: Optional[str]
    company_name: Optional[str]
    job_title: Optional[str]
    contact_type: ContactType
    assigned_to_id: Optional[UUID]
    is_active: bool
    tags: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("", response_model=PaginatedResponse[ContactResponse])
async def list_contacts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    contact_type: Optional[ContactType] = None,
    assigned_to_id: Optional[UUID] = None,
    is_active: Optional[bool] = True,
    current_user: TokenPayload = Depends(require_permissions("contact:list")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """List contacts with filtering and pagination."""
    query = select(Contact).where(
        Contact.organization_id == tenant_id,
        Contact.deleted_at.is_(None)
    )
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Contact.first_name.ilike(search_term),
                Contact.last_name.ilike(search_term),
                Contact.email.ilike(search_term),
                Contact.company_name.ilike(search_term),
            )
        )
    
    if contact_type:
        query = query.where(Contact.contact_type == contact_type)
    if assigned_to_id:
        query = query.where(Contact.assigned_to_id == assigned_to_id)
    if is_active is not None:
        query = query.where(Contact.is_active == is_active)
    
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0
    
    offset = (page - 1) * page_size
    query = query.order_by(Contact.created_at.desc()).offset(offset).limit(page_size)
    
    result = await db.execute(query)
    contacts = result.scalars().all()
    
    return PaginatedResponse.create(
        items=[ContactResponse.model_validate(c) for c in contacts],
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("", response_model=ContactResponse)
async def create_contact(
    contact_data: ContactCreate,
    current_user: TokenPayload = Depends(require_permissions("contact:create")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new contact."""
    contact = Contact(
        organization_id=tenant_id,
        created_by=UUID(current_user.sub),
        **contact_data.model_dump(exclude_unset=True)
    )
    
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    
    return ContactResponse.model_validate(contact)


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: UUID,
    current_user: TokenPayload = Depends(require_permissions("contact:read")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Get contact details."""
    query = select(Contact).where(
        Contact.id == contact_id,
        Contact.organization_id == tenant_id,
        Contact.deleted_at.is_(None)
    )
    
    result = await db.execute(query)
    contact = result.scalar_one_or_none()
    
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return ContactResponse.model_validate(contact)


@router.patch("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: UUID,
    update_data: ContactUpdate,
    current_user: TokenPayload = Depends(require_permissions("contact:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Update a contact."""
    query = select(Contact).where(
        Contact.id == contact_id,
        Contact.organization_id == tenant_id,
        Contact.deleted_at.is_(None)
    )
    
    result = await db.execute(query)
    contact = result.scalar_one_or_none()
    
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(contact, key, value)
    
    contact.updated_by = UUID(current_user.sub)
    
    await db.commit()
    await db.refresh(contact)
    
    return ContactResponse.model_validate(contact)


@router.delete("/{contact_id}", response_model=SuccessResponse)
async def delete_contact(
    contact_id: UUID,
    current_user: TokenPayload = Depends(require_permissions("contact:delete")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Soft delete a contact."""
    query = select(Contact).where(
        Contact.id == contact_id,
        Contact.organization_id == tenant_id,
        Contact.deleted_at.is_(None)
    )
    
    result = await db.execute(query)
    contact = result.scalar_one_or_none()
    
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    contact.deleted_at = datetime.utcnow()
    await db.commit()
    
    return SuccessResponse(message="Contact deleted successfully")
