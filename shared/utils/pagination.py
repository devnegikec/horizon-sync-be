"""Pagination utilities."""
from typing import Any, Generic, List, Optional, Type, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Query

from shared.schemas.common import PaginatedResponse, PaginationParams

T = TypeVar('T')


class Paginator(Generic[T]):
    """
    Async pagination helper for SQLAlchemy queries.
    """
    
    def __init__(
        self,
        session: AsyncSession,
        query: Any,
        params: PaginationParams,
        response_schema: Optional[Type] = None
    ):
        self.session = session
        self.query = query
        self.params = params
        self.response_schema = response_schema
    
    async def paginate(self) -> PaginatedResponse[T]:
        """Execute paginated query and return response."""
        # Get total count
        count_query = select(func.count()).select_from(self.query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply sorting
        if self.params.sort_by:
            # This assumes the query is on a model with the sort_by attribute
            order_col = getattr(self.query.column_descriptions[0]['entity'], self.params.sort_by, None)
            if order_col:
                if self.params.sort_order == "desc":
                    self.query = self.query.order_by(order_col.desc())
                else:
                    self.query = self.query.order_by(order_col.asc())
        
        # Apply pagination
        paginated_query = self.query.offset(self.params.offset).limit(self.params.limit)
        
        # Execute query
        result = await self.session.execute(paginated_query)
        items = result.scalars().all()
        
        # Convert to response schema if provided
        if self.response_schema:
            items = [self.response_schema.model_validate(item) for item in items]
        
        return PaginatedResponse.create(
            items=items,
            total=total,
            page=self.params.page,
            page_size=self.params.page_size
        )


async def paginate(
    session: AsyncSession,
    query: Any,
    page: int = 1,
    page_size: int = 20,
    sort_by: Optional[str] = None,
    sort_order: str = "desc",
    response_schema: Optional[Type] = None
) -> PaginatedResponse:
    """
    Paginate a SQLAlchemy query.
    
    Usage:
        query = select(User).where(User.is_active == True)
        result = await paginate(session, query, page=1, page_size=20)
    """
    params = PaginationParams(
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    paginator = Paginator(session, query, params, response_schema)
    return await paginator.paginate()


def create_pagination_params(
    page: int = 1,
    page_size: int = 20,
    sort_by: Optional[str] = None,
    sort_order: str = "desc"
) -> PaginationParams:
    """Create pagination parameters."""
    return PaginationParams(
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )
