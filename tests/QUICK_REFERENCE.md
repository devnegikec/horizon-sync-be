# Quick Reference: Running Tests

## Most Common Commands

```bash
# Run all tests
pytest tests/ -v

# Run tests for one service
pytest tests/services/test_auth_service.py -v
pytest tests/services/test_user_management_service.py -v
pytest tests/services/test_billing_service.py -v
pytest tests/services/test_inventory_service.py -v
pytest tests/services/test_lead_to_order_service.py -v
pytest tests/services/test_support_ticket_service.py -v

# Run specific test class
pytest tests/services/test_auth_service.py::TestAuthLogin -v

# Run specific test
pytest tests/services/test_auth_service.py::TestAuthLogin::test_login_success -v

# Run tests matching pattern
pytest tests/ -k "login" -v
pytest tests/ -k "create" -v
pytest tests/ -k "delete" -v

# Run with coverage report
pytest tests/ --cov=services --cov=shared --cov-report=html

# Run in parallel (faster)
pytest tests/ -n auto -v

# Debug mode (stop on first failure)
pytest tests/ -x -v

# Show print statements
pytest tests/ -s -v
```

## Test Files by Service

| Service | Test File | Test Cases |
|---------|-----------|-----------|
| Auth | `tests/services/test_auth_service.py` | 128 |
| User Management | `tests/services/test_user_management_service.py` | 130 |
| Billing | `tests/services/test_billing_service.py` | 115 |
| Inventory | `tests/services/test_inventory_service.py` | 110 |
| Lead to Order | `tests/services/test_lead_to_order_service.py` | 135 |
| Support Ticket | `tests/services/test_support_ticket_service.py` | 150 |

## Available Fixtures

```python
@pytest.mark.asyncio
async def test_example(
    client: AsyncClient,          # HTTP client
    auth_headers: dict,           # JWT auth headers
    db_session: AsyncSession,     # Database connection
    user_id: UUID,               # Test user ID
    org_id: UUID,                # Test org ID
    team_id: UUID                # Test team ID
):
    pass
```

## Writing a New Test

```python
@pytest.mark.asyncio
async def test_create_user_success(client: AsyncClient, auth_headers: dict):
    """Test successfully creating a user."""
    response = await client.post(
        "/api/v1/users",
        headers=auth_headers,
        json={
            "email": "newuser@example.com",
            "first_name": "John",
            "last_name": "Doe"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
```

## Assertion Helpers

```python
from tests.helpers import TestHelper

# Check status code
TestHelper.assert_status_in(response, [200, 201])
TestHelper.assert_success(response)
TestHelper.assert_error(response)
TestHelper.assert_unauthorized(response)
TestHelper.assert_forbidden(response)
TestHelper.assert_not_found(response)

# Check response content
TestHelper.assert_response_has_keys(response, ["id", "email"])
TestHelper.assert_paginated_response(response)

# Get JSON
data = TestHelper.get_json_response(response)
```

## Test Data Factories

```python
from tests.helpers import DataFactory

# Create test data
user_data = DataFactory.create_user_data(email="test@example.com")
product_data = DataFactory.create_product_data(sku="SKU-001")
invoice_data = DataFactory.create_invoice_data(invoice_no="INV-001")
lead_data = DataFactory.create_lead_data(title="New Lead")
ticket_data = DataFactory.create_ticket_data(subject="Issue Title")
```

## Database Helpers

```python
from tests.helpers import DatabaseHelper

# Check if record exists
exists = await DatabaseHelper.record_exists(
    db_session, 
    User, 
    email="test@example.com"
)

# Count records
count = await DatabaseHelper.count_records(db_session, User)

# Get records
users = await DatabaseHelper.get_records(db_session, User, limit=10)
```

## Test Organization

Tests are organized by service and then by feature:

```
tests/
├── services/
│   ├── test_auth_service.py
│   │   ├── TestAuthRegister
│   │   ├── TestAuthLogin
│   │   ├── TestAuthRefresh
│   │   ├── TestAuthLogout
│   │   ├── TestMFA
│   │   ├── TestPasswordReset
│   │   └── TestSessionManagement
│   │
│   ├── test_user_management_service.py
│   │   ├── TestUserProfile
│   │   ├── TestUserList
│   │   ├── TestUserManagement
│   │   ├── TestUserInvitation
│   │   ├── TestUserRole
│   │   ├── TestUserStatus
│   │   └── TestUserTeams
│   │
│   └── ... (other services)
```

## Common Test Scenarios

### Testing Success
```python
async def test_operation_success(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/v1/endpoint",
        headers=auth_headers,
        json={"field": "value"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["field"] == "value"
```

### Testing Errors
```python
async def test_operation_validation_error(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/v1/endpoint",
        headers=auth_headers,
        json={"invalid": "data"}
    )
    assert response.status_code in [400, 422]
```

### Testing Authentication
```python
async def test_requires_authentication(client: AsyncClient):
    response = await client.get("/api/v1/protected-endpoint")
    assert response.status_code == 401
```

### Testing with Database
```python
async def test_with_database(client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
    # Make API call
    response = await client.post(
        "/api/v1/users",
        headers=auth_headers,
        json={"email": "test@example.com"}
    )
    
    # Verify in database
    from sqlalchemy import select
    result = await db_session.execute(
        select(User).where(User.email == "test@example.com")
    )
    user = result.scalar_one_or_none()
    assert user is not None
```

### Testing Pagination
```python
async def test_list_with_pagination(client: AsyncClient, auth_headers: dict):
    response = await client.get(
        "/api/v1/items",
        headers=auth_headers,
        params={"page": 1, "page_size": 20}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Import errors | `export PYTHONPATH="${PYTHONPATH}:$(pwd)"` |
| Database connection | Check `DATABASE_URL` in `.env` |
| Async test issues | Install latest `pytest-asyncio` |
| Slow tests | Use `pytest tests/ -n auto` for parallel |
| Port already in use | Kill existing process or use different port |

## Documentation

- **Full guide**: `tests/UNIT_TESTS_README.md`
- **Execution guide**: `tests/TEST_EXECUTION_GUIDE.md`
- **Implementation details**: `tests/IMPLEMENTATION_SUMMARY.md`
- **API docs**: `services/*/api/*/` files

## Tips & Tricks

1. **Run failing tests first**
   ```bash
   pytest tests/ --lf
   ```

2. **Run slow tests first**
   ```bash
   pytest tests/ --durations=5
   ```

3. **Get detailed error info**
   ```bash
   pytest tests/ -vv --tb=long
   ```

4. **Run with debug output**
   ```bash
   pytest tests/ -s -v
   ```

5. **Stop on first failure**
   ```bash
   pytest tests/ -x
   ```

6. **Show fixture setup/teardown**
   ```bash
   pytest tests/ --setup-show -v
   ```

## Environment Setup

Before running tests, ensure:

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**
   ```bash
   export DATABASE_URL=postgresql://user:password@localhost/db
   export LOG_LEVEL=DEBUG
   ```

3. **Start database**
   ```bash
   docker-compose up postgres
   ```

4. **Run migrations** (if needed)
   ```bash
   alembic upgrade head
   ```

5. **Run tests**
   ```bash
   pytest tests/ -v
   ```

## Performance Targets

- Single test: < 1 second
- Full suite: 5-10 minutes
- With coverage: 10-15 minutes
- Parallel (4 workers): 2-4 minutes

## Getting Help

1. **Check documentation**: `tests/UNIT_TESTS_README.md`
2. **See examples**: Look at existing test files
3. **Use helpers**: `tests/helpers.py` has utilities
4. **Check conftest**: `tests/conftest.py` has fixtures
5. **Read pytest docs**: https://docs.pytest.org/

---

**Last Updated**: 2026-01-21
**Total Tests**: 300+
**Services Covered**: 6
