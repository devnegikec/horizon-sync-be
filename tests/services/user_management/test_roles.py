import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from shared.models.organization import Organization
from shared.models.role import Role, Permission, RolePermission
from shared.security.jwt import create_access_token

@pytest.mark.asyncio
async def test_list_roles(client: AsyncClient, db_session: AsyncSession):
    org_id = uuid4()
    org = Organization(id=org_id, name="Roles Org", slug="roles-org")
    db_session.add(org)
    
    # Create roles
    for i in range(3):
        role = Role(
            organization_id=org_id,
            code=f"role{i}",
            name=f"Role {i}",
            is_system=(i == 0)
        )
        db_session.add(role)
    
    await db_session.commit()

    token = create_access_token(
        user_id=uuid4(),
        organization_id=org_id,
        role="owner",
        permissions=[]
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/roles", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

@pytest.mark.asyncio
async def test_create_role(client: AsyncClient, db_session: AsyncSession):
    org_id = uuid4()
    org = Organization(id=org_id, name="Create Role Org", slug="create-role-org")
    db_session.add(org)
    await db_session.commit()

    token = create_access_token(
        user_id=uuid4(),
        organization_id=org_id,
        role="owner",
        permissions=["role:create"]
    )
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "code": "custom_role",
        "name": "Custom Role",
        "description": "A custom role",
        "hierarchy_level": 50
    }

    response = await client.post("/api/v1/roles", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "custom_role"
    assert data["name"] == "Custom Role"

@pytest.mark.asyncio
async def test_get_role(client: AsyncClient, db_session: AsyncSession):
    org_id = uuid4()
    org = Organization(id=org_id, name="Get Role Org", slug="get-role-org")
    db_session.add(org)
    
    role_id = uuid4()
    role = Role(
        id=role_id,
        organization_id=org_id,
        code="test_role",
        name="Test Role"
    )
    db_session.add(role)
    await db_session.commit()

    token = create_access_token(
        user_id=uuid4(),
        organization_id=org_id,
        role="owner",
        permissions=[]
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(f"/api/v1/roles/{role_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(role_id)
    assert data["code"] == "test_role"

@pytest.mark.asyncio
async def test_update_role(client: AsyncClient, db_session: AsyncSession):
    org_id = uuid4()
    org = Organization(id=org_id, name="Update Role Org", slug="update-role-org")
    db_session.add(org)
    
    role_id = uuid4()
    role = Role(
        id=role_id,
        organization_id=org_id,
        code="update_role",
        name="Old Name",
        is_system=False
    )
    db_session.add(role)
    await db_session.commit()

    token = create_access_token(
        user_id=uuid4(),
        organization_id=org_id,
        role="owner",
        permissions=["role:update"]
    )
    headers = {"Authorization": f"Bearer {token}"}

    payload = {"name": "New Name"}
    response = await client.patch(f"/api/v1/roles/{role_id}", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"

@pytest.mark.asyncio
async def test_delete_role(client: AsyncClient, db_session: AsyncSession):
    org_id = uuid4()
    org = Organization(id=org_id, name="Delete Role Org", slug="delete-role-org")
    db_session.add(org)
    
    role_id = uuid4()
    role = Role(
        id=role_id,
        organization_id=org_id,
        code="delete_role",
        name="Delete Role",
        is_system=False
    )
    db_session.add(role)
    await db_session.commit()

    token = create_access_token(
        user_id=uuid4(),
        organization_id=org_id,
        role="owner",
        permissions=["role:delete"]
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.delete(f"/api/v1/roles/{role_id}", headers=headers)
    assert response.status_code == 200
