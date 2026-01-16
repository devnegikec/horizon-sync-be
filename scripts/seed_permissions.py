"""Seed default permissions into the database."""
import asyncio
from shared.database import AsyncSessionLocal
from shared.models.role import Permission, ResourceType, ActionType

PERMISSIONS = [
    # Organization
    ("organization:read", "View Organization", ResourceType.ORGANIZATION, ActionType.READ, "user_management"),
    ("organization:update", "Update Organization", ResourceType.ORGANIZATION, ActionType.UPDATE, "user_management"),
    ("organization:delete", "Delete Organization", ResourceType.ORGANIZATION, ActionType.DELETE, "user_management"),
    # Users
    ("user:create", "Create User", ResourceType.USER, ActionType.CREATE, "user_management"),
    ("user:read", "View User", ResourceType.USER, ActionType.READ, "user_management"),
    ("user:update", "Update User", ResourceType.USER, ActionType.UPDATE, "user_management"),
    ("user:delete", "Delete User", ResourceType.USER, ActionType.DELETE, "user_management"),
    ("user:list", "List Users", ResourceType.USER, ActionType.LIST, "user_management"),
    # Roles
    ("role:create", "Create Role", ResourceType.ROLE, ActionType.CREATE, "user_management"),
    ("role:read", "View Role", ResourceType.ROLE, ActionType.READ, "user_management"),
    ("role:update", "Update Role", ResourceType.ROLE, ActionType.UPDATE, "user_management"),
    ("role:delete", "Delete Role", ResourceType.ROLE, ActionType.DELETE, "user_management"),
    ("role:assign", "Assign Role", ResourceType.ROLE, ActionType.ASSIGN, "user_management"),
    # Teams
    ("team:create", "Create Team", ResourceType.TEAM, ActionType.CREATE, "user_management"),
    ("team:read", "View Team", ResourceType.TEAM, ActionType.READ, "user_management"),
    ("team:update", "Update Team", ResourceType.TEAM, ActionType.UPDATE, "user_management"),
    ("team:delete", "Delete Team", ResourceType.TEAM, ActionType.DELETE, "user_management"),
    ("team:list", "List Teams", ResourceType.TEAM, ActionType.LIST, "user_management"),
    # Leads
    ("lead:create", "Create Lead", ResourceType.LEAD, ActionType.CREATE, "crm"),
    ("lead:read", "View Lead", ResourceType.LEAD, ActionType.READ, "crm"),
    ("lead:update", "Update Lead", ResourceType.LEAD, ActionType.UPDATE, "crm"),
    ("lead:delete", "Delete Lead", ResourceType.LEAD, ActionType.DELETE, "crm"),
    ("lead:list", "List Leads", ResourceType.LEAD, ActionType.LIST, "crm"),
    # Contacts
    ("contact:create", "Create Contact", ResourceType.CONTACT, ActionType.CREATE, "crm"),
    ("contact:read", "View Contact", ResourceType.CONTACT, ActionType.READ, "crm"),
    ("contact:update", "Update Contact", ResourceType.CONTACT, ActionType.UPDATE, "crm"),
    ("contact:delete", "Delete Contact", ResourceType.CONTACT, ActionType.DELETE, "crm"),
    ("contact:list", "List Contacts", ResourceType.CONTACT, ActionType.LIST, "crm"),
    # Deals
    ("deal:create", "Create Deal", ResourceType.DEAL, ActionType.CREATE, "crm"),
    ("deal:read", "View Deal", ResourceType.DEAL, ActionType.READ, "crm"),
    ("deal:update", "Update Deal", ResourceType.DEAL, ActionType.UPDATE, "crm"),
    ("deal:delete", "Delete Deal", ResourceType.DEAL, ActionType.DELETE, "crm"),
    ("deal:list", "List Deals", ResourceType.DEAL, ActionType.LIST, "crm"),
    # Tickets
    ("ticket:create", "Create Ticket", ResourceType.TICKET, ActionType.CREATE, "support"),
    ("ticket:read", "View Ticket", ResourceType.TICKET, ActionType.READ, "support"),
    ("ticket:update", "Update Ticket", ResourceType.TICKET, ActionType.UPDATE, "support"),
    ("ticket:delete", "Delete Ticket", ResourceType.TICKET, ActionType.DELETE, "support"),
    ("ticket:list", "List Tickets", ResourceType.TICKET, ActionType.LIST, "support"),
    # Products
    ("product:create", "Create Product", ResourceType.PRODUCT, ActionType.CREATE, "inventory"),
    ("product:read", "View Product", ResourceType.PRODUCT, ActionType.READ, "inventory"),
    ("product:update", "Update Product", ResourceType.PRODUCT, ActionType.UPDATE, "inventory"),
    ("product:delete", "Delete Product", ResourceType.PRODUCT, ActionType.DELETE, "inventory"),
    ("product:list", "List Products", ResourceType.PRODUCT, ActionType.LIST, "inventory"),
    # Inventory
    ("inventory:read", "View Inventory", ResourceType.INVENTORY, ActionType.READ, "inventory"),
    ("inventory:update", "Update Inventory", ResourceType.INVENTORY, ActionType.UPDATE, "inventory"),
    # Warehouse
    ("warehouse:create", "Create Warehouse", ResourceType.WAREHOUSE, ActionType.CREATE, "inventory"),
    ("warehouse:read", "View Warehouse", ResourceType.WAREHOUSE, ActionType.READ, "inventory"),
    ("warehouse:delete", "Delete Warehouse", ResourceType.WAREHOUSE, ActionType.DELETE, "inventory"),
    ("warehouse:list", "List Warehouses", ResourceType.WAREHOUSE, ActionType.LIST, "inventory"),
    # Quotes & Orders
    ("quote:create", "Create Quote", ResourceType.QUOTE, ActionType.CREATE, "crm"),
    ("quote:read", "View Quote", ResourceType.QUOTE, ActionType.READ, "crm"),
    ("quote:update", "Update Quote", ResourceType.QUOTE, ActionType.UPDATE, "crm"),
    ("quote:delete", "Delete Quote", ResourceType.QUOTE, ActionType.DELETE, "crm"),
    ("quote:list", "List Quotes", ResourceType.QUOTE, ActionType.LIST, "crm"),
    ("order:create", "Create Order", ResourceType.ORDER, ActionType.CREATE, "crm"),
    ("order:read", "View Order", ResourceType.ORDER, ActionType.READ, "crm"),
    ("order:update", "Update Order", ResourceType.ORDER, ActionType.UPDATE, "crm"),
    ("order:delete", "Delete Order", ResourceType.ORDER, ActionType.DELETE, "crm"),
    ("order:list", "List Orders", ResourceType.ORDER, ActionType.LIST, "crm"),
    # Settings & Audit
    ("setting:read", "View Settings", ResourceType.SETTING, ActionType.READ, "admin"),
    ("setting:update", "Update Settings", ResourceType.SETTING, ActionType.UPDATE, "admin"),
    ("audit_log:read", "View Audit Logs", ResourceType.AUDIT_LOG, ActionType.READ, "admin"),
    ("subscription:update", "Manage Subscription", ResourceType.SUBSCRIPTION, ActionType.UPDATE, "admin"),
]

async def seed_permissions():
    async with AsyncSessionLocal() as session:
        for code, name, resource, action, module in PERMISSIONS:
            existing = await session.execute(
                Permission.__table__.select().where(Permission.code == code)
            )
            if not existing.scalar_one_or_none():
                perm = Permission(code=code, name=name, resource=resource, action=action, module=module)
                session.add(perm)
        await session.commit()
        print(f"Seeded {len(PERMISSIONS)} permissions")

if __name__ == "__main__":
    asyncio.run(seed_permissions())
