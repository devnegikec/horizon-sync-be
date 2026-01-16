"""Common Pydantic schemas used across all services."""
from datetime import datetime
from typing import Any, Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    model_config = ConfigDict(
        from_attributes=True,  # Allow ORM mode
        populate_by_name=True,
        use_enum_values=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
    )


# Generic type for paginated responses
T = TypeVar('T')


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""
    
    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(default=None, description="Field to sort by")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$", description="Sort order")
    
    @property
    def offset(self) -> int:
        """Calculate offset for SQL queries."""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Get limit for SQL queries."""
        return self.page_size


class PaginatedResponse(BaseSchema, Generic[T]):
    """Generic paginated response wrapper."""
    
    items: List[T]
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Items per page")
    pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there are more pages")
    has_prev: bool = Field(description="Whether there are previous pages")
    
    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        page_size: int
    ) -> "PaginatedResponse[T]":
        """Create a paginated response from items and pagination info."""
        pages = (total + page_size - 1) // page_size if total > 0 else 1
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1
        )


class SuccessResponse(BaseSchema):
    """Generic success response."""
    
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[Any] = None


class ErrorResponse(BaseSchema):
    """Generic error response."""
    
    success: bool = False
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
    errors: Optional[List[dict]] = None


class HealthResponse(BaseSchema):
    """Health check response."""
    
    status: str = "healthy"
    service: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    checks: Optional[dict] = None


class IDResponse(BaseSchema):
    """Response containing just an ID."""
    
    id: UUID


class BulkOperationResponse(BaseSchema):
    """Response for bulk operations."""
    
    success_count: int
    failure_count: int
    total: int
    failed_items: Optional[List[dict]] = None


class FilterParams(BaseModel):
    """Base filter parameters."""
    
    search: Optional[str] = Field(default=None, description="Search term")
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    updated_after: Optional[datetime] = None
    updated_before: Optional[datetime] = None
    is_active: Optional[bool] = None


class DateRangeParams(BaseModel):
    """Date range parameters."""
    
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class SortParams(BaseModel):
    """Sort parameters."""
    
    sort_by: str = "created_at"
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
