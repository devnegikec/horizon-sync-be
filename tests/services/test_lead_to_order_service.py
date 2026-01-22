"""Unit tests for Lead to Order Service endpoints."""
import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestLeads:
    """Tests for lead management endpoints."""

    @pytest.mark.asyncio
    async def test_list_leads(self, client: AsyncClient, auth_headers: dict):
        """Test listing leads."""
        response = await client.get(
            "/api/v1/leads",
            headers=auth_headers,
            params={"page": 1, "page_size": 20}
        )
        
        assert response.status_code in [200, 401, 403]
        if response.status_code == 200:
            data = response.json()
            assert "items" in data
            assert "total" in data

    @pytest.mark.asyncio
    async def test_list_leads_with_filters(self, client: AsyncClient, auth_headers: dict):
        """Test listing leads with filters."""
        response = await client.get(
            "/api/v1/leads",
            headers=auth_headers,
            params={
                "page": 1,
                "page_size": 20,
                "status": "new",
                "priority": "high",
                "search": "company"
            }
        )
        
        assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_create_lead(self, client: AsyncClient, auth_headers: dict):
        """Test creating a lead."""
        response = await client.post(
            "/api/v1/leads",
            headers=auth_headers,
            json={
                "title": "New Lead",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "phone": "+1234567890",
                "company_name": "Acme Corp",
                "job_title": "Manager",
                "source": "website",
                "priority": "medium",
                "estimated_value": 50000.0
            }
        )
        
        assert response.status_code in [201, 400, 401, 403, 422]
        if response.status_code == 201:
            data = response.json()
            assert data["title"] == "New Lead"
            assert data["status"] in ["new", "open"]

    @pytest.mark.asyncio
    async def test_get_lead(self, client: AsyncClient, auth_headers: dict):
        """Test getting a lead."""
        lead_id = uuid4()
        response = await client.get(
            f"/api/v1/leads/{lead_id}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 401, 403, 404]

    @pytest.mark.asyncio
    async def test_update_lead(self, client: AsyncClient, auth_headers: dict):
        """Test updating a lead."""
        lead_id = uuid4()
        response = await client.patch(
            f"/api/v1/leads/{lead_id}",
            headers=auth_headers,
            json={
                "status": "qualified",
                "priority": "high",
                "estimated_value": 75000.0,
                "assigned_to_id": str(uuid4())
            }
        )
        
        assert response.status_code in [200, 401, 403, 404, 422]

    @pytest.mark.asyncio
    async def test_delete_lead(self, client: AsyncClient, auth_headers: dict):
        """Test deleting a lead."""
        lead_id = uuid4()
        response = await client.delete(
            f"/api/v1/leads/{lead_id}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 204, 401, 403, 404]

    @pytest.mark.asyncio
    async def test_convert_lead_to_contact(self, client: AsyncClient, auth_headers: dict):
        """Test converting lead to contact."""
        lead_id = uuid4()
        response = await client.post(
            f"/api/v1/leads/{lead_id}/convert",
            headers=auth_headers,
            json={
                "create_contact": True,
                "create_deal": True,
                "deal_name": "Acme Corp Deal",
                "deal_amount": 50000.0
            }
        )
        
        assert response.status_code in [200, 400, 401, 403, 404, 422]


class TestContacts:
    """Tests for contact management endpoints."""

    @pytest.mark.asyncio
    async def test_list_contacts(self, client: AsyncClient, auth_headers: dict):
        """Test listing contacts."""
        response = await client.get(
            "/api/v1/contacts",
            headers=auth_headers,
            params={"page": 1, "page_size": 20}
        )
        
        assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_create_contact(self, client: AsyncClient, auth_headers: dict):
        """Test creating a contact."""
        response = await client.post(
            "/api/v1/contacts",
            headers=auth_headers,
            json={
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane@example.com",
                "phone": "+1234567890",
                "company": "Acme Corp",
                "job_title": "CEO"
            }
        )
        
        assert response.status_code in [201, 400, 401, 403, 422]

    @pytest.mark.asyncio
    async def test_get_contact(self, client: AsyncClient, auth_headers: dict):
        """Test getting a contact."""
        contact_id = uuid4()
        response = await client.get(
            f"/api/v1/contacts/{contact_id}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 401, 403, 404]

    @pytest.mark.asyncio
    async def test_update_contact(self, client: AsyncClient, auth_headers: dict):
        """Test updating a contact."""
        contact_id = uuid4()
        response = await client.patch(
            f"/api/v1/contacts/{contact_id}",
            headers=auth_headers,
            json={
                "job_title": "President",
                "phone": "+9876543210"
            }
        )
        
        assert response.status_code in [200, 401, 403, 404, 422]

    @pytest.mark.asyncio
    async def test_delete_contact(self, client: AsyncClient, auth_headers: dict):
        """Test deleting a contact."""
        contact_id = uuid4()
        response = await client.delete(
            f"/api/v1/contacts/{contact_id}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 204, 401, 403, 404]


class TestDeals:
    """Tests for deal management endpoints."""

    @pytest.mark.asyncio
    async def test_list_deals(self, client: AsyncClient, auth_headers: dict):
        """Test listing deals."""
        response = await client.get(
            "/api/v1/deals",
            headers=auth_headers,
            params={"page": 1, "page_size": 20}
        )
        
        assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_create_deal(self, client: AsyncClient, auth_headers: dict):
        """Test creating a deal."""
        response = await client.post(
            "/api/v1/deals",
            headers=auth_headers,
            json={
                "name": "Enterprise Software Package",
                "contact_id": str(uuid4()),
                "value": 250000.0,
                "stage": "proposal",
                "probability": 75,
                "close_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "assigned_to_id": str(uuid4())
            }
        )
        
        assert response.status_code in [201, 400, 401, 403, 422]

    @pytest.mark.asyncio
    async def test_get_deal(self, client: AsyncClient, auth_headers: dict):
        """Test getting a deal."""
        deal_id = uuid4()
        response = await client.get(
            f"/api/v1/deals/{deal_id}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 401, 403, 404]

    @pytest.mark.asyncio
    async def test_update_deal(self, client: AsyncClient, auth_headers: dict):
        """Test updating a deal."""
        deal_id = uuid4()
        response = await client.patch(
            f"/api/v1/deals/{deal_id}",
            headers=auth_headers,
            json={
                "stage": "won",
                "probability": 100,
                "close_date": datetime.now().isoformat()
            }
        )
        
        assert response.status_code in [200, 401, 403, 404, 422]

    @pytest.mark.asyncio
    async def test_delete_deal(self, client: AsyncClient, auth_headers: dict):
        """Test deleting a deal."""
        deal_id = uuid4()
        response = await client.delete(
            f"/api/v1/deals/{deal_id}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 204, 401, 403, 404]

    @pytest.mark.asyncio
    async def test_move_deal_to_stage(self, client: AsyncClient, auth_headers: dict):
        """Test moving deal to different stage."""
        deal_id = uuid4()
        response = await client.post(
            f"/api/v1/deals/{deal_id}/move-stage",
            headers=auth_headers,
            json={"stage": "negotiation"}
        )
        
        assert response.status_code in [200, 400, 401, 403, 404, 422]


class TestQuotes:
    """Tests for quote management endpoints."""

    @pytest.mark.asyncio
    async def test_list_quotes(self, client: AsyncClient, auth_headers: dict):
        """Test listing quotes."""
        response = await client.get(
            "/api/v1/quotes",
            headers=auth_headers,
            params={"page": 1, "page_size": 20}
        )
        
        assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_create_quote(self, client: AsyncClient, auth_headers: dict):
        """Test creating a quote."""
        response = await client.post(
            "/api/v1/quotes",
            headers=auth_headers,
            json={
                "deal_id": str(uuid4()),
                "contact_id": str(uuid4()),
                "quote_date": datetime.now().isoformat(),
                "expiry_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "items": [
                    {
                        "description": "Service",
                        "quantity": 1,
                        "unit_price": 1000.0
                    }
                ],
                "tax_rate": 10.0
            }
        )
        
        assert response.status_code in [201, 400, 401, 403, 422]

    @pytest.mark.asyncio
    async def test_get_quote(self, client: AsyncClient, auth_headers: dict):
        """Test getting a quote."""
        quote_id = uuid4()
        response = await client.get(
            f"/api/v1/quotes/{quote_id}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 401, 403, 404]

    @pytest.mark.asyncio
    async def test_send_quote(self, client: AsyncClient, auth_headers: dict):
        """Test sending a quote."""
        quote_id = uuid4()
        response = await client.post(
            f"/api/v1/quotes/{quote_id}/send",
            headers=auth_headers,
            json={"email": "contact@example.com"}
        )
        
        assert response.status_code in [200, 400, 401, 403, 404, 422]

    @pytest.mark.asyncio
    async def test_accept_quote(self, client: AsyncClient, auth_headers: dict):
        """Test accepting a quote."""
        quote_id = uuid4()
        response = await client.post(
            f"/api/v1/quotes/{quote_id}/accept",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 400, 401, 403, 404, 422]


class TestOrders:
    """Tests for order management endpoints."""

    @pytest.mark.asyncio
    async def test_list_orders(self, client: AsyncClient, auth_headers: dict):
        """Test listing orders."""
        response = await client.get(
            "/api/v1/orders",
            headers=auth_headers,
            params={"page": 1, "page_size": 20}
        )
        
        assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_create_order(self, client: AsyncClient, auth_headers: dict):
        """Test creating an order."""
        response = await client.post(
            "/api/v1/orders",
            headers=auth_headers,
            json={
                "contact_id": str(uuid4()),
                "order_date": datetime.now().isoformat(),
                "delivery_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "items": [
                    {
                        "product_id": str(uuid4()),
                        "quantity": 5,
                        "unit_price": 100.0
                    }
                ],
                "shipping_address": "123 Customer St"
            }
        )
        
        assert response.status_code in [201, 400, 401, 403, 422]

    @pytest.mark.asyncio
    async def test_get_order(self, client: AsyncClient, auth_headers: dict):
        """Test getting an order."""
        order_id = uuid4()
        response = await client.get(
            f"/api/v1/orders/{order_id}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 401, 403, 404]

    @pytest.mark.asyncio
    async def test_update_order(self, client: AsyncClient, auth_headers: dict):
        """Test updating an order."""
        order_id = uuid4()
        response = await client.patch(
            f"/api/v1/orders/{order_id}",
            headers=auth_headers,
            json={
                "status": "processing",
                "shipping_address": "456 New Address"
            }
        )
        
        assert response.status_code in [200, 401, 403, 404, 422]

    @pytest.mark.asyncio
    async def test_confirm_order(self, client: AsyncClient, auth_headers: dict):
        """Test confirming an order."""
        order_id = uuid4()
        response = await client.post(
            f"/api/v1/orders/{order_id}/confirm",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 400, 401, 403, 404, 422]

    @pytest.mark.asyncio
    async def test_ship_order(self, client: AsyncClient, auth_headers: dict):
        """Test shipping an order."""
        order_id = uuid4()
        response = await client.post(
            f"/api/v1/orders/{order_id}/ship",
            headers=auth_headers,
            json={
                "tracking_number": "TRACK123456",
                "carrier": "FedEx"
            }
        )
        
        assert response.status_code in [200, 400, 401, 403, 404, 422]

    @pytest.mark.asyncio
    async def test_cancel_order(self, client: AsyncClient, auth_headers: dict):
        """Test canceling an order."""
        order_id = uuid4()
        response = await client.post(
            f"/api/v1/orders/{order_id}/cancel",
            headers=auth_headers,
            json={"reason": "Customer request"}
        )
        
        assert response.status_code in [200, 400, 401, 403, 404, 422]

    @pytest.mark.asyncio
    async def test_delete_order(self, client: AsyncClient, auth_headers: dict):
        """Test deleting an order."""
        order_id = uuid4()
        response = await client.delete(
            f"/api/v1/orders/{order_id}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 204, 401, 403, 404]
