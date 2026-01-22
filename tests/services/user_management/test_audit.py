import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from datetime import datetime

from shared.models.organization import Organization
from shared.models.audit import AuditLog, AuditAction
from shared.security.jwt import create_access_token

@pytest.mark.asyncio
async def test_list_audit_logs(client: AsyncClient, db_session: AsyncSession):
    org_id = uuid4()
    org = Organization(id=org_id, name="Audit Org", slug="audit-org")
    db_session.add(org)
    
    user_id = uuid4()
    
    # Create audit logs
    for i in range(3):
        log = AuditLog(
            organization_id=org_id,
            user_id=user_id,
            action=AuditAction.CREATE.value,
            resource_type="user",
            resource_id=uuid4(),
            timestamp=datetime.utcnow()
        )
        db_session.add(log)
    
    await db_session.commit()

    token = create_access_token(
        user_id=uuid4(),
        organization_id=org_id,
        role="owner",
        permissions=["audit_log:read"]
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/audit", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 3

@pytest.mark.asyncio
async def test_get_user_audit_logs(client: AsyncClient, db_session: AsyncSession):
    org_id = uuid4()
    org = Organization(id=org_id, name="User Audit Org", slug="user-audit-org")
    db_session.add(org)
    
    user_id = uuid4()
    
    # Create audit logs for specific user
    for i in range(2):
        log = AuditLog(
            organization_id=org_id,
            user_id=user_id,
            action=AuditAction.UPDATE.value,
            resource_type="user",
            resource_id=user_id,
            timestamp=datetime.utcnow()
        )
        db_session.add(log)
    
    await db_session.commit()

    token = create_access_token(
        user_id=uuid4(),
        organization_id=org_id,
        role="owner",
        permissions=["audit_log:read"]
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(f"/api/v1/audit/user/{user_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
