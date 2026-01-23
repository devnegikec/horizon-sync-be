# ERP System - Permissions and Roles Guide

## Overview

This guide explains how the permissions and roles system works in your ERP system, with real-world examples from the seed data.

## Core Concepts

### 1. **Permissions** (System-wide capabilities)

Permissions define **what actions** can be performed on **what resources**. They follow the format: `resource.action`

**Examples:**

- `user.create` - Can create new users
- `invoice.read` - Can view invoices
- `lead.update` - Can update leads
- `order.delete` - Can delete orders

### 2. **Roles** (Permission bundles)

Roles are collections of permissions assigned to users within an organization. Each organization can have its own custom roles.

### 3. **User-Organization-Role Assignment**

Users are assigned roles within specific organizations through the `user_organization_roles` table.

---

## Permission Categories

### User Management Module

- `user.create`, `user.read`, `user.update`, `user.delete`
- `organization.create`, `organization.read`, `organization.update`, `organization.delete`
- `team.create`, `team.read`, `team.update`, `team.delete`
- `role.create`, `role.read`, `role.update`, `role.delete`

### Lead-to-Order Module (CRM)

- `lead.create`, `lead.read`, `lead.update`, `lead.delete`
- `contact.create`, `contact.read`, `contact.update`, `contact.delete`
- `deal.create`, `deal.read`, `deal.update`, `deal.delete`
- `order.create`, `order.read`, `order.update`, `order.delete`

### Support Module

- `ticket.create`, `ticket.read`, `ticket.update`, `ticket.delete`

### Billing Module

- `invoice.create`, `invoice.read`, `invoice.update`, `invoice.delete`
- `payment.create`, `payment.read`, `payment.update`, `payment.delete`

### Audit & Activity

- `audit.read` - View audit logs
- `activity.read` - View activity logs

---

## Role Hierarchy & Examples

### TechCorp Solutions Organization

#### 1. **Sarah Johnson - Owner** (Full Access)

**Role:** Owner  
**Permissions:** ALL (56 permissions)

**What Sarah can do:**

- ✅ Create, read, update, and delete users
- ✅ Manage organization settings
- ✅ Create and delete roles
- ✅ Access all modules (CRM, Support, Billing)
- ✅ View all audit logs
- ✅ Delete the organization

**Example Actions:**

```sql
-- Sarah can create a new admin user
INSERT INTO users (...) VALUES (...);
INSERT INTO user_organization_roles (user_id, organization_id, role_id)
VALUES ('new-user-id', 'techcorp-id', 'admin-role-id');

-- Sarah can delete the organization
DELETE FROM organizations WHERE id = 'techcorp-id';
```

---

#### 2. **David Martinez - Administrator** (Almost Full Access)

**Role:** Administrator  
**Permissions:** ALL except `organization.delete` (55 permissions)

**What David can do:**

- ✅ Create, read, update, and delete users
- ✅ Manage teams and roles
- ✅ Access all modules
- ✅ View audit logs
- ❌ Cannot delete the organization

**Example Actions:**

```sql
-- David can create a new team
INSERT INTO teams (organization_id, name, code, lead_user_id)
VALUES ('techcorp-id', 'Marketing', 'MARKETING', 'some-user-id');

-- David can assign users to roles
INSERT INTO user_organization_roles (user_id, organization_id, role_id)
VALUES ('user-id', 'techcorp-id', 'sales-rep-role-id');
```

---

#### 3. **Emily Chen - Sales Manager** (Sales + Team Management)

**Role:** Sales Manager  
**Permissions:** 18 permissions

**What Emily can do:**

- ✅ View users (read-only)
- ✅ Create, read, and update teams
- ✅ Full access to leads, contacts, deals, and orders
- ❌ Cannot manage users or roles
- ❌ Cannot access support tickets
- ❌ Cannot access billing/invoices

**Specific Permissions:**

- `user.read` - Can view user list
- `team.create`, `team.read`, `team.update` - Manage sales team
- `lead.*`, `contact.*`, `deal.*`, `order.*` - Full CRM access

**Example Actions:**

```sql
-- Emily can create a new lead
INSERT INTO leads (organization_id, name, email, status, assigned_to)
VALUES ('techcorp-id', 'Acme Corp', 'contact@acme.com', 'new', 'emily-user-id');

-- Emily can add a team member to her sales team
INSERT INTO team_members (team_id, user_id, role, added_by_id)
VALUES ('sales-team-id', 'james-user-id', 'member', 'emily-user-id');

-- Emily CANNOT create invoices (no permission)
-- This would fail:
INSERT INTO invoices (...) VALUES (...); -- ❌ Permission denied
```

---

#### 4. **James Wilson - Sales Representative** (Limited Sales Access)

**Role:** Sales Representative  
**Permissions:** 10 permissions

**What James can do:**

- ✅ Create, read, and update leads (his own)
- ✅ Create, read, and update contacts
- ✅ Create, read, and update deals
- ✅ View orders (read-only)
- ❌ Cannot delete leads, contacts, or deals
- ❌ Cannot create or modify orders
- ❌ Cannot manage teams or users

**Specific Permissions:**

- `lead.create`, `lead.read`, `lead.update` (no delete)
- `contact.create`, `contact.read`, `contact.update` (no delete)
- `deal.create`, `deal.read`, `deal.update` (no delete)
- `order.read` (read-only)

**Example Actions:**

```sql
-- James can create a lead
INSERT INTO leads (organization_id, name, email, assigned_to)
VALUES ('techcorp-id', 'New Client', 'client@example.com', 'james-user-id');

-- James can update his own lead
UPDATE leads
SET status = 'qualified'
WHERE id = 'lead-id' AND assigned_to = 'james-user-id';

-- James can view orders but NOT create them
SELECT * FROM orders WHERE organization_id = 'techcorp-id'; -- ✅ Allowed

-- James CANNOT delete leads
DELETE FROM leads WHERE id = 'lead-id'; -- ❌ Permission denied

-- James CANNOT create orders
INSERT INTO orders (...) VALUES (...); -- ❌ Permission denied
```

---

#### 5. **Lisa Anderson - Support Manager** (Support + Team Management)

**Role:** Support Manager  
**Permissions:** 7 permissions

**What Lisa can do:**

- ✅ View users (read-only)
- ✅ Read and update teams
- ✅ Full access to support tickets
- ❌ Cannot access CRM (leads, contacts, deals)
- ❌ Cannot access billing

**Specific Permissions:**

- `user.read`
- `team.read`, `team.update`
- `ticket.create`, `ticket.read`, `ticket.update`, `ticket.delete`

**Example Actions:**

```sql
-- Lisa can view all support tickets
SELECT * FROM tickets WHERE organization_id = 'techcorp-id';

-- Lisa can assign tickets to team members
UPDATE tickets
SET assigned_to = 'robert-user-id'
WHERE id = 'ticket-id';

-- Lisa can delete resolved tickets
DELETE FROM tickets WHERE id = 'ticket-id' AND status = 'resolved';

-- Lisa CANNOT view leads
SELECT * FROM leads WHERE organization_id = 'techcorp-id'; -- ❌ Permission denied
```

---

#### 6. **Robert Taylor - Support Agent** (Limited Support Access)

**Role:** Support Agent  
**Permissions:** 3 permissions

**What Robert can do:**

- ✅ Create new support tickets
- ✅ View tickets (typically his assigned ones)
- ✅ Update ticket status and add comments
- ❌ Cannot delete tickets
- ❌ Cannot access other modules

**Specific Permissions:**

- `ticket.create`, `ticket.read`, `ticket.update`

**Example Actions:**

```sql
-- Robert can create a ticket
INSERT INTO tickets (organization_id, title, description, assigned_to)
VALUES ('techcorp-id', 'Login Issue', 'User cannot login', 'robert-user-id');

-- Robert can update his assigned tickets
UPDATE tickets
SET status = 'in_progress', description = 'Working on it...'
WHERE id = 'ticket-id' AND assigned_to = 'robert-user-id';

-- Robert CANNOT delete tickets
DELETE FROM tickets WHERE id = 'ticket-id'; -- ❌ Permission denied
```

---

#### 7. **Jennifer Lee - Finance Manager** (Full Financial Access)

**Role:** Finance Manager  
**Permissions:** 11 permissions

**What Jennifer can do:**

- ✅ View users (read-only)
- ✅ Full access to invoices and payments
- ✅ View audit logs
- ❌ Cannot access CRM or support modules
- ❌ Cannot manage users or teams

**Specific Permissions:**

- `user.read`
- `invoice.create`, `invoice.read`, `invoice.update`, `invoice.delete`
- `payment.create`, `payment.read`, `payment.update`, `payment.delete`
- `audit.read`

**Example Actions:**

```sql
-- Jennifer can create invoices
INSERT INTO invoices (organization_id, invoice_no, customer_id, total_amount)
VALUES ('techcorp-id', 'INV-001', 'customer-id', 5000.00);

-- Jennifer can record payments
INSERT INTO payments (organization_id, payment_no, invoice_id, amount)
VALUES ('techcorp-id', 'PAY-001', 'invoice-id', 5000.00);

-- Jennifer can view audit logs
SELECT * FROM audit_logs
WHERE organization_id = 'techcorp-id'
ORDER BY created_at DESC;

-- Jennifer CANNOT create leads
INSERT INTO leads (...) VALUES (...); -- ❌ Permission denied
```

---

### GlobalTrade Inc Organization

#### 8. **Michael Chen - Owner** (Full Access)

**Role:** Owner  
**Permissions:** ALL (56 permissions)

Same as Sarah Johnson - full access to everything.

---

#### 9. **Amanda Rodriguez - Administrator** (Almost Full Access)

**Role:** Administrator  
**Permissions:** ALL except `organization.delete` (55 permissions)

Same as David Martinez - can do everything except delete the organization.

---

#### 10. **Daniel Kim - Operations Manager** (Operations Focus)

**Role:** Operations Manager  
**Permissions:** 8 permissions

**What Daniel can do:**

- ✅ View users (read-only)
- ✅ Read and update teams
- ✅ Full access to orders
- ✅ View contacts (read-only)
- ❌ Cannot access leads or deals
- ❌ Cannot access billing

**Specific Permissions:**

- `user.read`
- `team.read`, `team.update`
- `order.create`, `order.read`, `order.update`, `order.delete`
- `contact.read`

**Example Actions:**

```sql
-- Daniel can create orders
INSERT INTO orders (organization_id, order_no, customer_id, total_amount)
VALUES ('globaltrade-id', 'ORD-001', 'customer-id', 10000.00);

-- Daniel can update order status
UPDATE orders
SET status = 'shipped'
WHERE id = 'order-id';

-- Daniel can view contacts
SELECT * FROM contacts WHERE organization_id = 'globaltrade-id';

-- Daniel CANNOT create leads
INSERT INTO leads (...) VALUES (...); -- ❌ Permission denied
```

---

#### 11. **Sophia Patel - Warehouse Supervisor** (Warehouse Operations)

**Role:** Warehouse Supervisor  
**Permissions:** 2 permissions

**What Sophia can do:**

- ✅ View orders (read-only)
- ✅ Update order fulfillment status
- ❌ Cannot create or delete orders
- ❌ Cannot access other modules

**Specific Permissions:**

- `order.read`, `order.update`

**Example Actions:**

```sql
-- Sophia can view orders for fulfillment
SELECT * FROM orders
WHERE organization_id = 'globaltrade-id'
AND status = 'pending';

-- Sophia can update order status after shipping
UPDATE orders
SET status = 'shipped', shipped_at = NOW()
WHERE id = 'order-id';

-- Sophia CANNOT delete orders
DELETE FROM orders WHERE id = 'order-id'; -- ❌ Permission denied
```

---

#### 12. **Thomas Brown - Accountant** (Financial Records)

**Role:** Accountant  
**Permissions:** 6 permissions

**What Thomas can do:**

- ✅ Full access to invoices (except delete)
- ✅ Create, read, and update payments
- ❌ Cannot delete invoices or payments
- ❌ Cannot access other modules

**Specific Permissions:**

- `invoice.create`, `invoice.read`, `invoice.update`
- `payment.create`, `payment.read`, `payment.update`

**Example Actions:**

```sql
-- Thomas can create invoices
INSERT INTO invoices (organization_id, invoice_no, total_amount)
VALUES ('globaltrade-id', 'INV-GT-001', 15000.00);

-- Thomas can record payments
INSERT INTO payments (organization_id, payment_no, amount)
VALUES ('globaltrade-id', 'PAY-GT-001', 15000.00);

-- Thomas CANNOT delete invoices
DELETE FROM invoices WHERE id = 'invoice-id'; -- ❌ Permission denied
```

---

#### 13. **Maria Garcia - Sales Representative** (Sales Activities)

**Role:** Sales Representative  
**Permissions:** 9 permissions

**What Maria can do:**

- ✅ Create, read, and update leads
- ✅ Create, read, and update contacts
- ✅ Create, read, and update deals
- ❌ Cannot delete anything
- ❌ Cannot access orders or billing

**Specific Permissions:**

- `lead.create`, `lead.read`, `lead.update`
- `contact.create`, `contact.read`, `contact.update`
- `deal.create`, `deal.read`, `deal.update`

**Example Actions:**

```sql
-- Maria can create leads
INSERT INTO leads (organization_id, name, email, assigned_to)
VALUES ('globaltrade-id', 'Potential Client', 'client@example.com', 'maria-user-id');

-- Maria can convert leads to deals
INSERT INTO deals (organization_id, name, lead_id, value, assigned_to)
VALUES ('globaltrade-id', 'Big Deal', 'lead-id', 50000.00, 'maria-user-id');

-- Maria CANNOT delete leads
DELETE FROM leads WHERE id = 'lead-id'; -- ❌ Permission denied
```

---

## How Permissions Are Checked

### Permission Check Flow

1. **User makes a request** (e.g., "Create a new lead")
2. **System identifies the user** from the authentication token
3. **System looks up user's role** in the current organization
4. **System checks role permissions** via `role_permissions` table
5. **System grants or denies access** based on permission existence

### Example Permission Check (Pseudocode)

```python
def check_permission(user_id, organization_id, required_permission):
    # Get user's role in the organization
    user_role = db.query("""
        SELECT role_id
        FROM user_organization_roles
        WHERE user_id = ? AND organization_id = ? AND is_active = true
    """, user_id, organization_id)

    # Check if role has the required permission
    has_permission = db.query("""
        SELECT COUNT(*) > 0
        FROM role_permissions rp
        JOIN permissions p ON rp.permission_id = p.id
        WHERE rp.role_id = ? AND p.code = ?
    """, user_role.role_id, required_permission)

    return has_permission
```

### Example Usage in API

```python
@app.post("/api/leads")
def create_lead(lead_data, current_user):
    # Check if user has permission
    if not check_permission(current_user.id, lead_data.organization_id, "lead.create"):
        raise PermissionDenied("You don't have permission to create leads")

    # Create the lead
    lead = Lead.create(lead_data)
    return lead
```

---

## Key Takeaways

### 1. **Hierarchical Access**

- **Owner** > **Admin** > **Manager** > **Staff**
- Higher roles have more permissions

### 2. **Principle of Least Privilege**

- Users only get permissions they need for their job
- Sales reps can't access billing
- Support agents can't delete tickets

### 3. **Organization Isolation**

- Permissions are scoped to organizations
- Sarah (TechCorp Owner) has no access to GlobalTrade data
- Michael (GlobalTrade Owner) has no access to TechCorp data

### 4. **Flexible Role System**

- Each organization can create custom roles
- Roles can be modified by adding/removing permissions
- Users can have different roles in different organizations

### 5. **Audit Trail**

- All actions are logged in `audit_logs`
- Finance managers and owners can view audit logs
- Helps track who did what and when

---

## Summary Table

| User             | Organization | Role                 | Key Permissions            | Can Do                     | Cannot Do                            |
| ---------------- | ------------ | -------------------- | -------------------------- | -------------------------- | ------------------------------------ |
| Sarah Johnson    | TechCorp     | Owner                | ALL (56)                   | Everything                 | Nothing restricted                   |
| David Martinez   | TechCorp     | Admin                | 55 (all except org.delete) | Almost everything          | Delete organization                  |
| Emily Chen       | TechCorp     | Sales Manager        | 18 (CRM + teams)           | Manage sales, leads, deals | Access billing, support              |
| James Wilson     | TechCorp     | Sales Rep            | 10 (limited CRM)           | Create/update leads, deals | Delete anything, create orders       |
| Lisa Anderson    | TechCorp     | Support Manager      | 7 (support + teams)        | Manage tickets, team       | Access CRM, billing                  |
| Robert Taylor    | TechCorp     | Support Agent        | 3 (limited support)        | Handle tickets             | Delete tickets, access other modules |
| Jennifer Lee     | TechCorp     | Finance Manager      | 11 (billing + audit)       | Manage invoices, payments  | Access CRM, support                  |
| Michael Chen     | GlobalTrade  | Owner                | ALL (56)                   | Everything                 | Nothing restricted                   |
| Amanda Rodriguez | GlobalTrade  | Admin                | 55 (all except org.delete) | Almost everything          | Delete organization                  |
| Daniel Kim       | GlobalTrade  | Operations Manager   | 8 (orders + teams)         | Manage orders              | Access leads, billing                |
| Sophia Patel     | GlobalTrade  | Warehouse Supervisor | 2 (order view/update)      | Update order status        | Create/delete orders                 |
| Thomas Brown     | GlobalTrade  | Accountant           | 6 (invoices + payments)    | Create invoices, payments  | Delete financial records             |
| Maria Garcia     | GlobalTrade  | Sales Rep            | 9 (limited CRM)            | Create/update leads, deals | Delete anything                      |

---

## Testing the Seed Data

Run the seed script:

```bash
psql -U your_username -d your_database -f scripts/seed_auth_user_management.sql
```

Login credentials for all users:

- **Email:** See user email in seed data (e.g., `sarah.johnson@techcorp.com`)
- **Password:** `Password123!` (for all users)

---

## Next Steps

1. **Implement permission checks** in your API endpoints
2. **Add row-level security** (e.g., users can only see their own leads)
3. **Create permission middleware** for your web framework
4. **Add UI permission checks** to hide/show features based on user permissions
5. **Implement audit logging** for all sensitive operations
