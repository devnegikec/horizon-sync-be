import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from httpx import AsyncClient, ASGITransport
from shared.database import get_async_session
from shared.database.base import Base
from shared.config import settings
from shared.security.jwt import create_access_token
from uuid import uuid4
import os

# Test database configuration
# Use the same database URL but with test DB ideally.
# For now effectively reusing the dev DB but wrapping in transactions that rollback.
# Async sqlalchemy rollback-only tests can be tricky.
# We will use the existing DB connection but try to isolate tests if possible.

@pytest_asyncio.fixture(scope="session")
async def db_engine():
    """Create database engine for tests."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Creates a new database session for a test.
    Rolls back the session after the test is complete.
    """
    connection = await db_engine.connect()
    # Begin a transaction
    trans = await connection.begin()
    
    # Bind session to the connection
    session_maker = async_sessionmaker(
        bind=connection,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    session = session_maker()
    
    try:
        yield session
    finally:
        await session.close()
        await trans.rollback()
        await connection.close()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession, request) -> AsyncGenerator[AsyncClient, None]:
    """
    Create a test client with overridden database dependency.
    This fixture selects the appropriate FastAPI app based on the test path.
    """
    test_path = str(request.node.fspath)
    
    if "test_auth_service" in test_path:
        from services.auth.main import app as target_app
    elif "test_user_management" in test_path:
        from services.user_management.main import app as target_app
    elif "test_billing" in test_path:
        from services.billing.main import app as target_app
    elif "test_inventory" in test_path:
        from services.inventory.main import app as target_app
    elif "test_lead_to_order" in test_path:
        from services.lead_to_order.main import app as target_app
    elif "test_support_ticket" in test_path:
        from services.support_ticket.main import app as target_app
    else:
        # Default to user_management
        from services.user_management.main import app as target_app
    
    async def override_get_db():
        yield db_session

    target_app.dependency_overrides[get_async_session] = override_get_db
    
    # Use ASGITransport for newer httpx versions with FastAPI
    transport = ASGITransport(app=target_app)
    
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    target_app.dependency_overrides.clear()


@pytest.fixture
def auth_headers() -> dict:
    """
    Generate auth headers for a test user.
    Returns a dictionary with Authorization header containing JWT token.
    """
    user_id = uuid4()
    org_id = uuid4()
    token = create_access_token(
        user_id=str(user_id),
        organization_id=str(org_id),
        role="owner",
        permissions=["*"]
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_id() -> uuid4:
    """Fixture to provide a test user ID."""
    return uuid4()


@pytest.fixture
def org_id() -> uuid4:
    """Fixture to provide a test organization ID."""
    return uuid4()


@pytest.fixture
def team_id() -> uuid4:
    """Fixture to provide a test team ID."""
    return uuid4()


# Pytest configuration
pytest_plugins = []


def pytest_collection_modifyitems(config, items):
    """Automatically mark async tests."""
    for item in items:
        if hasattr(item, "obj"):
            if hasattr(item.obj, "_pytestfixturefunction"):
                continue
            # Mark all async test functions
            if hasattr(item.obj, "__name__") and "test_" in item.obj.__name__:
                item.add_marker(pytest.mark.asyncio)
