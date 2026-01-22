import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from shared.models.role import Permission, ResourceType, ActionType
from shared.security.jwt import create_access_token

@pytest.mark.asyncio
async def test_list_permissions(client: AsyncClient, db_session: AsyncSession):
    # Create permissions
    for i in range(3):
        perm = Permission(
            code=f"test:action{i}",
            name=f"Test Action {i}",
            resource=ResourceType.USER.value,
            action=ActionType.READ.value
        )
        db_session.add(perm)
    
    await db_session.commit()

    token = create_access_token(
        user_id=uuid4(),
        organization_id=uuid4(),
        role="owner",
        permissions=[]
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/permissions", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3

@pytest.mark.asyncio
async def test_list_resource_types(client: AsyncClient):
    response = await client.get("/api/v1/permissions/resources")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

@pytest.mark.asyncio
async def test_list_action_types(client: AsyncClient):
    response = await client.get("/api/v1/permissions/actions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
