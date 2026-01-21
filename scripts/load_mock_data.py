"""
Script to load mock data into the database.
This script properly handles all required fields and constraints.
"""
import asyncio
import bcrypt
from datetime import datetime
from uuid import UUID
from shared.database import AsyncSessionLocal
from shared.models.organization import Organization
from shared.models.user import User
from shared.models.team import Team
from shared.models.role import Role, Permission, RolePermission
from shared.models.user import UserOrganizationRole

async def load_mock_data():
    """Load mock data into the database."""
    async with AsyncSessionLocal() as session:
        try:
            # Organization
            org_id = UUID('761b216c-504e-4729-a390-d6a62d37d565')
            org = Organization(
                id=org_id,
                name='Demo Org',
                slug='demo-org',
                status='active',
                is_active=True,
                owner_id=UUID('0a003a03-5aea-4195-a2a6-e11df7240247')
            )
            session.add(org)
            await session.flush()
            
            # Users
            password_hash = bcrypt.hashpw(b'Demo123!', bcrypt.gensalt()).decode()
            users_data = [
                ('0a003a03-5aea-4195-a2a6-e11df7240247', 'user1@demo.local', 'User1', 'Demo'),
                ('d6ea21cc-94ff-47d5-9d6b-1e8b0bf3d8a5', 'user2@demo.local', 'User2', 'Demo'),
                ('61da8c82-5548-4806-ac8f-7a91ed328151', 'user3@demo.local', 'User3', 'Demo'),
                ('efbcc110-4e0d-40d5-9af2-153b134cf673', 'user4@demo.local', 'User4', 'Demo'),
                ('c6cf51fd-d4a3-4579-a1dd-556bb99096c1', 'user5@demo.local', 'User5', 'Demo'),
            ]
            
            for user_id, email, first_name, last_name in users_data:
                user = User(
                    id=UUID(user_id),
                    organization_id=org_id,
                    email=email,
                    password_hash=password_hash,
                    first_name=first_name,
                    last_name=last_name,
                    display_name=f'{first_name} {last_name}',
                    user_type='standard',
                    status='active',
                    is_active=True,
                    email_verified=True
                )
                session.add(user)
            
            await session.flush()
            
            # Teams
            teams_data = [
                ('cb0e0480-41ef-492c-9b1b-241cb5826d51', 'Sales Team', 'sales'),
                ('7daf8405-10c6-4a66-b6b3-4cb8ed548218', 'Finance Team', 'finance'),
            ]
            
            for team_id, name, code in teams_data:
                team = Team(
                    id=UUID(team_id),
                    organization_id=org_id,
                    name=name,
                    code=code,
                    team_type='department',
                    is_active=True
                )
                session.add(team)
            
            await session.commit()
            print("✅ Mock data loaded successfully!")
            print(f"   - 1 organization")
            print(f"   - {len(users_data)} users (password: Demo123!)")
            print(f"   - {len(teams_data)} teams")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error loading mock data: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(load_mock_data())
