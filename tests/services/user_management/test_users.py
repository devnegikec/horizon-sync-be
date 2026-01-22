import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from datetime import datetime, timedelta

from shared.models.user import User, UserStatus
from shared.models.organization import Organization
from shared.models.role import Role, Permission, RolePermission
from shared.models.auth import Invitation, InvitationStatus
from shared.security.jwt import create_access_token
from shared.security.password import hash_password

@pytest.mark.asyncio
async def test_get_me(client: AsyncClient, db_session: AsyncSession):
    # Setup
    org_id = uuid4()
    org = Organization(id=org_id, name="Test Org", slug="test-org")
    db_session.add(org)

    role_id = uuid4()
    role = Role(
        id=role_id, 
        organization_id=org_id, 
        code="owner", 
        name="Owner",
        is_active=True
    )
    db_session.add(role)

    user_id = uuid4()
    user = User(
        id=user_id,
        email="me@example.com",
        first_name="Me",
        last_name="Test",
        organization_id=org_id,
        status=UserStatus.ACTIVE.value
    )
    db_session.add(user)
    
    # UserOrgRole association? 
    # The API uses user_service.get_user_organizations which likely queries UserOrganizationRole or similar
    # In shared/models/user.py UserOrganizationRole likely exists but wasn't fully visible in snippets.
    # Let's assume User has organization_id direct link OR there is a separate table.
    # The code `user.organization_id == org_id` in `get_organization_stats` suggests direct link.
    # But `get_user_organizations` suggests multiple.
    # Let's check `User` model again.
    # In `d:\Code\CRM\horizon-sync-be\shared\models\user.py`, User has `organization_id` column.
    # So direct link.

    await db_session.commit()

    token = create_access_token(
        user_id=user_id,
        organization_id=org_id,
        role="owner",
        permissions=[]
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(user_id)
    assert data["email"] == "me@example.com"
    assert data["organization_id"] == str(org_id)

@pytest.mark.asyncio
async def test_list_users(client: AsyncClient, db_session: AsyncSession):
    org_id = uuid4()
    # Create org
    org = Organization(id=org_id, name="List Org", slug="list-org")
    db_session.add(org)

    # Create users
    for i in range(3):
        user = User(
            email=f"user{i}@example.com",
            first_name=f"User{i}",
            last_name="Test",
            organization_id=org_id,
            status=UserStatus.ACTIVE.value
        )
        db_session.add(user)
    
    await db_session.commit()

    token = create_access_token(
        user_id=uuid4(), # requester ID doesn't need to exist in DB for this check if permissions allow
        organization_id=org_id,
        role="owner",
        permissions=["user:list"]
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/users", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3
    assert data["total"] == 3

@pytest.mark.asyncio
async def test_invite_user(client: AsyncClient, db_session: AsyncSession):
    org_id = uuid4()
    org = Organization(id=org_id, name="Invite Org", slug="invite-org")
    db_session.add(org)
    
    # Need a role to invite to
    role_id = uuid4()
    role = Role(id=role_id, organization_id=org_id, code="member", name="Member")
    db_session.add(role)
    
    await db_session.commit()

    requester_id = uuid4()
    token = create_access_token(
        user_id=requester_id,
        organization_id=org_id,
        role="owner",
        permissions=["user:create"]
    )
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "email": "invitee@example.com",
        "first_name": "Invitee",
        "last_name": "Person",
        "role_id": str(role_id)
    }

    response = await client.post("/api/v1/users/invite", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "invitee@example.com"
    assert "invitation_url" in data
    
    # Verify DB
    result = await db_session.execute(select(Invitation).where(Invitation.email == "invitee@example.com"))
    invitation = result.scalar_one_or_none()
    assert invitation is not None
    assert invitation.organization_id == org_id

@pytest.mark.asyncio
async def test_accept_invitation(client: AsyncClient, db_session: AsyncSession):
    org_id = uuid4()
    org = Organization(id=org_id, name="Accept Org", slug="accept-org")
    db_session.add(org)
    
    role_id = uuid4()
    role = Role(id=role_id, organization_id=org_id, code="member", name="Member")
    db_session.add(role)

    token = "test-token"
    token_hash = hash_password(token)
    
    invitation = Invitation(
        organization_id=org_id,
        email="accepted@example.com",
        first_name="Accepted",
        last_name="User",
        role_id=role_id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(days=1),
        status=InvitationStatus.PENDING.value
    )
    db_session.add(invitation)
    await db_session.commit()

    payload = {
        "token": token,
        "password": "Password123!",
        "first_name": "Accepted",
        "last_name": "User"
    }

    response = await client.post("/api/v1/users/accept-invitation", json=payload)
    assert response.status_code == 200
    
    # Verify user created
    result = await db_session.execute(select(User).where(User.email == "accepted@example.com"))
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.organization_id == org_id
    assert user.status == UserStatus.ACTIVE.value
    
    # Verify invitation accepted
    await db_session.refresh(invitation)
    assert invitation.status == InvitationStatus.ACCEPTED.value

@pytest.mark.asyncio
async def test_update_user(client: AsyncClient, db_session: AsyncSession):
    org_id = uuid4()
    org = Organization(id=org_id, name="Update Org", slug="update-org")
    db_session.add(org)

    user_id = uuid4()
    user = User(
        id=user_id,
        email="toupdate@example.com",
        organization_id=org_id,
        first_name="Old",
        last_name="Name"
    )
    db_session.add(user)
    await db_session.commit()

    token = create_access_token(
        user_id=uuid4(),
        organization_id=org_id,
        role="owner",
        permissions=["user:update"]
    )
    headers = {"Authorization": f"Bearer {token}"}

    payload = {"first_name": "New"}
    response = await client.patch(f"/api/v1/users/{user_id}", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["first_name"] == "New"
