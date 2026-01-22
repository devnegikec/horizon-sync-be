import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from shared.models.organization import Organization
from shared.models.subscription import SubscriptionPlan, Subscription, SubscriptionStatus
from shared.security.jwt import create_access_token

@pytest.mark.asyncio
async def test_list_subscription_plans(client: AsyncClient, db_session: AsyncSession):
    # Create plans
    for i in range(3):
        plan = SubscriptionPlan(
            name=f"Plan {i}",
            code=f"plan{i}",
            price=i * 10,
            max_users=10 * (i + 1),
            max_teams=5 * (i + 1)
        )
        db_session.add(plan)
    
    await db_session.commit()

    response = await client.get("/api/v1/subscriptions/plans")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3

@pytest.mark.asyncio
async def test_get_current_subscription(client: AsyncClient, db_session: AsyncSession):
    org_id = uuid4()
    org = Organization(id=org_id, name="Sub Org", slug="sub-org")
    db_session.add(org)
    
    plan_id = uuid4()
    plan = SubscriptionPlan(
        id=plan_id,
        name="Test Plan",
        code="test",
        price=50,
        max_users=10,
        max_teams=5
    )
    db_session.add(plan)
    
    sub_id = uuid4()
    subscription = Subscription(
        id=sub_id,
        organization_id=org_id,
        plan_id=plan_id,
        status=SubscriptionStatus.ACTIVE.value
    )
    db_session.add(subscription)
    await db_session.commit()

    token = create_access_token(
        user_id=uuid4(),
        organization_id=org_id,
        role="owner",
        permissions=[]
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/subscriptions/current", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(sub_id)
    assert data["plan"]["code"] == "test"
