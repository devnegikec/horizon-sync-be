# Test Execution Guide

This guide explains how to run the comprehensive unit tests for the Horizon Sync ERP project.

## Prerequisites

Ensure you have the following installed:

```bash
pip install pytest pytest-asyncio pytest-cov httpx sqlalchemy
```

Or install from requirements file:

```bash
pip install -r requirements.txt
```

## Quick Start

### Run All Tests

```bash
pytest tests/ -v
```

This will run all tests in the `tests/` directory with verbose output.

### Run Tests by Service

Each service has its own test module:

```bash
# Auth Service
pytest tests/services/test_auth_service.py -v

# User Management Service
pytest tests/services/test_user_management_service.py -v

# Billing Service
pytest tests/services/test_billing_service.py -v

# Inventory Service
pytest tests/services/test_inventory_service.py -v

# Lead to Order Service
pytest tests/services/test_lead_to_order_service.py -v

# Support Ticket Service
pytest tests/services/test_support_ticket_service.py -v
```

## Advanced Testing Options

### Run Specific Test Class

```bash
pytest tests/services/test_auth_service.py::TestAuthLogin -v
```

### Run Specific Test Method

```bash
pytest tests/services/test_auth_service.py::TestAuthLogin::test_login_success -v
```

### Run Tests Matching a Pattern

```bash
pytest tests/ -k "login" -v
pytest tests/ -k "create" -v
pytest tests/ -k "delete" -v
```

### Run Tests with Coverage Report

```bash
# Terminal report
pytest tests/ --cov=services --cov=shared --cov-report=term-missing

# HTML report
pytest tests/ --cov=services --cov=shared --cov-report=html
# Open htmlcov/index.html in browser
```

### Run Tests with Different Output Formats

```bash
# Short summary
pytest tests/ -v --tb=short

# No output capture (print statements shown)
pytest tests/ -v -s

# Quiet mode (only show failures)
pytest tests/ -q
```

### Run Tests in Parallel

Install pytest-xdist:

```bash
pip install pytest-xdist
```

Then run:

```bash
# Run with 4 workers
pytest tests/ -n 4 -v

# Run with auto-detected CPU count
pytest tests/ -n auto -v
```

### Run Only Failed Tests (from last run)

```bash
pytest tests/ --lf -v
```

### Run Tests with Markers

```bash
# Run only async tests
pytest tests/ -m asyncio -v

# Run only auth service tests
pytest tests/ -m auth -v

# Run tests except slow ones
pytest tests/ -m "not slow" -v
```

## Debugging Tests

### Show Print Statements

```bash
pytest tests/ -v -s
```

### Show Local Variables on Failure

```bash
pytest tests/ -v -l
```

### Drop into Debugger on Failure

```bash
pytest tests/ -v --pdb
```

### Drop into Debugger on First Failure

```bash
pytest tests/ -v --pdbcls=IPython.terminal.debugger:TerminalPdb --pdb
```

### Verbose Traceback

```bash
pytest tests/ -v --tb=long
```

### Generate JUnit XML Report

```bash
pytest tests/ -v --junit-xml=test-results.xml
```

## Environment Variables

Set environment variables before running tests:

```bash
# Use test database
export DATABASE_URL=postgresql://user:password@localhost/test_db

# Set log level
export LOG_LEVEL=DEBUG

# Disable HTTPS requirement
export ENVIRONMENT=development
```

### Windows PowerShell

```powershell
$env:DATABASE_URL="postgresql://user:password@localhost/test_db"
$env:LOG_LEVEL="DEBUG"
pytest tests/ -v
```

### Windows CMD

```cmd
set DATABASE_URL=postgresql://user:password@localhost/test_db
set LOG_LEVEL=DEBUG
pytest tests/ -v
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost/test_db
        run: |
          pytest tests/ --cov=services --cov=shared --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
        with:
          files: ./coverage.xml
```

## Performance Testing

### Measure Test Execution Time

```bash
pytest tests/ -v --durations=10
```

Shows the 10 slowest tests.

### Limit Test Duration

Install pytest-timeout:

```bash
pip install pytest-timeout
```

Set timeout in pytest.ini or via command line:

```bash
pytest tests/ --timeout=30 -v
```

## Test Organization

### By Service

```bash
pytest tests/services/test_auth_service.py
pytest tests/services/test_billing_service.py
```

### By Test Class

```bash
pytest tests/services/test_auth_service.py::TestAuthLogin
pytest tests/services/test_billing_service.py::TestInvoices
```

### By Test Type

```bash
# Happy path tests
pytest tests/ -k "success" -v

# Error handling tests
pytest tests/ -k "error or invalid or unauthorized" -v

# CRUD operations
pytest tests/ -k "create or read or update or delete" -v
```

## Continuous Testing

### Watch Mode (with pytest-watch)

Install pytest-watch:

```bash
pip install pytest-watch
```

Run tests in watch mode:

```bash
ptw tests/ -- -v
```

Tests will re-run whenever files change.

## Test Configuration

Edit `pytest.ini` to customize test behavior:

```ini
[pytest]
# Add these options
addopts = 
    -v                                      # Verbose
    --strict-markers                        # Strict marker checking
    --tb=short                              # Short traceback format
    -ra                                     # Show summary
    --cov=services --cov=shared             # Coverage
    --cov-report=html --cov-report=term    # Reports
```

## Troubleshooting

### Database Connection Error

```bash
# Check database connection
psql postgresql://user:password@localhost/database_name

# Or use TEST_DATABASE_URL
export TEST_DATABASE_URL=postgresql://user:password@localhost/test_db
pytest tests/ -v
```

### Import Errors

```bash
# Ensure PYTHONPATH includes project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/ -v
```

### Async Test Issues

Ensure `pytest-asyncio` is installed:

```bash
pip install pytest-asyncio>=0.21.0
```

### Port Already in Use

If test server can't start:

```bash
# Kill existing process on port
lsof -ti:8000 | xargs kill -9
pytest tests/ -v
```

## Best Practices

1. **Run tests before committing**
   ```bash
   pytest tests/ -v --tb=short
   ```

2. **Check coverage regularly**
   ```bash
   pytest tests/ --cov=services --cov-report=html
   open htmlcov/index.html
   ```

3. **Run tests in CI/CD pipeline** (see CI/CD Integration section)

4. **Keep tests isolated** - Use fixtures and database rollback

5. **Name tests clearly** - `test_<feature>_<scenario>`

6. **Test both success and error cases**

7. **Use markers for test categorization**

8. **Run tests frequently** - Add to pre-commit hooks:
   ```bash
   # .git/hooks/pre-commit
   #!/bin/bash
   pytest tests/ --tb=short || exit 1
   ```

## Test Statistics

After running tests, you can generate reports:

```bash
# Coverage report
pytest tests/ --cov=services --cov-report=html

# JUnit XML
pytest tests/ --junit-xml=results.xml

# JSON report (with pytest-json-report)
pip install pytest-json-report
pytest tests/ --json-report --json-report-file=report.json
```

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio)
- [FastAPI Testing](https://fastapi.tiangolo.com/advanced/testing-dependencies/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/orm/session_basics.html#testing)
