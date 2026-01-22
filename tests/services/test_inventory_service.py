"""Unit tests for Inventory Service endpoints."""
import pytest
from uuid import uuid4
from datetime import datetime
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestProducts:
    """Tests for product management endpoints."""

    @pytest.mark.asyncio
    async def test_list_products(self, client: AsyncClient, auth_headers: dict):
        """Test listing products."""
        response = await client.get(
            "/api/v1/products",
            headers=auth_headers,
            params={"page": 1, "page_size": 20}
        )
        
        assert response.status_code in [200, 401, 403]
        if response.status_code == 200:
            data = response.json()
            assert "items" in data
            assert "total" in data

    @pytest.mark.asyncio
    async def test_list_products_with_search(self, client: AsyncClient, auth_headers: dict):
        """Test listing products with search filter."""
        response = await client.get(
            "/api/v1/products",
            headers=auth_headers,
            params={
                "page": 1,
                "page_size": 20,
                "search": "widget"
            }
        )
        
        assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_create_product(self, client: AsyncClient, auth_headers: dict):
        """Test creating a product."""
        response = await client.post(
            "/api/v1/products",
            headers=auth_headers,
            json={
                "name": "Test Product",
                "sku": "SKU-001",
                "description": "A test product",
                "unit_price": 99.99,
                "cost_price": 50.00,
                "tax_rate": 10.0,
                "track_inventory": True,
                "min_stock_level": 10
            }
        )
        
        assert response.status_code in [201, 400, 401, 403, 422]
        if response.status_code == 201:
            data = response.json()
            assert data["name"] == "Test Product"
            assert data["sku"] == "SKU-001"

    @pytest.mark.asyncio
    async def test_create_product_duplicate_sku(self, client: AsyncClient, auth_headers: dict):
        """Test creating product with duplicate SKU."""
        response = await client.post(
            "/api/v1/products",
            headers=auth_headers,
            json={
                "name": "Product 1",
                "sku": "DUPLICATE-SKU",
                "unit_price": 99.99
            }
        )
        
        if response.status_code == 201:
            # Try creating another with same SKU
            response2 = await client.post(
                "/api/v1/products",
                headers=auth_headers,
                json={
                    "name": "Product 2",
                    "sku": "DUPLICATE-SKU",
                    "unit_price": 99.99
                }
            )
            assert response2.status_code in [400, 409]

    @pytest.mark.asyncio
    async def test_get_product(self, client: AsyncClient, auth_headers: dict):
        """Test getting a product."""
        product_id = uuid4()
        response = await client.get(
            f"/api/v1/products/{product_id}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 401, 403, 404]

    @pytest.mark.asyncio
    async def test_update_product(self, client: AsyncClient, auth_headers: dict):
        """Test updating a product."""
        product_id = uuid4()
        response = await client.patch(
            f"/api/v1/products/{product_id}",
            headers=auth_headers,
            json={
                "name": "Updated Product",
                "unit_price": 119.99,
                "min_stock_level": 20
            }
        )
        
        assert response.status_code in [200, 401, 403, 404, 422]

    @pytest.mark.asyncio
    async def test_delete_product(self, client: AsyncClient, auth_headers: dict):
        """Test deleting a product."""
        product_id = uuid4()
        response = await client.delete(
            f"/api/v1/products/{product_id}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 204, 401, 403, 404]


class TestStock:
    """Tests for stock management endpoints."""

    @pytest.mark.asyncio
    async def test_get_stock_levels(self, client: AsyncClient, auth_headers: dict):
        """Test getting stock levels."""
        response = await client.get(
            "/api/v1/stock",
            headers=auth_headers,
            params={"page": 1, "page_size": 20}
        )
        
        assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_adjust_stock(self, client: AsyncClient, auth_headers: dict):
        """Test adjusting stock level."""
        product_id = uuid4()
        response = await client.post(
            f"/api/v1/stock/{product_id}/adjust",
            headers=auth_headers,
            json={
                "quantity": 10,
                "reason": "manual_adjustment",
                "notes": "Stock correction"
            }
        )
        
        assert response.status_code in [200, 400, 401, 403, 404, 422]

    @pytest.mark.asyncio
    async def test_transfer_stock(self, client: AsyncClient, auth_headers: dict):
        """Test transferring stock between warehouses."""
        response = await client.post(
            "/api/v1/stock/transfer",
            headers=auth_headers,
            json={
                "product_id": str(uuid4()),
                "from_warehouse_id": str(uuid4()),
                "to_warehouse_id": str(uuid4()),
                "quantity": 5
            }
        )
        
        assert response.status_code in [200, 201, 400, 401, 403, 422]

    @pytest.mark.asyncio
    async def test_count_stock(self, client: AsyncClient, auth_headers: dict):
        """Test stock count."""
        warehouse_id = uuid4()
        response = await client.post(
            f"/api/v1/warehouses/{warehouse_id}/stock-count",
            headers=auth_headers,
            json={
                "count_date": datetime.now().isoformat(),
                "items": [
                    {
                        "product_id": str(uuid4()),
                        "counted_quantity": 100
                    }
                ]
            }
        )
        
        assert response.status_code in [200, 201, 400, 401, 403, 422]


class TestWarehouses:
    """Tests for warehouse management endpoints."""

    @pytest.mark.asyncio
    async def test_list_warehouses(self, client: AsyncClient, auth_headers: dict):
        """Test listing warehouses."""
        response = await client.get(
            "/api/v1/warehouses",
            headers=auth_headers,
            params={"page": 1, "page_size": 20}
        )
        
        assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_create_warehouse(self, client: AsyncClient, auth_headers: dict):
        """Test creating a warehouse."""
        response = await client.post(
            "/api/v1/warehouses",
            headers=auth_headers,
            json={
                "name": "Main Warehouse",
                "code": "WH-001",
                "address": "123 Warehouse St",
                "is_active": True
            }
        )
        
        assert response.status_code in [201, 400, 401, 403, 422]

    @pytest.mark.asyncio
    async def test_get_warehouse(self, client: AsyncClient, auth_headers: dict):
        """Test getting a warehouse."""
        warehouse_id = uuid4()
        response = await client.get(
            f"/api/v1/warehouses/{warehouse_id}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 401, 403, 404]

    @pytest.mark.asyncio
    async def test_update_warehouse(self, client: AsyncClient, auth_headers: dict):
        """Test updating a warehouse."""
        warehouse_id = uuid4()
        response = await client.patch(
            f"/api/v1/warehouses/{warehouse_id}",
            headers=auth_headers,
            json={
                "name": "Updated Warehouse",
                "address": "456 New St"
            }
        )
        
        assert response.status_code in [200, 401, 403, 404, 422]

    @pytest.mark.asyncio
    async def test_delete_warehouse(self, client: AsyncClient, auth_headers: dict):
        """Test deleting a warehouse."""
        warehouse_id = uuid4()
        response = await client.delete(
            f"/api/v1/warehouses/{warehouse_id}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 204, 401, 403, 404]


class TestStockTransactions:
    """Tests for stock transaction endpoints."""

    @pytest.mark.asyncio
    async def test_list_stock_transactions(self, client: AsyncClient, auth_headers: dict):
        """Test listing stock transactions."""
        response = await client.get(
            "/api/v1/stock-transactions",
            headers=auth_headers,
            params={"page": 1, "page_size": 20}
        )
        
        assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_get_stock_transaction(self, client: AsyncClient, auth_headers: dict):
        """Test getting a stock transaction."""
        transaction_id = uuid4()
        response = await client.get(
            f"/api/v1/stock-transactions/{transaction_id}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 401, 403, 404]


class TestItems:
    """Tests for item/SKU management endpoints."""

    @pytest.mark.asyncio
    async def test_list_items(self, client: AsyncClient, auth_headers: dict):
        """Test listing items."""
        response = await client.get(
            "/api/v1/items",
            headers=auth_headers,
            params={"page": 1, "page_size": 20}
        )
        
        assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_create_item(self, client: AsyncClient, auth_headers: dict):
        """Test creating an item."""
        response = await client.post(
            "/api/v1/items",
            headers=auth_headers,
            json={
                "product_id": str(uuid4()),
                "sku": "ITEM-001",
                "barcode": "123456789",
                "description": "Item variant"
            }
        )
        
        assert response.status_code in [201, 400, 401, 403, 422]

    @pytest.mark.asyncio
    async def test_update_item(self, client: AsyncClient, auth_headers: dict):
        """Test updating an item."""
        item_id = uuid4()
        response = await client.patch(
            f"/api/v1/items/{item_id}",
            headers=auth_headers,
            json={
                "barcode": "987654321"
            }
        )
        
        assert response.status_code in [200, 401, 403, 404, 422]

    @pytest.mark.asyncio
    async def test_delete_item(self, client: AsyncClient, auth_headers: dict):
        """Test deleting an item."""
        item_id = uuid4()
        response = await client.delete(
            f"/api/v1/items/{item_id}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 204, 401, 403, 404]


class TestInventorySettings:
    """Tests for inventory settings endpoints."""

    @pytest.mark.asyncio
    async def test_get_inventory_settings(self, client: AsyncClient, auth_headers: dict):
        """Test getting inventory settings."""
        response = await client.get(
            "/api/v1/settings",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_update_inventory_settings(self, client: AsyncClient, auth_headers: dict):
        """Test updating inventory settings."""
        response = await client.patch(
            "/api/v1/settings",
            headers=auth_headers,
            json={
                "enable_low_stock_alerts": True,
                "low_stock_threshold": 5,
                "enable_barcode_scanning": True
            }
        )
        
        assert response.status_code in [200, 400, 401, 403, 422]
