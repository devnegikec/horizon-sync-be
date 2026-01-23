-- =====================================================
-- ERP System - Auth & User Management Seed Data (Fixed)
-- =====================================================

-- Clean existing data
DELETE FROM invitations;
DELETE FROM user_teams;
DELETE FROM user_organization_roles;
DELETE FROM role_permissions;
DELETE FROM teams;
DELETE FROM roles;
DELETE FROM users;
DELETE FROM organizations;
DELETE FROM permissions;

-- =====================================================
-- 1. PERMISSIONS
-- =====================================================
INSERT INTO permissions (id, code, name, description) VALUES
-- User Management
('11111111-1111-1111-1111-111111111101', 'user.create', 'Create Users', 'Create new users'),
('11111111-1111-1111-1111-111111111102', 'user.read', 'View Users', 'View user information'),
('11111111-1111-1111-1111-111111111103', 'user.update', 'Update Users', 'Update user information'),
('11111111-1111-1111-1111-111111111104', 'user.delete', 'Delete Users', 'Delete users'),
-- Organization Management
('11111111-1111-1111-1111-111111111201', 'organization.create', 'Create Organizations', 'Create new organizations'),
('11111111-1111-1111-1111-111111111202', 'organization.read', 'View Organizations', 'View organization information'),
('11111111-1111-1111-1111-111111111203', 'organization.update', 'Update Organizations', 'Update organization settings'),
('11111111-1111-1111-1111-111111111204', 'organization.delete', 'Delete Organizations', 'Delete organizations'),
-- Team Management
('11111111-1111-1111-1111-111111111301', 'team.create', 'Create Teams', 'Create new teams'),
('11111111-1111-1111-1111-111111111302', 'team.read', 'View Teams', 'View team information'),
('11111111-1111-1111-1111-111111111303', 'team.update', 'Update Teams', 'Update team information'),
('11111111-1111-1111-1111-111111111304', 'team.delete', 'Delete Teams', 'Delete teams'),
-- Role Management
('11111111-1111-1111-1111-111111111401', 'role.create', 'Create Roles', 'Create new roles'),
('11111111-1111-1111-1111-111111111402', 'role.read', 'View Roles', 'View role information'),
('11111111-1111-1111-1111-111111111403', 'role.update', 'Update Roles', 'Update role permissions'),
('11111111-1111-1111-1111-111111111404', 'role.delete', 'Delete Roles', 'Delete roles'),
-- Lead Management
('11111111-1111-1111-1111-111111111601', 'lead.create', 'Create Leads', 'Create new leads'),
('11111111-1111-1111-1111-111111111602', 'lead.read', 'View Leads', 'View lead information'),
('11111111-1111-1111-1111-111111111603', 'lead.update', 'Update Leads', 'Update lead information'),
('11111111-1111-1111-1111-111111111604', 'lead.delete', 'Delete Leads', 'Delete leads'),
-- Contact Management
('11111111-1111-1111-1111-111111111701', 'contact.create', 'Create Contacts', 'Create new contacts'),
('11111111-1111-1111-1111-111111111702', 'contact.read', 'View Contacts', 'View contact information'),
('11111111-1111-1111-1111-111111111703', 'contact.update', 'Update Contacts', 'Update contact information'),
('11111111-1111-1111-1111-111111111704', 'contact.delete', 'Delete Contacts', 'Delete contacts');

-- =====================================================
-- 2. ORGANIZATIONS
-- =====================================================
INSERT INTO organizations (id, name, slug, status, owner_id, is_active, created_at, updated_at) VALUES
('22222222-2222-2222-2222-222222222201', 'TechCorp Solutions', 'techcorp-solutions', 'active', 
 '33333333-3333-3333-3333-333333333301', true, NOW(), NOW()),
('22222222-2222-2222-2222-222222222202', 'GlobalTrade Inc', 'globaltrade-inc', 'active', 
 '33333333-3333-3333-3333-333333333311', true, NOW(), NOW());

-- =====================================================
-- 3. USERS (Password: Password123!)
-- =====================================================
INSERT INTO users (id, organization_id, email, password_hash, first_name, last_name, display_name, 
    phone, avatar_url, user_type, status, is_active, email_verified, mfa_enabled, 
    failed_login_attempts, last_login_at, timezone, language, created_at, updated_at) VALUES
-- TechCorp Users
('33333333-3333-3333-3333-333333333301', '22222222-2222-2222-2222-222222222201',
 'sarah.johnson@techcorp.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.Hs7HO6',
 'Sarah', 'Johnson', 'Sarah Johnson', '+1-555-0101', 'https://i.pravatar.cc/150?img=1',
 'internal', 'active', true, true, true, 0, NOW() - INTERVAL '2 hours', 
 'America/Los_Angeles', 'en', NOW() - INTERVAL '2 years', NOW()),
('33333333-3333-3333-3333-333333333302', '22222222-2222-2222-2222-222222222201',
 'david.martinez@techcorp.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.Hs7HO6',
 'David', 'Martinez', 'David Martinez', '+1-555-0102', 'https://i.pravatar.cc/150?img=12',
 'internal', 'active', true, true, true, 0, NOW() - INTERVAL '5 hours',
 'America/Los_Angeles', 'en', NOW() - INTERVAL '1 year', NOW()),
('33333333-3333-3333-3333-333333333303', '22222222-2222-2222-2222-222222222201',
 'emily.chen@techcorp.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.Hs7HO6',
 'Emily', 'Chen', 'Emily Chen', '+1-555-0103', 'https://i.pravatar.cc/150?img=5',
 'internal', 'active', true, true, false, 0, NOW() - INTERVAL '1 day',
 'America/Los_Angeles', 'en', NOW() - INTERVAL '1 year', NOW()),
('33333333-3333-3333-3333-333333333304', '22222222-2222-2222-2222-222222222201',
 'james.wilson@techcorp.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.Hs7HO6',
 'James', 'Wilson', 'James Wilson', '+1-555-0104', 'https://i.pravatar.cc/150?img=13',
 'internal', 'active', true, true, false, 0, NOW() - INTERVAL '3 hours',
 'America/Los_Angeles', 'en', NOW() - INTERVAL '8 months', NOW()),
-- GlobalTrade Users
('33333333-3333-3333-3333-333333333311', '22222222-2222-2222-2222-222222222202',
 'michael.chen@globaltrade.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.Hs7HO6',
 'Michael', 'Chen', 'Michael Chen', '+1-555-0201', 'https://i.pravatar.cc/150?img=15',
 'internal', 'active', true, true, true, 0, NOW() - INTERVAL '1 hour',
 'America/Chicago', 'en', NOW() - INTERVAL '3 years', NOW()),
('33333333-3333-3333-3333-333333333312', '22222222-2222-2222-2222-222222222202',
 'amanda.rodriguez@globaltrade.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.Hs7HO6',
 'Amanda', 'Rodriguez', 'Amanda Rodriguez', '+1-555-0202', 'https://i.pravatar.cc/150?img=20',
 'internal', 'active', true, true, true, 0, NOW() - INTERVAL '3 hours',
 'America/Chicago', 'en', NOW() - INTERVAL '2 years', NOW());

-- =====================================================
-- 4. ROLES
-- =====================================================
INSERT INTO roles (id, organization_id, name, code, description, is_system, is_default, hierarchy_level, is_active) VALUES
-- TechCorp Roles
('44444444-4444-4444-4444-444444444401', '22222222-2222-2222-2222-222222222201',
 'Owner', 'OWNER', 'Organization owner with full access', true, false, 1, true),
('44444444-4444-4444-4444-444444444402', '22222222-2222-2222-2222-222222222201',
 'Administrator', 'ADMIN', 'System administrator', true, false, 2, true),
('44444444-4444-4444-4444-444444444403', '22222222-2222-2222-2222-222222222201',
 'Sales Manager', 'SALES_MANAGER', 'Manages sales team', false, false, 3, true),
('44444444-4444-4444-4444-444444444404', '22222222-2222-2222-2222-222222222201',
 'Sales Representative', 'SALES_REP', 'Sales representative', false, true, 4, true),
-- GlobalTrade Roles
('44444444-4444-4444-4444-444444444411', '22222222-2222-2222-2222-222222222202',
 'Owner', 'OWNER', 'Organization owner with full access', true, false, 1, true),
('44444444-4444-4444-4444-444444444412', '22222222-2222-2222-2222-222222222202',
 'Administrator', 'ADMIN', 'System administrator', true, false, 2, true);

-- =====================================================
-- 5. ROLE_PERMISSIONS
-- =====================================================
-- TechCorp Owner - All permissions
INSERT INTO role_permissions (id, role_id, permission_id) 
SELECT gen_random_uuid(), '44444444-4444-4444-4444-444444444401', id FROM permissions;

-- TechCorp Admin - All except organization delete
INSERT INTO role_permissions (id, role_id, permission_id)
SELECT gen_random_uuid(), '44444444-4444-4444-4444-444444444402', id 
FROM permissions WHERE code != 'organization.delete';

-- TechCorp Sales Manager - Sales permissions
INSERT INTO role_permissions (id, role_id, permission_id) VALUES
(gen_random_uuid(), '44444444-4444-4444-4444-444444444403', '11111111-1111-1111-1111-111111111102'),
(gen_random_uuid(), '44444444-4444-4444-4444-444444444403', '11111111-1111-1111-1111-111111111601'),
(gen_random_uuid(), '44444444-4444-4444-4444-444444444403', '11111111-1111-1111-1111-111111111602'),
(gen_random_uuid(), '44444444-4444-4444-4444-444444444403', '11111111-1111-1111-1111-111111111603'),
(gen_random_uuid(), '44444444-4444-4444-4444-444444444403', '11111111-1111-1111-1111-111111111604'),
(gen_random_uuid(), '44444444-4444-4444-4444-444444444403', '11111111-1111-1111-1111-111111111701'),
(gen_random_uuid(), '44444444-4444-4444-4444-444444444403', '11111111-1111-1111-1111-111111111702'),
(gen_random_uuid(), '44444444-4444-4444-4444-444444444403', '11111111-1111-1111-1111-111111111703'),
(gen_random_uuid(), '44444444-4444-4444-4444-444444444403', '11111111-1111-1111-1111-111111111704');

-- TechCorp Sales Rep - Limited sales permissions
INSERT INTO role_permissions (id, role_id, permission_id) VALUES
(gen_random_uuid(), '44444444-4444-4444-4444-444444444404', '11111111-1111-1111-1111-111111111601'),
(gen_random_uuid(), '44444444-4444-4444-4444-444444444404', '11111111-1111-1111-1111-111111111602'),
(gen_random_uuid(), '44444444-4444-4444-4444-444444444404', '11111111-1111-1111-1111-111111111603'),
(gen_random_uuid(), '44444444-4444-4444-4444-444444444404', '11111111-1111-1111-1111-111111111701'),
(gen_random_uuid(), '44444444-4444-4444-4444-444444444404', '11111111-1111-1111-1111-111111111702'),
(gen_random_uuid(), '44444444-4444-4444-4444-444444444404', '11111111-1111-1111-1111-111111111703');

-- GlobalTrade Owner - All permissions
INSERT INTO role_permissions (id, role_id, permission_id) 
SELECT gen_random_uuid(), '44444444-4444-4444-4444-444444444411', id FROM permissions;

-- GlobalTrade Admin - All except organization delete
INSERT INTO role_permissions (id, role_id, permission_id)
SELECT gen_random_uuid(), '44444444-4444-4444-4444-444444444412', id 
FROM permissions WHERE code != 'organization.delete';

-- =====================================================
-- 6. USER_ORGANIZATION_ROLES
-- =====================================================
INSERT INTO user_organization_roles (id, user_id, role_id, is_active, status) VALUES
-- TechCorp
(gen_random_uuid(), '33333333-3333-3333-3333-333333333301', '44444444-4444-4444-4444-444444444401', true, 'active'), -- Sarah - Owner
(gen_random_uuid(), '33333333-3333-3333-3333-333333333302', '44444444-4444-4444-4444-444444444402', true, 'active'), -- David - Admin
(gen_random_uuid(), '33333333-3333-3333-3333-333333333303', '44444444-4444-4444-4444-444444444403', true, 'active'), -- Emily - Sales Manager
(gen_random_uuid(), '33333333-3333-3333-3333-333333333304', '44444444-4444-4444-4444-444444444404', true, 'active'), -- James - Sales Rep
-- GlobalTrade
(gen_random_uuid(), '33333333-3333-3333-3333-333333333311', '44444444-4444-4444-4444-444444444411', true, 'active'), -- Michael - Owner
(gen_random_uuid(), '33333333-3333-3333-3333-333333333312', '44444444-4444-4444-4444-444444444412', true, 'active'); -- Amanda - Admin

-- =====================================================
-- Summary
-- =====================================================
SELECT 'permissions', COUNT(*) FROM permissions
UNION ALL
SELECT 'organizations', COUNT(*) FROM organizations
UNION ALL
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'roles', COUNT(*) FROM roles
UNION ALL
SELECT 'role_permissions', COUNT(*) FROM role_permissions
UNION ALL
SELECT 'user_organization_roles', COUNT(*) FROM user_organization_roles;
