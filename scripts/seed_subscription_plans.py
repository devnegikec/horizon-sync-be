"""Seed subscription plans."""
import asyncio
from decimal import Decimal
from shared.database import AsyncSessionLocal
from shared.models.subscription import SubscriptionPlan, PlanType

PLANS = [
    {"name": "Free", "code": "free", "price": 0, "billing_cycle": "monthly",
     "max_users": 3, "max_teams": 1, "max_leads": 100, "max_contacts": 500, "max_deals": 50, "max_tickets": 100, "max_products": 50, "max_storage_gb": 1,
     "sort_order": 0, "features": {"email_integration": False, "api_access": False, "custom_fields": False}},
    {"name": "Basic", "code": "basic", "price": Decimal("29.00"), "billing_cycle": "monthly",
     "max_users": 10, "max_teams": 5, "max_leads": 1000, "max_contacts": 5000, "max_deals": 500, "max_tickets": 1000, "max_products": 500, "max_storage_gb": 10,
     "sort_order": 1, "features": {"email_integration": True, "api_access": False, "custom_fields": True}},
    {"name": "Pro", "code": "pro", "price": Decimal("79.00"), "billing_cycle": "monthly",
     "max_users": 50, "max_teams": 20, "max_leads": 10000, "max_contacts": 50000, "max_deals": 5000, "max_tickets": 10000, "max_products": 5000, "max_storage_gb": 50,
     "sort_order": 2, "features": {"email_integration": True, "api_access": True, "custom_fields": True, "advanced_reporting": True}},
    {"name": "Enterprise", "code": "enterprise", "price": Decimal("199.00"), "billing_cycle": "monthly",
     "max_users": 500, "max_teams": 100, "max_leads": 100000, "max_contacts": 500000, "max_deals": 50000, "max_tickets": 100000, "max_products": 50000, "max_storage_gb": 500,
     "sort_order": 3, "features": {"email_integration": True, "api_access": True, "custom_fields": True, "advanced_reporting": True, "sso": True, "dedicated_support": True}},
]

async def seed_plans():
    async with AsyncSessionLocal() as session:
        for plan_data in PLANS:
            existing = await session.execute(SubscriptionPlan.__table__.select().where(SubscriptionPlan.code == plan_data["code"]))
            if not existing.scalar_one_or_none():
                plan = SubscriptionPlan(**plan_data)
                session.add(plan)
        await session.commit()
        print(f"Seeded {len(PLANS)} subscription plans")

if __name__ == "__main__":
    asyncio.run(seed_plans())
