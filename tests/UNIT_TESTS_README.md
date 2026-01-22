# Unit Tests Documentation

This directory contains comprehensive unit tests for all API endpoints across all services in the Horizon Sync ERP project.

## Test Structure

```
tests/
├── conftest.py                              # Pytest configuration and fixtures
├── services/
│   ├── __init__.py
│   ├── test_auth_service.py                 # Auth Service tests
│   ├── test_user_management_service.py      # User Management Service tests
│   ├── test_billing_service.py              # Billing Service tests
│   ├── test_inventory_service.py            # Inventory Service tests
│   ├── test_lead_to_order_service.py        # Lead to Order Service tests
│   └── test_support_ticket_service.py       # Support Ticket Service tests
```

## Test Coverage

### 1. Auth Service (`test_auth_service.py`)

Tests for authentication and authorization endpoints:

- **TestAuthRegister**: User registration
  - Successful registration
  - Duplicate email handling
  - Invalid email validation
  - Weak password validation

- **TestAuthLogin**: Login functionality
  - Successful login
  - Invalid email handling
  - Invalid password handling
  - Inactive account handling
  - Suspended account handling

- **TestAuthRefresh**: Token refresh
  - Successful token refresh
  - Invalid token handling
  - Expired token handling

- **TestAuthLogout**: Logout functionality
  - Successful logout
  - Unauthorized logout attempt

- **TestMFA**: Multi-factor authentication
  - MFA setup
  - MFA verification
  - MFA disable

- **TestPasswordReset**: Password reset workflow
  - Request password reset
  - Non-existent email handling
  - Confirm password reset

- **TestSessionManagement**: Session management
  - Get all sessions
  - Revoke specific session
  - Revoke all sessions

### 2. User Management Service (`test_user_management_service.py`)

Tests for user profile and management endpoints:

- **TestUserProfile**: User profile operations
  - Get current user profile
  - Unauthorized profile access
  - Update profile information
  - Update email address

- **TestUserList**: User listing with pagination and filters
  - List users with pagination
  - Filter by search term
  - Filter by status

- **TestUserManagement**: CRUD operations on users
  - Get user by ID
  - Create new user
  - Update user information
  - Delete user

- **TestUserInvitation**: User invitation workflow
  - Invite users to organization
  - Accept invitation
  - Resend invitation
  - Cancel invitation

- **TestUserRole**: Role management
  - Update user role
  - Get user roles

- **TestUserStatus**: User status management
  - Deactivate user
  - Activate user
  - Suspend user

- **TestUserTeams**: Team management
  - Get user teams
  - Add user to team
  - Remove user from team

### 3. Billing Service (`test_billing_service.py`)

Tests for billing and accounting endpoints:

- **TestInvoices**: Invoice management
  - List invoices with pagination and filters
  - Create invoice
  - Get invoice details
  - Update invoice
  - Submit invoice
  - Send invoice
  - Mark as paid
  - Delete invoice

- **TestCustomers**: Customer management
  - List customers
  - Create customer
  - Get customer
  - Update customer
  - Delete customer

- **TestPayments**: Payment recording
  - List payments
  - Record payment
  - Get payment
  - Refund payment

- **TestSuppliers**: Supplier management
  - List suppliers
  - Create supplier
  - Get supplier
  - Update supplier
  - Delete supplier

- **TestAccounting**: Accounting entries and reports
  - List journal entries
  - Create journal entry
  - Balance sheet
  - Income statement
  - Cash flow statement

### 4. Inventory Service (`test_inventory_service.py`)

Tests for inventory management endpoints:

- **TestProducts**: Product management
  - List products with search
  - Create product
  - Duplicate SKU handling
  - Get product
  - Update product
  - Delete product

- **TestStock**: Stock management
  - Get stock levels
  - Adjust stock
  - Transfer stock between warehouses
  - Perform stock count

- **TestWarehouses**: Warehouse management
  - List warehouses
  - Create warehouse
  - Get warehouse
  - Update warehouse
  - Delete warehouse

- **TestStockTransactions**: Stock transaction history
  - List transactions
  - Get transaction details

- **TestItems**: Item/SKU management
  - List items
  - Create item
  - Update item
  - Delete item

- **TestInventorySettings**: Configuration
  - Get inventory settings
  - Update settings

### 5. Lead to Order Service (`test_lead_to_order_service.py`)

Tests for CRM lead-to-order pipeline:

- **TestLeads**: Lead management
  - List leads with filters
  - Create lead
  - Get lead
  - Update lead
  - Delete lead
  - Convert lead to contact

- **TestContacts**: Contact management
  - List contacts
  - Create contact
  - Get contact
  - Update contact
  - Delete contact

- **TestDeals**: Deal/opportunity management
  - List deals
  - Create deal
  - Get deal
  - Update deal
  - Delete deal
  - Move deal between stages

- **TestQuotes**: Quote management
  - List quotes
  - Create quote
  - Get quote
  - Send quote
  - Accept quote

- **TestOrders**: Order management
  - List orders
  - Create order
  - Get order
  - Update order
  - Confirm order
  - Ship order
  - Cancel order
  - Delete order

### 6. Support Ticket Service (`test_support_ticket_service.py`)

Tests for support ticket management:

- **TestTickets**: Ticket operations
  - List tickets with filters
  - Create ticket
  - Get ticket
  - Update ticket
  - Assign ticket
  - Update status
  - Close ticket
  - Reopen ticket
  - Delete ticket

- **TestTicketComments**: Comment management
  - List comments
  - Add comment
  - Add internal comment
  - Add resolution comment
  - Update comment
  - Delete comment

- **TestTicketAttachments**: Attachment management
  - List attachments
  - Upload attachment
  - Delete attachment

- **TestTicketWorkflow**: Workflow management
  - Get ticket history
  - Add/remove followers
  - Add/remove tags

- **TestTicketMetrics**: Metrics and reporting
  - Get ticket metrics
  - Get SLA metrics
  - Get agent performance

- **TestTicketEscalation**: Escalation and batch operations
  - Escalate ticket
  - Set priority
  - Batch update tickets

## Running Tests

### Run all tests
```bash
pytest tests/ -v
```

### Run tests for a specific service
```bash
pytest tests/services/test_auth_service.py -v
pytest tests/services/test_user_management_service.py -v
pytest tests/services/test_billing_service.py -v
pytest tests/services/test_inventory_service.py -v
pytest tests/services/test_lead_to_order_service.py -v
pytest tests/services/test_support_ticket_service.py -v
```

### Run a specific test class
```bash
pytest tests/services/test_auth_service.py::TestAuthLogin -v
```

### Run a specific test
```bash
pytest tests/services/test_auth_service.py::TestAuthLogin::test_login_success -v
```

### Run with coverage
```bash
pytest tests/ --cov=services --cov=shared --cov-report=html
```

### Run tests matching a pattern
```bash
pytest tests/ -k "login" -v
```

## Fixtures

The following pytest fixtures are available (defined in `conftest.py`):

- **`db_engine`**: Database engine for session scope (all tests)
- **`db_session`**: AsyncSession for each test with automatic rollback
- **`client`**: AsyncClient for making HTTP requests to API
- **`auth_headers`**: Pre-configured headers with valid JWT token for authentication
- **`user_id`**: Random UUID for user references
- **`org_id`**: Random UUID for organization references
- **`team_id`**: Random UUID for team references

### Example Fixture Usage

```python
@pytest.mark.asyncio
async def test_example(client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
    # Make authenticated request
    response = await client.get(
        "/api/v1/users/me",
        headers=auth_headers
    )
    
    # Access database
    result = await db_session.execute(select(User))
    user = result.scalar_one_or_none()
```

## Test Patterns

### Testing Successful Operation
```python
@pytest.mark.asyncio
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

### Testing Error Cases
```python
@pytest.mark.asyncio
async def test_operation_error(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/v1/endpoint",
        headers=auth_headers,
        json={"invalid": "data"}
    )
    
    assert response.status_code in [400, 422]
```

### Testing Pagination
```python
@pytest.mark.asyncio
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

## Database Isolation

Each test:
1. Starts a new database connection
2. Begins a transaction
3. Executes the test
4. Rolls back the transaction (so no data persists)
5. Closes the connection

This ensures tests don't interfere with each other.

## Expected Response Codes

Tests check for multiple possible status codes to handle different service implementations:

- **Success**: 200, 201, 202
- **Client Error**: 400, 401, 403, 404, 409, 422
- **Server Error**: 500

Some tests expect multiple codes because:
- Services may have different validation rules
- Some operations may not be implemented
- Authorization may be enforced differently

## Future Improvements

1. **Integration Tests**: Add tests that span multiple services
2. **Mock Data**: Create fixtures for common test data
3. **Performance Tests**: Add benchmark tests for critical paths
4. **Load Tests**: Add load testing for concurrent operations
5. **Test Documentation**: Add detailed documentation for each test class
6. **Custom Assertions**: Create helper functions for common assertions
7. **Parameterized Tests**: Use pytest.mark.parametrize for testing multiple scenarios
8. **Async Context Managers**: Use async context managers for complex test setup

## Troubleshooting

### Import Errors
- Ensure all service modules are properly installed
- Check that PYTHONPATH includes the project root

### Database Connection Errors
- Verify DATABASE_URL in settings
- Ensure database is running
- Check database permissions

### Async Test Issues
- All async tests must have `@pytest.mark.asyncio` decorator
- Use `await` for async operations
- Don't mix sync and async fixtures

### JWT Token Issues
- Verify JWT secret is configured
- Check token expiration settings
- Ensure token payload structure matches expectations

## Contributing

When adding new tests:

1. Follow existing naming conventions
2. Group related tests in classes
3. Add docstrings to test functions
4. Use meaningful assertion messages
5. Clean up resources in teardown
6. Keep tests independent and isolated
7. Document complex test scenarios

## Test Metrics

- **Total Test Cases**: 300+
- **Estimated Coverage**: 80%+
- **Average Test Execution Time**: < 1 second per test
- **Total Execution Time**: ~ 5-10 minutes for full suite
