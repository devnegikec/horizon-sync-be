import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from shared.models.organization import Organization, OrganizationStatus
from shared.models.subscription import SubscriptionPlan, PlanType
from shared.security.jwt import create_access_token

@pytest.mark.asyncio
async def test_onboard_organization(client: AsyncClient, db_session: AsyncSession):
    # Ensure free plan exists
    plan = SubscriptionPlan(
        name="Free", code="free", price=0, 
        max_users=5, max_teams=1,
        features={}
    )
    db_session.add(plan)
    await db_session.commit()

    payload = {
        "organization_name": "Test Org",
        "owner_email": "test@example.com",
        "owner_password": "Password123!",
        "owner_first_name": "Test",
        "owner_last_name": "User",
        "plan": "free"
    }

    response = await client.post("/api/v1/organizations/onboard", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["organization"]["name"] == "Test Org"
    assert "access_token" in data
    assert "refresh_token" in data

    # Verify db
    result = await db_session.execute(select(Organization).where(Organization.name == "Test Org"))
    org = result.scalar_one_or_none()
    assert org is not None
    assert org.slug is not None

@pytest.mark.asyncio
async def test_onboard_user_exists(client: AsyncClient, db_session: AsyncSession):
    # This test might require creating a user first, but since we use a fresh DB session for each test...
    # Actually, we need to create a user first within this test session.
    # But onboard creates everything.
    # Let's just call onboard twice with same email.
    
    # Ensure free plan exists
    plan = SubscriptionPlan(
        name="Free", code="free", price=0, 
        max_users=5, max_teams=1,
        features={}
    )
    db_session.add(plan)
    await db_session.commit()

    payload = {
        "organization_name": "Test Org 1",
        "owner_email": "duplicate@example.com",
        "owner_password": "Password123!",
        "owner_first_name": "Test",
        "owner_last_name": "User",
        "plan": "free"
    }

    # First call
    response1 = await client.post("/api/v1/organizations/onboard", json=payload)
    assert response1.status_code == 200

    # Second call
    payload["organization_name"] = "Test Org 2"
    response2 = await client.post("/api/v1/organizations/onboard", json=payload)
    assert response2.status_code == 409
    assert response2.json()["detail"] == "Email already registered"


@pytest.mark.asyncio
async def test_get_organization(client: AsyncClient, db_session: AsyncSession):
    # Setup
    org_id = uuid4()
    org = Organization(
        id=org_id,
        name="Get Test Org",
        slug="get-test-org",
        status=OrganizationStatus.ACTIVE.value
    )
    db_session.add(org)
    await db_session.commit()

    user_id = uuid4()
    token = create_access_token(
        user_id=user_id,
        organization_id=org_id,
        role="owner",
        permissions=[]
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(f"/api/v1/organizations/{org_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == str(org_id)
    assert response.json()["name"] == "Get Test Org"

@pytest.mark.asyncio
async def test_get_organization_access_denied(client: AsyncClient, db_session: AsyncSession):
    # Setup - Org A
    org_id_a = uuid4()
    org_a = Organization(id=org_id_a, name="Org A", slug="org-a")
    db_session.add(org_a)
    
    # Org B
    org_id_b = uuid4()
    org_b = Organization(id=org_id_b, name="Org B", slug="org-b")
    db_session.add(org_b)
    
    await db_session.commit()

    # User belongs to Org A
    user_id = uuid4()
    token = create_access_token(
        user_id=user_id,
        organization_id=org_id_a,
        role="owner",
        permissions=[]
    )
    headers = {"Authorization": f"Bearer {token}"}

    # Try to access Org B
    response = await client.get(f"/api/v1/organizations/{org_id_b}", headers=headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied"

@pytest.mark.asyncio
async def test_update_organization(client: AsyncClient, db_session: AsyncSession):
    org_id = uuid4()
    org = Organization(id=org_id, name="Update Test", slug="update-test")
    db_session.add(org)
    await db_session.commit()

    user_id = uuid4()
    # Need organization:update permission
    token = create_access_token(
        user_id=user_id,
        organization_id=org_id,
        role="owner",
        permissions=["organization:update"]
    )
    headers = {"Authorization": f"Bearer {token}"}

    payload = {"name": "Updated Org Name"}
    response = await client.patch(f"/api/v1/organizations/{org_id}", json=payload, headers=headers)
    
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Org Name"
    
    await db_session.refresh(org)
    assert org.name == "Updated Org Name"

@pytest.mark.asyncio
async def test_delete_organization(client: AsyncClient, db_session: AsyncSession):
    user_id = uuid4()
    org_id = uuid4()
    org = Organization(
        id=org_id, 
        name="Delete Test", 
        slug="delete-test",
        owner_id=user_id
    )
    db_session.add(org)
    await db_session.commit()

    token = create_access_token(
        user_id=user_id,
        organization_id=org_id,
        role="owner",
        permissions=["organization:delete"]
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.delete(f"/api/v1/organizations/{org_id}", headers=headers)
    assert response.status_code == 200
    
    await db_session.refresh(org)
    assert org.deleted_at is not None
    assert org.status == OrganizationStatus.INACTIVE.value
    assert org.is_active is False

@pytest.mark.asyncio
async def test_update_settings(client: AsyncClient, db_session: AsyncSession):
    org_id = uuid4()
    org = Organization(id=org_id, name="Settings Test", slug="settings-test", settings={})
    db_session.add(org)
    await db_session.commit()

    token = create_access_token(
        user_id=uuid4(),
        organization_id=org_id,
        role="owner",
        permissions=["setting:update"]
    )
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "timezone": "Europe/London",
        "currency": "GBP"
    }

    response = await client.patch(f"/api/v1/organizations/{org_id}/settings", json=payload, headers=headers)
    assert response.status_code == 200
    
    await db_session.refresh(org)
    assert org.settings["timezone"] == "Europe/London"
    assert org.settings["currency"] == "GBP"
