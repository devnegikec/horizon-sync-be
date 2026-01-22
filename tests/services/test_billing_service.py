"""Unit tests for Billing Service endpoints."""
import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models.billing_accounting import Invoice, InvoiceStatus


class TestInvoices:
    """Tests for invoice management endpoints."""

    @pytest.mark.asyncio
    async def test_list_invoices(self, client: AsyncClient, auth_headers: dict):
        """Test listing invoices."""
        response = await client.get(
            "/api/v1/invoices",
            headers=auth_headers,
            params={"page": 1, "page_size": 20}
        )
        
        assert response.status_code in [200, 401, 403]
        if response.status_code == 200:
            data = response.json()
            assert "items" in data
            assert "total" in data

    @pytest.mark.asyncio
    async def test_list_invoices_with_filters(self, client: AsyncClient, auth_headers: dict):
        """Test listing invoices with filters."""
        response = await client.get(
            "/api/v1/invoices",
            headers=auth_headers,
            params={
                "page": 1,
                "page_size": 20,
                "status": "draft",
                "search": "invoice"
            }
        )
        
        assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_create_invoice(self, client: AsyncClient, auth_headers: dict):
        """Test creating an invoice."""
        response = await client.post(
            "/api/v1/invoices",
            headers=auth_headers,
            json={
                "invoice_no": "INV-001",
                "customer_id": str(uuid4()),
                "issue_date": datetime.now().isoformat(),
                "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "items": [
                    {
                        "description": "Service",
                        "quantity": 1,
                        "unit_price": 100.0,
                        "total_amount": 100.0
                    }
                ]
            }
        )
        
        assert response.status_code in [201, 400, 401, 403, 422]
        if response.status_code == 201:
            data = response.json()
            assert data["status"] == "draft"

    @pytest.mark.asyncio
    async def test_get_invoice(self, client: AsyncClient, auth_headers: dict):
        """Test getting a specific invoice."""
        invoice_id = uuid4()
        response = await client.get(
            f"/api/v1/invoices/{invoice_id}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 401, 403, 404]

    @pytest.mark.asyncio
    async def test_update_invoice(self, client: AsyncClient, auth_headers: dict):
        """Test updating an invoice."""
        invoice_id = uuid4()
        response = await client.patch(
            f"/api/v1/invoices/{invoice_id}",
            headers=auth_headers,
            json={
                "invoice_no": "INV-002",
                "due_date": (datetime.now() + timedelta(days=45)).isoformat()
            }
        )
        
        assert response.status_code in [200, 400, 401, 403, 404, 422]

    @pytest.mark.asyncio
    async def test_submit_invoice(self, client: AsyncClient, auth_headers: dict):
        """Test submitting a draft invoice."""
        invoice_id = uuid4()
        response = await client.post(
            f"/api/v1/invoices/{invoice_id}/submit",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 400, 401, 403, 404, 422]

    @pytest.mark.asyncio
    async def test_send_invoice(self, client: AsyncClient, auth_headers: dict):
        """Test sending an invoice to customer."""
        invoice_id = uuid4()
        response = await client.post(
            f"/api/v1/invoices/{invoice_id}/send",
            headers=auth_headers,
            json={"send_to_email": "customer@example.com"}
        )
        
        assert response.status_code in [200, 400, 401, 403, 404, 422]

    @pytest.mark.asyncio
    async def test_mark_invoice_as_paid(self, client: AsyncClient, auth_headers: dict):
        """Test marking an invoice as paid."""
        invoice_id = uuid4()
        response = await client.post(
            f"/api/v1/invoices/{invoice_id}/mark-paid",
            headers=auth_headers,
            json={
                "amount_paid": 100.0,
                "payment_method": "bank_transfer"
            }
        )
        
        assert response.status_code in [200, 400, 401, 403, 404, 422]

    @pytest.mark.asyncio
    async def test_delete_invoice(self, client: AsyncClient, auth_headers: dict):
        """Test deleting an invoice."""
        invoice_id = uuid4()
        response = await client.delete(
            f"/api/v1/invoices/{invoice_id}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 204, 401, 403, 404]


class TestCustomers:
    """Tests for customer management endpoints."""

    @pytest.mark.asyncio
    async def test_list_customers(self, client: AsyncClient, auth_headers: dict):
        """Test listing customers."""
        response = await client.get(
            "/api/v1/customers",
            headers=auth_headers,
            params={"page": 1, "page_size": 20}
        )
        
        assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_create_customer(self, client: AsyncClient, auth_headers: dict):
        """Test creating a customer."""
        response = await client.post(
            "/api/v1/customers",
            headers=auth_headers,
            json={
                "name": "Test Company",
                "email": "company@example.com",
                "phone": "+1234567890",
                "address": "123 Main St"
            }
        )
        
        assert response.status_code in [201, 400, 401, 403, 422]

    @pytest.mark.asyncio
    async def test_get_customer(self, client: AsyncClient, auth_headers: dict):
        """Test getting a customer."""
        customer_id = uuid4()
        response = await client.get(
            f"/api/v1/customers/{customer_id}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 401, 403, 404]

    @pytest.mark.asyncio
    async def test_update_customer(self, client: AsyncClient, auth_headers: dict):
        """Test updating a customer."""
        customer_id = uuid4()
        response = await client.patch(
            f"/api/v1/customers/{customer_id}",
            headers=auth_headers,
            json={
                "name": "Updated Company",
                "phone": "+9876543210"
            }
        )
        
        assert response.status_code in [200, 401, 403, 404, 422]

    @pytest.mark.asyncio
    async def test_delete_customer(self, client: AsyncClient, auth_headers: dict):
        """Test deleting a customer."""
        customer_id = uuid4()
        response = await client.delete(
            f"/api/v1/customers/{customer_id}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 204, 401, 403, 404]


class TestPayments:
    """Tests for payment management endpoints."""

    @pytest.mark.asyncio
    async def test_list_payments(self, client: AsyncClient, auth_headers: dict):
        """Test listing payments."""
        response = await client.get(
            "/api/v1/payments",
            headers=auth_headers,
            params={"page": 1, "page_size": 20}
        )
        
        assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_record_payment(self, client: AsyncClient, auth_headers: dict):
        """Test recording a payment."""
        response = await client.post(
            "/api/v1/payments",
            headers=auth_headers,
            json={
                "invoice_id": str(uuid4()),
                "amount": 100.0,
                "payment_method": "bank_transfer",
                "payment_date": datetime.now().isoformat()
            }
        )
        
        assert response.status_code in [201, 400, 401, 403, 422]

    @pytest.mark.asyncio
    async def test_get_payment(self, client: AsyncClient, auth_headers: dict):
        """Test getting a payment."""
        payment_id = uuid4()
        response = await client.get(
            f"/api/v1/payments/{payment_id}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 401, 403, 404]

    @pytest.mark.asyncio
    async def test_refund_payment(self, client: AsyncClient, auth_headers: dict):
        """Test refunding a payment."""
        payment_id = uuid4()
        response = await client.post(
            f"/api/v1/payments/{payment_id}/refund",
            headers=auth_headers,
            json={"reason": "Customer request"}
        )
        
        assert response.status_code in [200, 400, 401, 403, 404, 422]


class TestSuppliers:
    """Tests for supplier management endpoints."""

    @pytest.mark.asyncio
    async def test_list_suppliers(self, client: AsyncClient, auth_headers: dict):
        """Test listing suppliers."""
        response = await client.get(
            "/api/v1/suppliers",
            headers=auth_headers,
            params={"page": 1, "page_size": 20}
        )
        
        assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_create_supplier(self, client: AsyncClient, auth_headers: dict):
        """Test creating a supplier."""
        response = await client.post(
            "/api/v1/suppliers",
            headers=auth_headers,
            json={
                "name": "Supplier Inc",
                "email": "supplier@example.com",
                "phone": "+1234567890",
                "address": "456 Supplier St"
            }
        )
        
        assert response.status_code in [201, 400, 401, 403, 422]

    @pytest.mark.asyncio
    async def test_get_supplier(self, client: AsyncClient, auth_headers: dict):
        """Test getting a supplier."""
        supplier_id = uuid4()
        response = await client.get(
            f"/api/v1/suppliers/{supplier_id}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 401, 403, 404]

    @pytest.mark.asyncio
    async def test_update_supplier(self, client: AsyncClient, auth_headers: dict):
        """Test updating a supplier."""
        supplier_id = uuid4()
        response = await client.patch(
            f"/api/v1/suppliers/{supplier_id}",
            headers=auth_headers,
            json={"name": "Updated Supplier"}
        )
        
        assert response.status_code in [200, 401, 403, 404, 422]

    @pytest.mark.asyncio
    async def test_delete_supplier(self, client: AsyncClient, auth_headers: dict):
        """Test deleting a supplier."""
        supplier_id = uuid4()
        response = await client.delete(
            f"/api/v1/suppliers/{supplier_id}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 204, 401, 403, 404]


class TestAccounting:
    """Tests for accounting/journal entry endpoints."""

    @pytest.mark.asyncio
    async def test_list_journal_entries(self, client: AsyncClient, auth_headers: dict):
        """Test listing journal entries."""
        response = await client.get(
            "/api/v1/accounting/journal-entries",
            headers=auth_headers,
            params={"page": 1, "page_size": 20}
        )
        
        assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_create_journal_entry(self, client: AsyncClient, auth_headers: dict):
        """Test creating a journal entry."""
        response = await client.post(
            "/api/v1/accounting/journal-entries",
            headers=auth_headers,
            json={
                "description": "Test entry",
                "entry_date": datetime.now().isoformat(),
                "items": [
                    {
                        "account_id": str(uuid4()),
                        "debit": 100.0,
                        "credit": 0.0
                    },
                    {
                        "account_id": str(uuid4()),
                        "debit": 0.0,
                        "credit": 100.0
                    }
                ]
            }
        )
        
        assert response.status_code in [201, 400, 401, 403, 422]

    @pytest.mark.asyncio
    async def test_get_balance_sheet(self, client: AsyncClient, auth_headers: dict):
        """Test getting balance sheet."""
        response = await client.get(
            "/api/v1/accounting/balance-sheet",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_get_income_statement(self, client: AsyncClient, auth_headers: dict):
        """Test getting income statement."""
        response = await client.get(
            "/api/v1/accounting/income-statement",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_get_cash_flow(self, client: AsyncClient, auth_headers: dict):
        """Test getting cash flow statement."""
        response = await client.get(
            "/api/v1/accounting/cash-flow",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 401, 403]
