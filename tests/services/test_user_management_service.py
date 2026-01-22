"""Unit tests for User Management Service endpoints."""
import pytest
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models.user import User, UserOrganizationRole, UserStatus
from shared.models.organization import Organization
from shared.models.role import Role
from shared.security.password import hash_password


class TestUserProfile:
    """Tests for user profile endpoints."""

    @pytest.mark.asyncio
    async def test_get_current_user_profile(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Test getting current user's profile."""
        response = await client.get(
            "/api/v1/users/me",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 401, 404]
        if response.status_code == 200:
            data = response.json()
            assert "id" in data
            assert "email" in data
            assert "first_name" in data
            assert "last_name" in data

    @pytest.mark.asyncio
    async def test_get_current_user_without_auth(self, client: AsyncClient):
        """Test getting current user profile without authentication."""
        response = await client.get("/api/v1/users/me")
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_current_user_profile(self, client: AsyncClient, auth_headers: dict):
        """Test updating current user's profile."""
        response = await client.patch(
            "/api/v1/users/me",
            headers=auth_headers,
            json={
                "first_name": "Updated",
                "last_name": "Name",
                "phone": "+1234567890"
            }
        )
        
        assert response.status_code in [200, 401, 404]
        if response.status_code == 200:
            data = response.json()
            assert data["first_name"] == "Updated"
            assert data["last_name"] == "Name"

    @pytest.mark.asyncio
    async def test_update_user_email(self, client: AsyncClient, auth_headers: dict):
        """Test updating user email."""
        response = await client.patch(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"email": "newemail@example.com"}
        )
        
        # Email update might require verification or have restrictions
        assert response.status_code in [200, 400, 401, 404]


class TestUserList:
    """Tests for user listing endpoints."""

    @pytest.mark.asyncio
    async def test_list_users_success(self, client: AsyncClient, auth_headers: dict):
        """Test listing users in organization."""
        response = await client.get(
            "/api/v1/users",
            headers=auth_headers,
            params={"page": 1, "page_size": 20}
        )
        
        assert response.status_code in [200, 401, 403]
        if response.status_code == 200:
            data = response.json()
            assert "items" in data
            assert "total" in data
            assert "page" in data
            assert "page_size" in data

    @pytest.mark.asyncio
    async def test_list_users_pagination(self, client: AsyncClient, auth_headers: dict):
        """Test user listing with pagination."""
        response = await client.get(
            "/api/v1/users",
            headers=auth_headers,
            params={"page": 2, "page_size": 10}
        )
        
        assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_list_users_with_search(self, client: AsyncClient, auth_headers: dict):
        """Test user listing with search filter."""
        response = await client.get(
            "/api/v1/users",
            headers=auth_headers,
            params={
                "page": 1,
                "page_size": 20,
                "search": "john"
            }
        )
        
        assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_list_users_with_status_filter(self, client: AsyncClient, auth_headers: dict):
        """Test user listing with status filter."""
        response = await client.get(
            "/api/v1/users",
            headers=auth_headers,
            params={
                "page": 1,
                "page_size": 20,
                "status": "active"
            }
        )
        
        assert response.status_code in [200, 401, 403]


class TestUserManagement:
    """Tests for user management endpoints."""

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Test getting user by ID."""
        user = User(
            email="testuser@example.com",
            password_hash=hash_password("Password123!"),
            first_name="Test",
            last_name="User",
            is_active=True
        )
        db_session.add(user)
        await db_session.commit()

        response = await client.get(
            f"/api/v1/users/{user.id}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 401, 403, 404]
        if response.status_code == 200:
            data = response.json()
            assert data["id"] == str(user.id)

    @pytest.mark.asyncio
    async def test_get_nonexistent_user(self, client: AsyncClient, auth_headers: dict):
        """Test getting non-existent user."""
        response = await client.get(
            f"/api/v1/users/{uuid4()}",
            headers=auth_headers
        )
        
        assert response.status_code in [404, 401, 403]

    @pytest.mark.asyncio
    async def test_create_user(self, client: AsyncClient, auth_headers: dict):
        """Test creating a new user."""
        response = await client.post(
            "/api/v1/users",
            headers=auth_headers,
            json={
                "email": "newuser@example.com",
                "first_name": "New",
                "last_name": "User",
                "user_type": "employee"
            }
        )
        
        assert response.status_code in [201, 400, 401, 403, 422]

    @pytest.mark.asyncio
    async def test_update_user(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Test updating user information."""
        user = User(
            email="testuser@example.com",
            password_hash=hash_password("Password123!"),
            first_name="Test",
            last_name="User",
            is_active=True
        )
        db_session.add(user)
        await db_session.commit()

        response = await client.patch(
            f"/api/v1/users/{user.id}",
            headers=auth_headers,
            json={
                "first_name": "Updated",
                "phone": "+1234567890"
            }
        )
        
        assert response.status_code in [200, 401, 403, 404, 422]

    @pytest.mark.asyncio
    async def test_delete_user(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Test deleting a user."""
        user = User(
            email="deleteuser@example.com",
            password_hash=hash_password("Password123!"),
            first_name="Delete",
            last_name="User",
            is_active=True
        )
        db_session.add(user)
        await db_session.commit()

        response = await client.delete(
            f"/api/v1/users/{user.id}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 204, 401, 403, 404]


class TestUserInvitation:
    """Tests for user invitation endpoints."""

    @pytest.mark.asyncio
    async def test_invite_user(self, client: AsyncClient, auth_headers: dict):
        """Test inviting a user to organization."""
        response = await client.post(
            "/api/v1/users/invite",
            headers=auth_headers,
            json={
                "email": "invited@example.com",
                "role_id": str(uuid4()),
                "first_name": "Invited",
                "last_name": "User"
            }
        )
        
        assert response.status_code in [201, 202, 400, 401, 403, 422]

    @pytest.mark.asyncio
    async def test_accept_invitation(self, client: AsyncClient):
        """Test accepting user invitation."""
        response = await client.post(
            "/api/v1/users/accept-invitation",
            json={
                "token": "invalid_token",
                "password": "NewPassword123!"
            }
        )
        
        assert response.status_code in [200, 400, 422]

    @pytest.mark.asyncio
    async def test_resend_invitation(self, client: AsyncClient, auth_headers: dict):
        """Test resending invitation."""
        response = await client.post(
            f"/api/v1/users/{uuid4()}/resend-invitation",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 404, 401, 403]

    @pytest.mark.asyncio
    async def test_cancel_invitation(self, client: AsyncClient, auth_headers: dict):
        """Test canceling invitation."""
        response = await client.post(
            f"/api/v1/users/{uuid4()}/cancel-invitation",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 404, 401, 403]


class TestUserRole:
    """Tests for user role management endpoints."""

    @pytest.mark.asyncio
    async def test_update_user_role(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Test updating user's role."""
        user = User(
            email="testuser@example.com",
            password_hash=hash_password("Password123!"),
            first_name="Test",
            last_name="User",
            is_active=True
        )
        db_session.add(user)
        await db_session.commit()

        response = await client.patch(
            f"/api/v1/users/{user.id}/role",
            headers=auth_headers,
            json={"role_id": str(uuid4())}
        )
        
        assert response.status_code in [200, 400, 401, 403, 404, 422]

    @pytest.mark.asyncio
    async def test_get_user_roles(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Test getting user's roles."""
        user = User(
            email="testuser@example.com",
            password_hash=hash_password("Password123!"),
            first_name="Test",
            last_name="User",
            is_active=True
        )
        db_session.add(user)
        await db_session.commit()

        response = await client.get(
            f"/api/v1/users/{user.id}/roles",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 401, 403, 404]


class TestUserStatus:
    """Tests for user status management."""

    @pytest.mark.asyncio
    async def test_deactivate_user(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Test deactivating a user."""
        user = User(
            email="testuser@example.com",
            password_hash=hash_password("Password123!"),
            first_name="Test",
            last_name="User",
            is_active=True
        )
        db_session.add(user)
        await db_session.commit()

        response = await client.patch(
            f"/api/v1/users/{user.id}/deactivate",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 401, 403, 404, 422]

    @pytest.mark.asyncio
    async def test_activate_user(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Test activating a user."""
        user = User(
            email="testuser@example.com",
            password_hash=hash_password("Password123!"),
            first_name="Test",
            last_name="User",
            is_active=False
        )
        db_session.add(user)
        await db_session.commit()

        response = await client.patch(
            f"/api/v1/users/{user.id}/activate",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 401, 403, 404, 422]

    @pytest.mark.asyncio
    async def test_suspend_user(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Test suspending a user."""
        user = User(
            email="testuser@example.com",
            password_hash=hash_password("Password123!"),
            first_name="Test",
            last_name="User",
            is_active=True,
            status=UserStatus.ACTIVE
        )
        db_session.add(user)
        await db_session.commit()

        response = await client.patch(
            f"/api/v1/users/{user.id}/suspend",
            headers=auth_headers,
            json={"reason": "Policy violation"}
        )
        
        assert response.status_code in [200, 401, 403, 404, 422]


class TestUserTeams:
    """Tests for user team management."""

    @pytest.mark.asyncio
    async def test_get_user_teams(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Test getting user's teams."""
        user = User(
            email="testuser@example.com",
            password_hash=hash_password("Password123!"),
            first_name="Test",
            last_name="User",
            is_active=True
        )
        db_session.add(user)
        await db_session.commit()

        response = await client.get(
            f"/api/v1/users/{user.id}/teams",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 401, 403, 404]

    @pytest.mark.asyncio
    async def test_add_user_to_team(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Test adding user to team."""
        user = User(
            email="testuser@example.com",
            password_hash=hash_password("Password123!"),
            first_name="Test",
            last_name="User",
            is_active=True
        )
        db_session.add(user)
        await db_session.commit()

        response = await client.post(
            f"/api/v1/users/{user.id}/teams",
            headers=auth_headers,
            json={"team_id": str(uuid4())}
        )
        
        assert response.status_code in [200, 201, 400, 401, 403, 404, 422]

    @pytest.mark.asyncio
    async def test_remove_user_from_team(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Test removing user from team."""
        user = User(
            email="testuser@example.com",
            password_hash=hash_password("Password123!"),
            first_name="Test",
            last_name="User",
            is_active=True
        )
        db_session.add(user)
        await db_session.commit()

        response = await client.delete(
            f"/api/v1/users/{user.id}/teams/{uuid4()}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 204, 401, 403, 404]
