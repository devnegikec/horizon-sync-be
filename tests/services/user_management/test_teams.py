import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from shared.models.organization import Organization
from shared.models.team import Team, TeamType, TeamRole
from shared.models.user import User, UserStatus
from shared.security.jwt import create_access_token

@pytest.mark.asyncio
async def test_list_teams(client: AsyncClient, db_session: AsyncSession):
    org_id = uuid4()
    org = Organization(id=org_id, name="Teams Org", slug="teams-org")
    db_session.add(org)
    
    # Create teams
    for i in range(3):
        team = Team(
            organization_id=org_id,
            name=f"Team {i}",
            code=f"team{i}",
            team_type=TeamType.DEPARTMENT.value
        )
        db_session.add(team)
    
    await db_session.commit()

    token = create_access_token(
        user_id=uuid4(),
        organization_id=org_id,
        role="owner",
        permissions=[]
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/teams", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

@pytest.mark.asyncio
async def test_create_team(client: AsyncClient, db_session: AsyncSession):
    org_id = uuid4()
    org = Organization(id=org_id, name="Create Team Org", slug="create-team-org")
    db_session.add(org)
    await db_session.commit()

    token = create_access_token(
        user_id=uuid4(),
        organization_id=org_id,
        role="owner",
        permissions=["team:create"]
    )
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "name": "New Team",
        "code": "new_team",
        "team_type": "department"
    }

    response = await client.post("/api/v1/teams", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Team"
    assert data["code"] == "new_team"

@pytest.mark.asyncio
async def test_get_team(client: AsyncClient, db_session: AsyncSession):
    org_id = uuid4()
    org = Organization(id=org_id, name="Get Team Org", slug="get-team-org")
    db_session.add(org)
    
    team_id = uuid4()
    team = Team(
        id=team_id,
        organization_id=org_id,
        name="Test Team",
        code="test_team",
        team_type=TeamType.DEPARTMENT.value
    )
    db_session.add(team)
    await db_session.commit()

    token = create_access_token(
        user_id=uuid4(),
        organization_id=org_id,
        role="owner",
        permissions=[]
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(f"/api/v1/teams/{team_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(team_id)
    assert data["name"] == "Test Team"

@pytest.mark.asyncio
async def test_update_team(client: AsyncClient, db_session: AsyncSession):
    org_id = uuid4()
    org = Organization(id=org_id, name="Update Team Org", slug="update-team-org")
    db_session.add(org)
    
    team_id = uuid4()
    team = Team(
        id=team_id,
        organization_id=org_id,
        name="Old Name",
        code="old_name",
        team_type=TeamType.DEPARTMENT.value
    )
    db_session.add(team)
    await db_session.commit()

    token = create_access_token(
        user_id=uuid4(),
        organization_id=org_id,
        role="owner",
        permissions=["team:update"]
    )
    headers = {"Authorization": f"Bearer {token}"}

    payload = {"name": "New Team Name"}
    response = await client.patch(f"/api/v1/teams/{team_id}", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "New Team Name"

@pytest.mark.asyncio
async def test_delete_team(client: AsyncClient, db_session: AsyncSession):
    org_id = uuid4()
    org = Organization(id=org_id, name="Delete Team Org", slug="delete-team-org")
    db_session.add(org)
    
    team_id = uuid4()
    team = Team(
        id=team_id,
        organization_id=org_id,
        name="Delete Team",
        code="delete_team",
        team_type=TeamType.DEPARTMENT.value
    )
    db_session.add(team)
    await db_session.commit()

    token = create_access_token(
        user_id=uuid4(),
        organization_id=org_id,
        role="owner",
        permissions=["team:delete"]
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.delete(f"/api/v1/teams/{team_id}", headers=headers)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_add_team_member(client: AsyncClient, db_session: AsyncSession):
    org_id = uuid4()
    org = Organization(id=org_id, name="Member Org", slug="member-org")
    db_session.add(org)
    
    team_id = uuid4()
    team = Team(
        id=team_id,
        organization_id=org_id,
        name="Member Team",
        code="member_team",
        team_type=TeamType.DEPARTMENT.value
    )
    db_session.add(team)
    
    user_id = uuid4()
    user = User(
        id=user_id,
        email="member@example.com",
        organization_id=org_id,
        status=UserStatus.ACTIVE.value
    )
    db_session.add(user)
    await db_session.commit()

    token = create_access_token(
        user_id=uuid4(),
        organization_id=org_id,
        role="owner",
        permissions=["team:update"]
    )
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "user_id": str(user_id),
        "role": "member"
    }

    response = await client.post(f"/api/v1/teams/{team_id}/members", json=payload, headers=headers)
    assert response.status_code == 200
