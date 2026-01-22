"""Common test utilities and helpers."""
import json
from typing import Any, Dict, Optional
from uuid import UUID
from datetime import datetime
from httpx import Response
from sqlalchemy.ext.asyncio import AsyncSession


class TestHelper:
    """Helper class for common testing operations."""

    @staticmethod
    def assert_status_in(response: Response, expected_statuses: list, message: str = ""):
        """
        Assert that response status is in the expected list.
        
        Args:
            response: HTTPResponse object
            expected_statuses: List of acceptable status codes
            message: Optional error message
        """
        assert response.status_code in expected_statuses, (
            f"{message}\n"
            f"Expected status in {expected_statuses}, got {response.status_code}\n"
            f"Response: {response.text}"
        )

    @staticmethod
    def assert_success(response: Response, message: str = ""):
        """Assert that response status is successful (200-299)."""
        assert 200 <= response.status_code < 300, (
            f"{message}\n"
            f"Expected success status, got {response.status_code}\n"
            f"Response: {response.text}"
        )

    @staticmethod
    def assert_error(response: Response, message: str = ""):
        """Assert that response status is an error (400+)."""
        assert response.status_code >= 400, (
            f"{message}\n"
            f"Expected error status, got {response.status_code}\n"
            f"Response: {response.text}"
        )

    @staticmethod
    def assert_unauthorized(response: Response, message: str = ""):
        """Assert that response is 401 Unauthorized."""
        assert response.status_code == 401, (
            f"{message}\n"
            f"Expected 401, got {response.status_code}\n"
            f"Response: {response.text}"
        )

    @staticmethod
    def assert_forbidden(response: Response, message: str = ""):
        """Assert that response is 403 Forbidden."""
        assert response.status_code == 403, (
            f"{message}\n"
            f"Expected 403, got {response.status_code}\n"
            f"Response: {response.text}"
        )

    @staticmethod
    def assert_not_found(response: Response, message: str = ""):
        """Assert that response is 404 Not Found."""
        assert response.status_code == 404, (
            f"{message}\n"
            f"Expected 404, got {response.status_code}\n"
            f"Response: {response.text}"
        )

    @staticmethod
    def get_json_response(response: Response) -> Dict[str, Any]:
        """Get and parse JSON response body."""
        try:
            return response.json()
        except json.JSONDecodeError:
            raise AssertionError(
                f"Expected JSON response, got:\n{response.text}"
            )

    @staticmethod
    def assert_response_has_keys(response: Response, keys: list, message: str = ""):
        """Assert that response JSON has all expected keys."""
        data = TestHelper.get_json_response(response)
        missing = set(keys) - set(data.keys())
        assert not missing, (
            f"{message}\n"
            f"Missing keys in response: {missing}\n"
            f"Response keys: {list(data.keys())}"
        )

    @staticmethod
    def assert_paginated_response(response: Response, message: str = ""):
        """Assert that response is a valid paginated response."""
        data = TestHelper.get_json_response(response)
        required_keys = ["items", "total", "page", "page_size"]
        TestHelper.assert_response_has_keys(response, required_keys, message)
        
        assert isinstance(data["items"], list), "items must be a list"
        assert isinstance(data["total"], int), "total must be an integer"
        assert isinstance(data["page"], int), "page must be an integer"
        assert isinstance(data["page_size"], int), "page_size must be an integer"


class DataFactory:
    """Factory for creating test data."""

    @staticmethod
    def create_user_data(
        email: str = "test@example.com",
        first_name: str = "Test",
        last_name: str = "User",
        password: str = "TestPassword123!",
        **kwargs
    ) -> Dict[str, Any]:
        """Create test user data."""
        data = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "password": password,
        }
        data.update(kwargs)
        return data

    @staticmethod
    def create_product_data(
        name: str = "Test Product",
        sku: str = "SKU-001",
        unit_price: float = 99.99,
        **kwargs
    ) -> Dict[str, Any]:
        """Create test product data."""
        data = {
            "name": name,
            "sku": sku,
            "unit_price": unit_price,
        }
        data.update(kwargs)
        return data

    @staticmethod
    def create_invoice_data(
        invoice_no: str = "INV-001",
        customer_id: str = None,
        items: list = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create test invoice data."""
        if customer_id is None:
            from uuid import uuid4
            customer_id = str(uuid4())
        
        if items is None:
            items = [
                {
                    "description": "Service",
                    "quantity": 1,
                    "unit_price": 100.0,
                    "total_amount": 100.0
                }
            ]
        
        data = {
            "invoice_no": invoice_no,
            "customer_id": customer_id,
            "items": items,
        }
        data.update(kwargs)
        return data

    @staticmethod
    def create_lead_data(
        title: str = "New Lead",
        email: str = "lead@example.com",
        **kwargs
    ) -> Dict[str, Any]:
        """Create test lead data."""
        data = {
            "title": title,
            "email": email,
        }
        data.update(kwargs)
        return data

    @staticmethod
    def create_ticket_data(
        subject: str = "Test Issue",
        description: str = "Test ticket description",
        **kwargs
    ) -> Dict[str, Any]:
        """Create test ticket data."""
        data = {
            "subject": subject,
            "description": description,
        }
        data.update(kwargs)
        return data


class DatabaseHelper:
    """Helper class for database operations in tests."""

    @staticmethod
    async def count_records(session: AsyncSession, model_class) -> int:
        """Count total records of a model."""
        from sqlalchemy import select, func
        result = await session.execute(
            select(func.count()).select_from(model_class)
        )
        return result.scalar() or 0

    @staticmethod
    async def get_records(session: AsyncSession, model_class, limit: int = None):
        """Get records of a model."""
        from sqlalchemy import select
        query = select(model_class)
        if limit:
            query = query.limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def record_exists(session: AsyncSession, model_class, **filters) -> bool:
        """Check if record exists matching filters."""
        from sqlalchemy import select
        query = select(model_class)
        for key, value in filters.items():
            if hasattr(model_class, key):
                query = query.where(getattr(model_class, key) == value)
        result = await session.execute(query)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def clean_table(session: AsyncSession, model_class):
        """Delete all records from a table (use carefully!)."""
        from sqlalchemy import delete
        await session.execute(delete(model_class))
        await session.commit()


def serialize_uuid(obj):
    """JSON serializer for UUID objects."""
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def create_auth_header(token: str) -> Dict[str, str]:
    """Create authorization header from token."""
    return {"Authorization": f"Bearer {token}"}


def extract_id_from_response(response: Response) -> Optional[str]:
    """Extract ID from response JSON."""
    data = response.json()
    if "id" in data:
        return data["id"]
    return None


def is_valid_uuid(value: str) -> bool:
    """Check if string is valid UUID."""
    try:
        UUID(value)
        return True
    except ValueError:
        return False
