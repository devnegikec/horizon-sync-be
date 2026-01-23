-- =====================================================
-- ERP System - Auth & User Management Seed Data
-- =====================================================
-- This script creates realistic seed data for:
-- 1. Permissions (system-wide capabilities)
-- 2. Organizations (2 companies)
-- 3. Roles (with different permission levels)
-- 4. Users (owners, admins, managers, staff)
-- 5. Teams (departments)
-- 6. Invitations (pending user invites)
-- =====================================================

-- Clean existing data (in reverse order of dependencies)
DELETE FROM invitations;
DELETE FROM user_teams;
DELETE FROM team_members;
DELETE FROM user_organization_roles;
DELETE FROM role_permissions;
DELETE FROM teams;
DELETE FROM roles;
DELETE FROM users;
DELETE FROM organization_settings;
DELETE FROM organizations;
DELETE FROM permissions;

-- =====================================================
-- 1. PERMISSIONS - System-wide capabilities
-- =====================================================
-- These define what actions can be performed on resources
-- Format: resource.action (e.g., user.create, invoice.read)

INSERT INTO permissions (id, code, name, description, resource, action, module, category, is_active, created_at, updated_at) VALUES

-- User Management Permissions
('11111111-1111-1111-1111-111111111101', 'user.create', 'Create Users', 'Create new users in the organization', 'user', 'create', 'user_management', 'users', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111111102', 'user.read', 'View Users', 'View user information', 'user', 'read', 'user_management', 'users', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111111103', 'user.update', 'Update Users', 'Update user information', 'user', 'update', 'user_management', 'users', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111111104', 'user.delete', 'Delete Users', 'Delete users from the organization', 'user', 'delete', 'user_management', 'users', true, NOW(), NOW()),

-- Organization Management Permissions
('11111111-1111-1111-1111-111111111201', 'organization.create', 'Create Organizations', 'Create new organizations', 'organization', 'create', 'user_management', 'organizations', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111111202', 'organization.read', 'View Organizations', 'View organization information', 'organization', 'read', 'user_management', 'organizations', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111111203', 'organization.update', 'Update Organizations', 'Update organization settings', 'organization', 'update', 'user_management', 'organizations', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111111204', 'organization.delete', 'Delete Organizations', 'Delete organizations', 'organization', 'delete', 'user_management', 'organizations', true, NOW(), NOW()),

-- Team Management Permissions
('11111111-1111-1111-1111-111111111301', 'team.create', 'Create Teams', 'Create new teams', 'team', 'create', 'user_management', 'teams', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111111302', 'team.read', 'View Teams', 'View team information', 'team', 'read', 'user_management', 'teams', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111111303', 'team.update', 'Update Teams', 'Update team information', 'team', 'update', 'user_management', 'teams', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111111304', 'team.delete', 'Delete Teams', 'Delete teams', 'team', 'delete', 'user_management', 'teams', true, NOW(), NOW()),

-- Role Management Permissions
('11111111-1111-1111-1111-111111111401', 'role.create', 'Create Roles', 'Create new roles', 'role', 'create', 'user_management', 'roles', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111111402', 'role.read', 'View Roles', 'View role information', 'role', 'read', 'user_management', 'roles', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111111403', 'role.update', 'Update Roles', 'Update role permissions', 'role', 'update', 'user_management', 'roles', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111111404', 'role.delete', 'Delete Roles', 'Delete roles', 'role', 'delete', 'user_management', 'roles', true, NOW(), NOW()),

-- Audit & Activity Permissions
('11111111-1111-1111-1111-111111111501', 'audit.read', 'View Audit Logs', 'View audit logs', 'audit', 'read', 'user_management', 'audit', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111111502', 'activity.read', 'View Activity Logs', 'View activity logs', 'activity', 'read', 'user_management', 'activity', true, NOW(), NOW()),

-- Lead Management Permissions
('11111111-1111-1111-1111-111111111601', 'lead.create', 'Create Leads', 'Create new leads', 'lead', 'create', 'lead_to_order', 'leads', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111111602', 'lead.read', 'View Leads', 'View lead information', 'lead', 'read', 'lead_to_order', 'leads', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111111603', 'lead.update', 'Update Leads', 'Update lead information', 'lead', 'update', 'lead_to_order', 'leads', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111111604', 'lead.delete', 'Delete Leads', 'Delete leads', 'lead', 'delete', 'lead_to_order', 'leads', true, NOW(), NOW()),

-- Contact Management Permissions
('11111111-1111-1111-1111-111111111701', 'contact.create', 'Create Contacts', 'Create new contacts', 'contact', 'create', 'lead_to_order', 'contacts', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111111702', 'contact.read', 'View Contacts', 'View contact information', 'contact', 'read', 'lead_to_order', 'contacts', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111111703', 'contact.update', 'Update Contacts', 'Update contact information', 'contact', 'update', 'lead_to_order', 'contacts', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111111704', 'contact.delete', 'Delete Contacts', 'Delete contacts', 'contact', 'delete', 'lead_to_order', 'contacts', true, NOW(), NOW()),

-- Deal Management Permissions
('11111111-1111-1111-1111-111111111801', 'deal.create', 'Create Deals', 'Create new deals', 'deal', 'create', 'lead_to_order', 'deals', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111111802', 'deal.read', 'View Deals', 'View deal information', 'deal', 'read', 'lead_to_order', 'deals', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111111803', 'deal.update', 'Update Deals', 'Update deal information', 'deal', 'update', 'lead_to_order', 'deals', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111111804', 'deal.delete', 'Delete Deals', 'Delete deals', 'deal', 'delete', 'lead_to_order', 'deals', true, NOW(), NOW()),

-- Order Management Permissions
('11111111-1111-1111-1111-111111111901', 'order.create', 'Create Orders', 'Create new orders', 'order', 'create', 'lead_to_order', 'orders', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111111902', 'order.read', 'View Orders', 'View order information', 'order', 'read', 'lead_to_order', 'orders', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111111903', 'order.update', 'Update Orders', 'Update order information', 'order', 'update', 'lead_to_order', 'orders', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111111904', 'order.delete', 'Delete Orders', 'Delete orders', 'order', 'delete', 'lead_to_order', 'orders', true, NOW(), NOW()),

-- Support Ticket Permissions
('11111111-1111-1111-1111-111111112001', 'ticket.create', 'Create Tickets', 'Create support tickets', 'ticket', 'create', 'support', 'tickets', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111112002', 'ticket.read', 'View Tickets', 'View support tickets', 'ticket', 'read', 'support', 'tickets', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111112003', 'ticket.update', 'Update Tickets', 'Update support tickets', 'ticket', 'update', 'support', 'tickets', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111112004', 'ticket.delete', 'Delete Tickets', 'Delete support tickets', 'ticket', 'delete', 'support', 'tickets', true, NOW(), NOW()),

-- Billing & Accounting Permissions
('11111111-1111-1111-1111-111111112101', 'invoice.create', 'Create Invoices', 'Create invoices', 'invoice', 'create', 'billing', 'invoices', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111112102', 'invoice.read', 'View Invoices', 'View invoices', 'invoice', 'read', 'billing', 'invoices', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111112103', 'invoice.update', 'Update Invoices', 'Update invoices', 'invoice', 'update', 'billing', 'invoices', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111112104', 'invoice.delete', 'Delete Invoices', 'Delete invoices', 'invoice', 'delete', 'billing', 'invoices', true, NOW(), NOW()),

-- Payment Permissions
('11111111-1111-1111-1111-111111112201', 'payment.create', 'Create Payments', 'Record payments', 'payment', 'create', 'billing', 'payments', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111112202', 'payment.read', 'View Payments', 'View payment records', 'payment', 'read', 'billing', 'payments', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111112203', 'payment.update', 'Update Payments', 'Update payment records', 'payment', 'update', 'billing', 'payments', true, NOW(), NOW()),
('11111111-1111-1111-1111-111111112204', 'payment.delete', 'Delete Payments', 'Delete payment records', 'payment', 'delete', 'billing', 'payments', true, NOW(), NOW());


-- =====================================================
-- 2. ORGANIZATIONS - Two sample companies
-- =====================================================

INSERT INTO organizations (id, name, slug, display_name, description, email, phone, website, 
    address_line1, address_line2, city, state, postal_code, country, 
    organization_type, industry, tax_id, logo_url, primary_color, domain, 
    sso_enabled, status, is_active, owner_id, created_at, updated_at) VALUES

-- Organization 1: TechCorp Solutions (Technology Company)
('22222222-2222-2222-2222-222222222201', 
 'TechCorp Solutions', 
 'techcorp-solutions', 
 'TechCorp Solutions Inc.', 
 'Leading provider of enterprise software solutions and IT consulting services',
 'contact@techcorp.com',
 '+1-555-0100',
 'https://www.techcorp.com',
 '123 Innovation Drive',
 'Suite 500',
 'San Francisco',
 'California',
 '94105',
 'United States',
 'enterprise',
 'Technology',
 'TAX-123456789',
 'https://cdn.techcorp.com/logo.png',
 '#0066CC',
 'techcorp.com',
 false,
 'active',
 true,
 '33333333-3333-3333-3333-333333333301', -- Will be created below (Sarah Johnson - Owner)
 NOW(),
 NOW()),

-- Organization 2: GlobalTrade Inc (Manufacturing & Distribution)
('22222222-2222-2222-2222-222222222202',
 'GlobalTrade Inc',
 'globaltrade-inc',
 'GlobalTrade International Inc.',
 'International trading company specializing in manufacturing and distribution',
 'info@globaltrade.com',
 '+1-555-0200',
 'https://www.globaltrade.com',
 '456 Commerce Boulevard',
 'Building B',
 'Chicago',
 'Illinois',
 '60601',
 'United States',
 'enterprise',
 'Manufacturing',
 'TAX-987654321',
 'https://cdn.globaltrade.com/logo.png',
 '#CC0000',
 'globaltrade.com',
 false,
 'active',
 true,
 '33333333-3333-3333-3333-333333333311', -- Will be created below (Michael Chen - Owner)
 NOW(),
 NOW());


-- =====================================================
-- 3. USERS - Various roles across organizations
-- =====================================================
-- Password for all users: "Password123!" (hashed with bcrypt)
-- Hash: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.Hs7HO6

INSERT INTO users (id, email, password_hash, first_name, last_name, display_name, phone, avatar_url,
    user_type, status, is_active, email_verified, email_verified_at, mfa_enabled, 
    last_login_at, failed_login_attempts, timezone, language, created_at, updated_at) VALUES

-- ===== TECHCORP SOLUTIONS USERS =====

-- 1. Sarah Johnson - Owner/CEO of TechCorp
('33333333-3333-3333-3333-333333333301',
 'sarah.johnson@techcorp.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.Hs7HO6',
 'Sarah',
 'Johnson',
 'Sarah Johnson',
 '+1-555-0101',
 'https://i.pravatar.cc/150?img=1',
 'internal',
 'active',
 true,
 true,
 NOW() - INTERVAL '90 days',
 true,
 NOW() - INTERVAL '2 hours',
 0,
 'America/Los_Angeles',
 'en',
 NOW() - INTERVAL '2 years',
 NOW()),

-- 2. David Martinez - CTO/Admin
('33333333-3333-3333-3333-333333333302',
 'david.martinez@techcorp.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.Hs7HO6',
 'David',
 'Martinez',
 'David Martinez',
 '+1-555-0102',
 'https://i.pravatar.cc/150?img=12',
 'internal',
 'active',
 true,
 true,
 NOW() - INTERVAL '85 days',
 true,
 NOW() - INTERVAL '5 hours',
 0,
 'America/Los_Angeles',
 'en',
 NOW() - INTERVAL '1 year 8 months',
 NOW()),

-- 3. Emily Chen - Sales Manager
('33333333-3333-3333-3333-333333333303',
 'emily.chen@techcorp.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.Hs7HO6',
 'Emily',
 'Chen',
 'Emily Chen',
 '+1-555-0103',
 'https://i.pravatar.cc/150?img=5',
 'internal',
 'active',
 true,
 true,
 NOW() - INTERVAL '60 days',
 false,
 NOW() - INTERVAL '1 day',
 0,
 'America/Los_Angeles',
 'en',
 NOW() - INTERVAL '1 year 3 months',
 NOW()),

-- 4. James Wilson - Sales Representative
('33333333-3333-3333-3333-333333333304',
 'james.wilson@techcorp.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.Hs7HO6',
 'James',
 'Wilson',
 'James Wilson',
 '+1-555-0104',
 'https://i.pravatar.cc/150?img=13',
 'internal',
 'active',
 true,
 true,
 NOW() - INTERVAL '45 days',
 false,
 NOW() - INTERVAL '3 hours',
 0,
 'America/Los_Angeles',
 'en',
 NOW() - INTERVAL '8 months',
 NOW()),

-- 5. Lisa Anderson - Support Manager
('33333333-3333-3333-3333-333333333305',
 'lisa.anderson@techcorp.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.Hs7HO6',
 'Lisa',
 'Anderson',
 'Lisa Anderson',
 '+1-555-0105',
 'https://i.pravatar.cc/150?img=9',
 'internal',
 'active',
 true,
 true,
 NOW() - INTERVAL '30 days',
 false,
 NOW() - INTERVAL '6 hours',
 0,
 'America/Los_Angeles',
 'en',
 NOW() - INTERVAL '1 year',
 NOW()),

-- 6. Robert Taylor - Support Agent
('33333333-3333-3333-3333-333333333306',
 'robert.taylor@techcorp.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.Hs7HO6',
 'Robert',
 'Taylor',
 'Robert Taylor',
 '+1-555-0106',
 'https://i.pravatar.cc/150?img=14',
 'internal',
 'active',
 true,
 true,
 NOW() - INTERVAL '20 days',
 false,
 NOW() - INTERVAL '1 hour',
 0,
 'America/Los_Angeles',
 'en',
 NOW() - INTERVAL '6 months',
 NOW()),

-- 7. Jennifer Lee - Finance Manager
('33333333-3333-3333-3333-333333333307',
 'jennifer.lee@techcorp.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.Hs7HO6',
 'Jennifer',
 'Lee',
 'Jennifer Lee',
 '+1-555-0107',
 'https://i.pravatar.cc/150?img=10',
 'internal',
 'active',
 true,
 true,
 NOW() - INTERVAL '25 days',
 true,
 NOW() - INTERVAL '4 hours',
 0,
 'America/Los_Angeles',
 'en',
 NOW() - INTERVAL '1 year 6 months',
 NOW()),


-- ===== GLOBALTRADE INC USERS =====

-- 8. Michael Chen - Owner/CEO of GlobalTrade
('33333333-3333-3333-3333-333333333311',
 'michael.chen@globaltrade.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.Hs7HO6',
 'Michael',
 'Chen',
 'Michael Chen',
 '+1-555-0201',
 'https://i.pravatar.cc/150?img=15',
 'internal',
 'active',
 true,
 true,
 NOW() - INTERVAL '100 days',
 true,
 NOW() - INTERVAL '1 hour',
 0,
 'America/Chicago',
 'en',
 NOW() - INTERVAL '3 years',
 NOW()),

-- 9. Amanda Rodriguez - COO/Admin
('33333333-3333-3333-3333-333333333312',
 'amanda.rodriguez@globaltrade.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.Hs7HO6',
 'Amanda',
 'Rodriguez',
 'Amanda Rodriguez',
 '+1-555-0202',
 'https://i.pravatar.cc/150?img=20',
 'internal',
 'active',
 true,
 true,
 NOW() - INTERVAL '95 days',
 true,
 NOW() - INTERVAL '3 hours',
 0,
 'America/Chicago',
 'en',
 NOW() - INTERVAL '2 years 6 months',
 NOW()),

-- 10. Daniel Kim - Operations Manager
('33333333-3333-3333-3333-333333333313',
 'daniel.kim@globaltrade.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.Hs7HO6',
 'Daniel',
 'Kim',
 'Daniel Kim',
 '+1-555-0203',
 'https://i.pravatar.cc/150?img=33',
 'internal',
 'active',
 true,
 true,
 NOW() - INTERVAL '50 days',
 false,
 NOW() - INTERVAL '2 days',
 0,
 'America/Chicago',
 'en',
 NOW() - INTERVAL '1 year 9 months',
 NOW()),

-- 11. Sophia Patel - Warehouse Supervisor
('33333333-3333-3333-3333-333333333314',
 'sophia.patel@globaltrade.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.Hs7HO6',
 'Sophia',
 'Patel',
 'Sophia Patel',
 '+1-555-0204',
 'https://i.pravatar.cc/150?img=25',
 'internal',
 'active',
 true,
 true,
 NOW() - INTERVAL '40 days',
 false,
 NOW() - INTERVAL '5 hours',
 0,
 'America/Chicago',
 'en',
 NOW() - INTERVAL '1 year 2 months',
 NOW()),

-- 12. Thomas Brown - Accountant
('33333333-3333-3333-3333-333333333315',
 'thomas.brown@globaltrade.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.Hs7HO6',
 'Thomas',
 'Brown',
 'Thomas Brown',
 '+1-555-0205',
 'https://i.pravatar.cc/150?img=32',
 'internal',
 'active',
 true,
 true,
 NOW() - INTERVAL '35 days',
 false,
 NOW() - INTERVAL '7 hours',
 0,
 'America/Chicago',
 'en',
 NOW() - INTERVAL '10 months',
 NOW()),

-- 13. Maria Garcia - Sales Representative
('33333333-3333-3333-3333-333333333316',
 'maria.garcia@globaltrade.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.Hs7HO6',
 'Maria',
 'Garcia',
 'Maria Garcia',
 '+1-555-0206',
 'https://i.pravatar.cc/150?img=24',
 'internal',
 'active',
 true,
 true,
 NOW() - INTERVAL '28 days',
 false,
 NOW() - INTERVAL '4 hours',
 0,
 'America/Chicago',
 'en',
 NOW() - INTERVAL '7 months',
 NOW());


-- =====================================================
-- 4. ROLES - Different permission levels per organization
-- =====================================================

INSERT INTO roles (id, organization_id, name, code, description, is_system, is_default, hierarchy_level, is_active, created_at, updated_at) VALUES

-- ===== TECHCORP SOLUTIONS ROLES =====

-- Owner Role - Full access to everything
('44444444-4444-4444-4444-444444444401',
 '22222222-2222-2222-2222-222222222201',
 'Owner',
 'OWNER',
 'Organization owner with full administrative access to all features and settings',
 true,
 false,
 1,
 true,
 NOW(),
 NOW()),

-- Admin Role - Almost full access, cannot delete organization
('44444444-4444-4444-4444-444444444402',
 '22222222-2222-2222-2222-222222222201',
 'Administrator',
 'ADMIN',
 'System administrator with full access to manage users, teams, and most settings',
 true,
 false,
 2,
 true,
 NOW(),
 NOW()),

-- Sales Manager Role - Manage sales team and all sales operations
('44444444-4444-4444-4444-444444444403',
 '22222222-2222-2222-2222-222222222201',
 'Sales Manager',
 'SALES_MANAGER',
 'Manages sales team, leads, contacts, deals, and orders',
 false,
 false,
 3,
 true,
 NOW(),
 NOW()),

-- Sales Representative Role - Limited to own sales activities
('44444444-4444-4444-4444-444444444404',
 '22222222-2222-2222-2222-222222222201',
 'Sales Representative',
 'SALES_REP',
 'Can create and manage own leads, contacts, and deals',
 false,
 true,
 4,
 true,
 NOW(),
 NOW()),

-- Support Manager Role - Manage support team and tickets
('44444444-4444-4444-4444-444444444405',
 '22222222-2222-2222-2222-222222222201',
 'Support Manager',
 'SUPPORT_MANAGER',
 'Manages support team and all customer support tickets',
 false,
 false,
 3,
 true,
 NOW(),
 NOW()),

-- Support Agent Role - Handle assigned tickets
('44444444-4444-4444-4444-444444444406',
 '22222222-2222-2222-2222-222222222201',
 'Support Agent',
 'SUPPORT_AGENT',
 'Can view and respond to assigned support tickets',
 false,
 false,
 4,
 true,
 NOW(),
 NOW()),

-- Finance Manager Role - Full access to billing and accounting
('44444444-4444-4444-4444-444444444407',
 '22222222-2222-2222-2222-222222222201',
 'Finance Manager',
 'FINANCE_MANAGER',
 'Manages all financial operations including invoices, payments, and accounting',
 false,
 false,
 3,
 true,
 NOW(),
 NOW()),

-- ===== GLOBALTRADE INC ROLES =====

-- Owner Role
('44444444-4444-4444-4444-444444444411',
 '22222222-2222-2222-2222-222222222202',
 'Owner',
 'OWNER',
 'Organization owner with full administrative access',
 true,
 false,
 1,
 true,
 NOW(),
 NOW()),

-- Admin Role
('44444444-4444-4444-4444-444444444412',
 '22222222-2222-2222-2222-222222222202',
 'Administrator',
 'ADMIN',
 'System administrator with full access to manage operations',
 true,
 false,
 2,
 true,
 NOW(),
 NOW()),

-- Operations Manager Role
('44444444-4444-4444-4444-444444444413',
 '22222222-2222-2222-2222-222222222202',
 'Operations Manager',
 'OPS_MANAGER',
 'Manages operations, orders, and logistics',
 false,
 false,
 3,
 true,
 NOW(),
 NOW()),

-- Warehouse Supervisor Role
('44444444-4444-4444-4444-444444444414',
 '22222222-2222-2222-2222-222222222202',
 'Warehouse Supervisor',
 'WAREHOUSE_SUPERVISOR',
 'Manages warehouse operations and inventory',
 false,
 false,
 4,
 true,
 NOW(),
 NOW()),

-- Accountant Role
('44444444-4444-4444-4444-444444444415',
 '22222222-2222-2222-2222-222222222202',
 'Accountant',
 'ACCOUNTANT',
 'Manages financial records and accounting',
 false,
 false,
 4,
 true,
 NOW(),
 NOW()),

-- Sales Representative Role
('44444444-4444-4444-4444-444444444416',
 '22222222-2222-2222-2222-222222222202',
 'Sales Representative',
 'SALES_REP',
 'Handles sales and customer relationships',
 false,
 true,
 4,
 true,
 NOW(),
 NOW());


-- =====================================================
-- 5. ROLE_PERMISSIONS - Assign permissions to roles
-- =====================================================

-- ===== TECHCORP OWNER ROLE - ALL PERMISSIONS =====
INSERT INTO role_permissions (id, role_id, permission_id) 
SELECT 
    gen_random_uuid(),
    '44444444-4444-4444-4444-444444444401', -- TechCorp Owner
    id
FROM permissions;

-- ===== TECHCORP ADMIN ROLE - ALL EXCEPT ORGANIZATION DELETE =====
INSERT INTO role_permissions (id, role_id, permission_id)
SELECT 
    gen_random_uuid(),
    '44444444-4444-4444-4444-444444444402', -- TechCorp Admin
    id
FROM permissions
WHERE code != 'organization.delete';

-- ===== TECHCORP SALES MANAGER - Sales + Team Management =====
INSERT INTO role_permissions (id, role_id, permission_id) VALUES
-- User permissions (read only)
(gen_random_uuid(), '44444444-4444-4444-4444-444444444403', '11111111-1111-1111-1111-111111111102'), -- user.read
-- Team permissions (full)
(gen_random_uuid(), '44444444-4444-4444-4444-444444444403', '11111111-1111-1111-1111-111111111301'), -- team.create
(gen_random_uuid(), '44444444-4444-4444-4444-444444444403', '11111111-1111-1111-1111-111111111302'), -- team.read
(gen_random_uuid(), '44444444-4444-4444-4444-444444444403', '11111111-1111-1111-1111-111111111303'), -- team.update
-- Lead permissions (full)
(gen_random_uuid(), '44444444-4444-4444-4444-444444444403', '11111111-1111-1111-1111-111111111601'), -- lead.create
(gen_random_uuid(), '44444444-4444-4444-4444-444444444403', '11111111-1111-1111-1111-111111111602'), -- lead.read
(gen_random_uuid(), '44444444-4444-4444-4444-444444444403', '11111111-1111-1111-1111-111111111603'), -- lead.update
(gen_random_uuid(), '44444444-4444-4444-4444-444444444403', '11111111-1111-1111-1111-111111111604'), -- lead.delete
-- Contact permissions (full)
(gen_random_uuid(), '44444444-4444-4444-4444-444444444403', '11111111-1111-1111-1111-111111111701'), -- contact.create
(gen_random_uuid(), '44444444-4444-4444-4444-444444444403', '11111111-1111-1111-1111-111111111702'), -- contact.read
(gen_random_uuid(), '44444444-4444-4444-4444-444444444403', '11111111-1111-1111-1111-111111111703'), -- contact.update
(gen_random_uuid(), '44444444-4444-4444-4444-444444444403', '11111111-1111-1111-1111-111111111704'), -- contact.delete
-- Deal permissions (full)
(gen_random_uuid(), '44444444-4444-4444-4444-444444444403', '11111111-1111-1111-1111-111111111801'), -- deal.create
(gen_random_uuid(), '44444444-4444-4444-4444-444444444403', '11111111-1111-1111-1111-111111111802'), -- deal.read
(gen_random_uuid(), '44444444-4444-4444-4444-444444444403', '11111111-1111-1111-1111-111111111803'), -- deal.update
(gen_random_uuid(), '44444444-4444-4444-4444-444444444403', '11111111-1111-1111-1111-111111111804'), -- deal.delete
-- Order permissions (full)
(gen_random_uuid(), '44444444-4444-4444-4444-444444444403', '11111111-1111-1111-1111-111111111901'), -- order.create
(gen_random_uuid(), '44444444-4444-4444-4444-444444444403', '11111111-1111-1111-1111-111111111902'), -- order.read
(gen_random_uuid(), '44444444-4444-4444-4444-444444444403', '11111111-1111-1111-1111-111111111903'), -- order.update
(gen_random_uuid(), '44444444-4444-4444-4444-444444444403', '11111111-1111-1111-1111-111111111904'); -- order.delete

-- ===== TECHCORP SALES REP - Limited Sales Access =====
INSERT INTO role_permissions (id, role_id, permission_id) VALUES
-- Lead permissions (create, read, update own)
(gen_random_uuid(), '44444444-4444-4444-4444-444444444404', '11111111-1111-1111-1111-111111111601'), -- lead.create
(gen_random_uuid(), '44444444-4444-4444-4444-444444444404', '11111111-1111-1111-1111-111111111602'), -- lead.read
(gen_random_uuid(), '44444444-4444-4444-4444-444444444404', '11111111-1111-1111-1111-111111111603'), -- lead.update
-- Contact permissions (create, read, update)
(gen_random_uuid(), '44444444-4444-4444-4444-444444444404', '11111111-1111-1111-1111-111111111701'), -- contact.create
(gen_random_uuid(), '44444444-4444-4444-4444-444444444404', '11111111-1111-1111-1111-111111111702'), -- contact.read
(gen_random_uuid(), '44444444-4444-4444-4444-444444444404', '11111111-1111-1111-1111-111111111703'), -- contact.update
-- Deal permissions (create, read, update)
(gen_random_uuid(), '44444444-4444-4444-4444-444444444404', '11111111-1111-1111-1111-111111111801'), -- deal.create
(gen_random_uuid(), '44444444-4444-4444-4444-444444444404', '11111111-1111-1111-1111-111111111802'), -- deal.read
(gen_random_uuid(), '44444444-4444-4444-4444-444444444404', '11111111-1111-1111-1111-111111111803'), -- deal.update
-- Order permissions (read only)
(gen_random_uuid(), '44444444-4444-4444-4444-444444444404', '11111111-1111-1111-1111-111111111902'); -- order.read

-- ===== TECHCORP SUPPORT MANAGER - Support + Team Management =====
INSERT INTO role_permissions (id, role_id, permission_id) VALUES
-- User permissions (read only)
(gen_random_uuid(), '44444444-4444-4444-4444-444444444405', '11111111-1111-1111-1111-111111111102'), -- user.read
-- Team permissions (read, update)
(gen_random_uuid(), '44444444-4444-4444-4444-444444444405', '11111111-1111-1111-1111-111111111302'), -- team.read
(gen_random_uuid(), '44444444-4444-4444-4444-444444444405', '11111111-1111-1111-1111-111111111303'), -- team.update
-- Ticket permissions (full)
(gen_random_uuid(), '44444444-4444-4444-4444-444444444405', '11111111-1111-1111-1111-111111112001'), -- ticket.create
(gen_random_uuid(), '44444444-4444-4444-4444-444444444405', '11111111-1111-1111-1111-111111112002'), -- ticket.read
(gen_random_uuid(), '44444444-4444-4444-4444-444444444405', '11111111-1111-1111-1111-111111112003'), -- ticket.update
(gen_random_uuid(), '44444444-4444-4444-4444-444444444405', '11111111-1111-1111-1111-111111112004'); -- ticket.delete

-- ===== TECHCORP SUPPORT AGENT - Limited Support Access =====
INSERT INTO role_permissions (id, role_id, permission_id) VALUES
-- Ticket permissions (create, read, update)
(gen_random_uuid(), '44444444-4444-4444-4444-444444444406', '11111111-1111-1111-1111-111111112001'), -- ticket.create
(gen_random_uuid(), '44444444-4444-4444-4444-444444444406', '11111111-1111-1111-1111-111111112002'), -- ticket.read
(gen_random_uuid(), '44444444-4444-4444-4444-444444444406', '11111111-1111-1111-1111-111111112003'); -- ticket.update

-- ===== TECHCORP FINANCE MANAGER - Full Financial Access =====
INSERT INTO role_permissions (id, role_id, permission_id) VALUES
-- User permissions (read only)
(gen_random_uuid(), '44444444-4444-4444-4444-444444444407', '11111111-1111-1111-1111-111111111102'), -- user.read
-- Invoice permissions (full)
(gen_random_uuid(), '44444444-4444-4444-4444-444444444407', '11111111-1111-1111-1111-111111112101'), -- invoice.create
(gen_random_uuid(), '44444444-4444-4444-4444-444444444407', '11111111-1111-1111-1111-111111112102'), -- invoice.read
(gen_random_uuid(), '44444444-4444-4444-4444-444444444407', '11111111-1111-1111-1111-111111112103'), -- invoice.update
(gen_random_uuid(), '44444444-4444-4444-4444-444444444407', '11111111-1111-1111-1111-111111112104'), -- invoice.delete
-- Payment permissions (full)
(gen_random_uuid(), '44444444-4444-4444-4444-444444444407', '11111111-1111-1111-1111-111111112201'), -- payment.create
(gen_random_uuid(), '44444444-4444-4444-4444-444444444407', '11111111-1111-1111-1111-111111112202'), -- payment.read
(gen_random_uuid(), '44444444-4444-4444-4444-444444444407', '11111111-1111-1111-1111-111111112203'), -- payment.update
(gen_random_uuid(), '44444444-4444-4444-4444-444444444407', '11111111-1111-1111-1111-111111112204'), -- payment.delete
-- Audit permissions
(gen_random_uuid(), '44444444-4444-4444-4444-444444444407', '11111111-1111-1111-1111-111111111501'); -- audit.read


-- ===== GLOBALTRADE OWNER ROLE - ALL PERMISSIONS =====
INSERT INTO role_permissions (id, role_id, permission_id) 
SELECT 
    gen_random_uuid(),
    '44444444-4444-4444-4444-444444444411', -- GlobalTrade Owner
    id
FROM permissions;

-- ===== GLOBALTRADE ADMIN ROLE - ALL EXCEPT ORGANIZATION DELETE =====
INSERT INTO role_permissions (id, role_id, permission_id)
SELECT 
    gen_random_uuid(),
    '44444444-4444-4444-4444-444444444412', -- GlobalTrade Admin
    id
FROM permissions
WHERE code != 'organization.delete';

-- ===== GLOBALTRADE OPERATIONS MANAGER =====
INSERT INTO role_permissions (id, role_id, permission_id) VALUES
-- User permissions (read only)
(gen_random_uuid(), '44444444-4444-4444-4444-444444444413', '11111111-1111-1111-1111-111111111102'), -- user.read
-- Team permissions (read, update)
(gen_random_uuid(), '44444444-4444-4444-4444-444444444413', '11111111-1111-1111-1111-111111111302'), -- team.read
(gen_random_uuid(), '44444444-4444-4444-4444-444444444413', '11111111-1111-1111-1111-111111111303'), -- team.update
-- Order permissions (full)
(gen_random_uuid(), '44444444-4444-4444-4444-444444444413', '11111111-1111-1111-1111-111111111901'), -- order.create
(gen_random_uuid(), '44444444-4444-4444-4444-444444444413', '11111111-1111-1111-1111-111111111902'), -- order.read
(gen_random_uuid(), '44444444-4444-4444-4444-444444444413', '11111111-1111-1111-1111-111111111903'), -- order.update
(gen_random_uuid(), '44444444-4444-4444-4444-444444444413', '11111111-1111-1111-1111-111111111904'), -- order.delete
-- Contact permissions (read)
(gen_random_uuid(), '44444444-4444-4444-4444-444444444413', '11111111-1111-1111-1111-111111111702'); -- contact.read

-- ===== GLOBALTRADE WAREHOUSE SUPERVISOR =====
INSERT INTO role_permissions (id, role_id, permission_id) VALUES
-- Order permissions (read, update)
(gen_random_uuid(), '44444444-4444-4444-4444-444444444414', '11111111-1111-1111-1111-111111111902'), -- order.read
(gen_random_uuid(), '44444444-4444-4444-4444-444444444414', '11111111-1111-1111-1111-111111111903'); -- order.update

-- ===== GLOBALTRADE ACCOUNTANT =====
INSERT INTO role_permissions (id, role_id, permission_id) VALUES
-- Invoice permissions (full)
(gen_random_uuid(), '44444444-4444-4444-4444-444444444415', '11111111-1111-1111-1111-111111112101'), -- invoice.create
(gen_random_uuid(), '44444444-4444-4444-4444-444444444415', '11111111-1111-1111-1111-111111112102'), -- invoice.read
(gen_random_uuid(), '44444444-4444-4444-4444-444444444415', '11111111-1111-1111-1111-111111112103'), -- invoice.update
-- Payment permissions (create, read, update)
(gen_random_uuid(), '44444444-4444-4444-4444-444444444415', '11111111-1111-1111-1111-111111112201'), -- payment.create
(gen_random_uuid(), '44444444-4444-4444-4444-444444444415', '11111111-1111-1111-1111-111111112202'), -- payment.read
(gen_random_uuid(), '44444444-4444-4444-4444-444444444415', '11111111-1111-1111-1111-111111112203'); -- payment.update

-- ===== GLOBALTRADE SALES REP =====
INSERT INTO role_permissions (id, role_id, permission_id) VALUES
-- Lead permissions (create, read, update)
(gen_random_uuid(), '44444444-4444-4444-4444-444444444416', '11111111-1111-1111-1111-111111111601'), -- lead.create
(gen_random_uuid(), '44444444-4444-4444-4444-444444444416', '11111111-1111-1111-1111-111111111602'), -- lead.read
(gen_random_uuid(), '44444444-4444-4444-4444-444444444416', '11111111-1111-1111-1111-111111111603'), -- lead.update
-- Contact permissions (create, read, update)
(gen_random_uuid(), '44444444-4444-4444-4444-444444444416', '11111111-1111-1111-1111-111111111701'), -- contact.create
(gen_random_uuid(), '44444444-4444-4444-4444-444444444416', '11111111-1111-1111-1111-111111111702'), -- contact.read
(gen_random_uuid(), '44444444-4444-4444-4444-444444444416', '11111111-1111-1111-1111-111111111703'), -- contact.update
-- Deal permissions (create, read, update)
(gen_random_uuid(), '44444444-4444-4444-4444-444444444416', '11111111-1111-1111-1111-111111111801'), -- deal.create
(gen_random_uuid(), '44444444-4444-4444-4444-444444444416', '11111111-1111-1111-1111-111111111802'), -- deal.read
(gen_random_uuid(), '44444444-4444-4444-4444-444444444416', '11111111-1111-1111-1111-111111111803'); -- deal.update


-- =====================================================
-- 6. USER_ORGANIZATION_ROLES - Assign users to roles
-- =====================================================

INSERT INTO user_organization_roles (id, user_id, organization_id, role_id, is_primary, is_active, status, joined_at, created_at, updated_at) VALUES

-- ===== TECHCORP SOLUTIONS =====

-- Sarah Johnson - Owner
('55555555-5555-5555-5555-555555555501',
 '33333333-3333-3333-3333-333333333301',
 '22222222-2222-2222-2222-222222222201',
 '44444444-4444-4444-4444-444444444401',
 true,
 true,
 'active',
 NOW() - INTERVAL '2 years',
 NOW() - INTERVAL '2 years',
 NOW()),

-- David Martinez - Admin
('55555555-5555-5555-5555-555555555502',
 '33333333-3333-3333-3333-333333333302',
 '22222222-2222-2222-2222-222222222201',
 '44444444-4444-4444-4444-444444444402',
 true,
 true,
 'active',
 NOW() - INTERVAL '1 year 8 months',
 NOW() - INTERVAL '1 year 8 months',
 NOW()),

-- Emily Chen - Sales Manager
('55555555-5555-5555-5555-555555555503',
 '33333333-3333-3333-3333-333333333303',
 '22222222-2222-2222-2222-222222222201',
 '44444444-4444-4444-4444-444444444403',
 true,
 true,
 'active',
 NOW() - INTERVAL '1 year 3 months',
 NOW() - INTERVAL '1 year 3 months',
 NOW()),

-- James Wilson - Sales Rep
('55555555-5555-5555-5555-555555555504',
 '33333333-3333-3333-3333-333333333304',
 '22222222-2222-2222-2222-222222222201',
 '44444444-4444-4444-4444-444444444404',
 true,
 true,
 'active',
 NOW() - INTERVAL '8 months',
 NOW() - INTERVAL '8 months',
 NOW()),

-- Lisa Anderson - Support Manager
('55555555-5555-5555-5555-555555555505',
 '33333333-3333-3333-3333-333333333305',
 '22222222-2222-2222-2222-222222222201',
 '44444444-4444-4444-4444-444444444405',
 true,
 true,
 'active',
 NOW() - INTERVAL '1 year',
 NOW() - INTERVAL '1 year',
 NOW()),

-- Robert Taylor - Support Agent
('55555555-5555-5555-5555-555555555506',
 '33333333-3333-3333-3333-333333333306',
 '22222222-2222-2222-2222-222222222201',
 '44444444-4444-4444-4444-444444444406',
 true,
 true,
 'active',
 NOW() - INTERVAL '6 months',
 NOW() - INTERVAL '6 months',
 NOW()),

-- Jennifer Lee - Finance Manager
('55555555-5555-5555-5555-555555555507',
 '33333333-3333-3333-3333-333333333307',
 '22222222-2222-2222-2222-222222222201',
 '44444444-4444-4444-4444-444444444407',
 true,
 true,
 'active',
 NOW() - INTERVAL '1 year 6 months',
 NOW() - INTERVAL '1 year 6 months',
 NOW()),

-- ===== GLOBALTRADE INC =====

-- Michael Chen - Owner
('55555555-5555-5555-5555-555555555511',
 '33333333-3333-3333-3333-333333333311',
 '22222222-2222-2222-2222-222222222202',
 '44444444-4444-4444-4444-444444444411',
 true,
 true,
 'active',
 NOW() - INTERVAL '3 years',
 NOW() - INTERVAL '3 years',
 NOW()),

-- Amanda Rodriguez - Admin
('55555555-5555-5555-5555-555555555512',
 '33333333-3333-3333-3333-333333333312',
 '22222222-2222-2222-2222-222222222202',
 '44444444-4444-4444-4444-444444444412',
 true,
 true,
 'active',
 NOW() - INTERVAL '2 years 6 months',
 NOW() - INTERVAL '2 years 6 months',
 NOW()),

-- Daniel Kim - Operations Manager
('55555555-5555-5555-5555-555555555513',
 '33333333-3333-3333-3333-333333333313',
 '22222222-2222-2222-2222-222222222202',
 '44444444-4444-4444-4444-444444444413',
 true,
 true,
 'active',
 NOW() - INTERVAL '1 year 9 months',
 NOW() - INTERVAL '1 year 9 months',
 NOW()),

-- Sophia Patel - Warehouse Supervisor
('55555555-5555-5555-5555-555555555514',
 '33333333-3333-3333-3333-333333333314',
 '22222222-2222-2222-2222-222222222202',
 '44444444-4444-4444-4444-444444444414',
 true,
 true,
 'active',
 NOW() - INTERVAL '1 year 2 months',
 NOW() - INTERVAL '1 year 2 months',
 NOW()),

-- Thomas Brown - Accountant
('55555555-5555-5555-5555-555555555515',
 '33333333-3333-3333-3333-333333333315',
 '22222222-2222-2222-2222-222222222202',
 '44444444-4444-4444-4444-444444444415',
 true,
 true,
 'active',
 NOW() - INTERVAL '10 months',
 NOW() - INTERVAL '10 months',
 NOW()),

-- Maria Garcia - Sales Rep
('55555555-5555-5555-5555-555555555516',
 '33333333-3333-3333-3333-333333333316',
 '22222222-2222-2222-2222-222222222202',
 '44444444-4444-4444-4444-444444444416',
 true,
 true,
 'active',
 NOW() - INTERVAL '7 months',
 NOW() - INTERVAL '7 months',
 NOW());


-- =====================================================
-- 7. TEAMS - Departments within organizations
-- =====================================================

INSERT INTO teams (id, organization_id, name, code, description, team_type, parent_id, lead_user_id, is_active, created_at, updated_at) VALUES

-- ===== TECHCORP SOLUTIONS TEAMS =====

-- Sales Team
('66666666-6666-6666-6666-666666666601',
 '22222222-2222-2222-2222-222222222201',
 'Sales Team',
 'SALES',
 'Responsible for lead generation, customer acquisition, and revenue growth',
 'department',
 NULL,
 '33333333-3333-3333-3333-333333333303', -- Emily Chen (Sales Manager)
 true,
 NOW() - INTERVAL '1 year 6 months',
 NOW()),

-- Support Team
('66666666-6666-6666-6666-666666666602',
 '22222222-2222-2222-2222-222222222201',
 'Customer Support',
 'SUPPORT',
 'Handles customer inquiries, issues, and technical support',
 'department',
 NULL,
 '33333333-3333-3333-3333-333333333305', -- Lisa Anderson (Support Manager)
 true,
 NOW() - INTERVAL '1 year 3 months',
 NOW()),

-- Finance Team
('66666666-6666-6666-6666-666666666603',
 '22222222-2222-2222-2222-222222222201',
 'Finance & Accounting',
 'FINANCE',
 'Manages financial operations, invoicing, and accounting',
 'department',
 NULL,
 '33333333-3333-3333-3333-333333333307', -- Jennifer Lee (Finance Manager)
 true,
 NOW() - INTERVAL '1 year 6 months',
 NOW()),

-- ===== GLOBALTRADE INC TEAMS =====

-- Operations Team
('66666666-6666-6666-6666-666666666611',
 '22222222-2222-2222-2222-222222222202',
 'Operations',
 'OPERATIONS',
 'Manages day-to-day operations, logistics, and order fulfillment',
 'department',
 NULL,
 '33333333-3333-3333-3333-333333333313', -- Daniel Kim (Operations Manager)
 true,
 NOW() - INTERVAL '1 year 9 months',
 NOW()),

-- Warehouse Team
('66666666-6666-6666-6666-666666666612',
 '22222222-2222-2222-2222-222222222202',
 'Warehouse',
 'WAREHOUSE',
 'Handles inventory management, storage, and shipping',
 'department',
 NULL,
 '33333333-3333-3333-3333-333333333314', -- Sophia Patel (Warehouse Supervisor)
 true,
 NOW() - INTERVAL '1 year 2 months',
 NOW()),

-- Finance Team
('66666666-6666-6666-6666-666666666613',
 '22222222-2222-2222-2222-222222222202',
 'Finance',
 'FINANCE',
 'Manages accounting, invoicing, and financial reporting',
 'department',
 NULL,
 '33333333-3333-3333-3333-333333333315', -- Thomas Brown (Accountant)
 true,
 NOW() - INTERVAL '10 months',
 NOW()),

-- Sales Team
('66666666-6666-6666-6666-666666666614',
 '22222222-2222-2222-2222-222222222202',
 'Sales',
 'SALES',
 'Handles customer relationships and sales activities',
 'department',
 NULL,
 '33333333-3333-3333-3333-333333333316', -- Maria Garcia (Sales Rep - acting lead)
 true,
 NOW() - INTERVAL '7 months',
 NOW());


-- =====================================================
-- 8. TEAM_MEMBERS - Assign users to teams
-- =====================================================

INSERT INTO team_members (id, team_id, user_id, role, is_active, joined_at, added_by_id, created_at, updated_at) VALUES

-- ===== TECHCORP SALES TEAM =====

-- Emily Chen - Team Lead
('77777777-7777-7777-7777-777777777701',
 '66666666-6666-6666-6666-666666666601',
 '33333333-3333-3333-3333-333333333303',
 'lead',
 true,
 NOW() - INTERVAL '1 year 3 months',
 '33333333-3333-3333-3333-333333333301', -- Added by Sarah (Owner)
 NOW() - INTERVAL '1 year 3 months',
 NOW()),

-- James Wilson - Member
('77777777-7777-7777-7777-777777777702',
 '66666666-6666-6666-6666-666666666601',
 '33333333-3333-3333-3333-333333333304',
 'member',
 true,
 NOW() - INTERVAL '8 months',
 '33333333-3333-3333-3333-333333333303', -- Added by Emily (Sales Manager)
 NOW() - INTERVAL '8 months',
 NOW()),

-- ===== TECHCORP SUPPORT TEAM =====

-- Lisa Anderson - Team Lead
('77777777-7777-7777-7777-777777777703',
 '66666666-6666-6666-6666-666666666602',
 '33333333-3333-3333-3333-333333333305',
 'lead',
 true,
 NOW() - INTERVAL '1 year',
 '33333333-3333-3333-3333-333333333301', -- Added by Sarah (Owner)
 NOW() - INTERVAL '1 year',
 NOW()),

-- Robert Taylor - Member
('77777777-7777-7777-7777-777777777704',
 '66666666-6666-6666-6666-666666666602',
 '33333333-3333-3333-3333-333333333306',
 'member',
 true,
 NOW() - INTERVAL '6 months',
 '33333333-3333-3333-3333-333333333305', -- Added by Lisa (Support Manager)
 NOW() - INTERVAL '6 months',
 NOW()),

-- ===== TECHCORP FINANCE TEAM =====

-- Jennifer Lee - Team Lead
('77777777-7777-7777-7777-777777777705',
 '66666666-6666-6666-6666-666666666603',
 '33333333-3333-3333-3333-333333333307',
 'lead',
 true,
 NOW() - INTERVAL '1 year 6 months',
 '33333333-3333-3333-3333-333333333301', -- Added by Sarah (Owner)
 NOW() - INTERVAL '1 year 6 months',
 NOW()),

-- ===== GLOBALTRADE OPERATIONS TEAM =====

-- Daniel Kim - Team Lead
('77777777-7777-7777-7777-777777777711',
 '66666666-6666-6666-6666-666666666611',
 '33333333-3333-3333-3333-333333333313',
 'lead',
 true,
 NOW() - INTERVAL '1 year 9 months',
 '33333333-3333-3333-3333-333333333311', -- Added by Michael (Owner)
 NOW() - INTERVAL '1 year 9 months',
 NOW()),

-- ===== GLOBALTRADE WAREHOUSE TEAM =====

-- Sophia Patel - Team Lead
('77777777-7777-7777-7777-777777777712',
 '66666666-6666-6666-6666-666666666612',
 '33333333-3333-3333-3333-333333333314',
 'lead',
 true,
 NOW() - INTERVAL '1 year 2 months',
 '33333333-3333-3333-3333-333333333313', -- Added by Daniel (Ops Manager)
 NOW() - INTERVAL '1 year 2 months',
 NOW()),

-- ===== GLOBALTRADE FINANCE TEAM =====

-- Thomas Brown - Team Lead
('77777777-7777-7777-7777-777777777713',
 '66666666-6666-6666-6666-666666666613',
 '33333333-3333-3333-3333-333333333315',
 'lead',
 true,
 NOW() - INTERVAL '10 months',
 '33333333-3333-3333-3333-333333333312', -- Added by Amanda (Admin)
 NOW() - INTERVAL '10 months',
 NOW()),

-- ===== GLOBALTRADE SALES TEAM =====

-- Maria Garcia - Team Lead
('77777777-7777-7777-7777-777777777714',
 '66666666-6666-6666-6666-666666666614',
 '33333333-3333-3333-3333-333333333316',
 'lead',
 true,
 NOW() - INTERVAL '7 months',
 '33333333-3333-3333-3333-333333333312', -- Added by Amanda (Admin)
 NOW() - INTERVAL '7 months',
 NOW());


-- =====================================================
-- 9. INVITATIONS - Pending user invitations
-- =====================================================

INSERT INTO invitations (id, organization_id, email, first_name, last_name, role_id, team_ids, 
    invited_by_id, token_hash, status, expires_at, message, created_at) VALUES

-- ===== TECHCORP INVITATIONS =====

-- Invitation for new Sales Rep
('88888888-8888-8888-8888-888888888801',
 '22222222-2222-2222-2222-222222222201',
 'john.smith@techcorp.com',
 'John',
 'Smith',
 '44444444-4444-4444-4444-444444444404', -- Sales Rep role
 '["66666666-6666-6666-6666-666666666601"]', -- Sales team
 '33333333-3333-3333-3333-333333333303', -- Invited by Emily (Sales Manager)
 '$2b$12$abcdefghijklmnopqrstuvwxyz123456789ABCDEFGHIJKLMNOP', -- Token hash
 'pending',
 NOW() + INTERVAL '7 days',
 'Welcome to TechCorp! We are excited to have you join our sales team.',
 NOW() - INTERVAL '2 days'),

-- Invitation for new Support Agent
('88888888-8888-8888-8888-888888888802',
 '22222222-2222-2222-2222-222222222201',
 'susan.white@techcorp.com',
 'Susan',
 'White',
 '44444444-4444-4444-4444-444444444406', -- Support Agent role
 '["66666666-6666-6666-6666-666666666602"]', -- Support team
 '33333333-3333-3333-3333-333333333305', -- Invited by Lisa (Support Manager)
 '$2b$12$zyxwvutsrqponmlkjihgfedcba987654321ZYXWVUTSRQPONMLK', -- Token hash
 'pending',
 NOW() + INTERVAL '5 days',
 'Join our support team and help us deliver excellent customer service!',
 NOW() - INTERVAL '1 day'),

-- Expired invitation (example)
('88888888-8888-8888-8888-888888888803',
 '22222222-2222-2222-2222-222222222201',
 'expired.user@techcorp.com',
 'Expired',
 'User',
 '44444444-4444-4444-4444-444444444404', -- Sales Rep role
 '["66666666-6666-6666-6666-666666666601"]', -- Sales team
 '33333333-3333-3333-3333-333333333302', -- Invited by David (Admin)
 '$2b$12$expiredtokenhashexamplexxxxxxxxxxxxxxxxxxxxxxxx', -- Token hash
 'expired',
 NOW() - INTERVAL '3 days',
 'Welcome to TechCorp Sales Team.',
 NOW() - INTERVAL '10 days'),

-- ===== GLOBALTRADE INVITATIONS =====

-- Invitation for new Warehouse Staff
('88888888-8888-8888-8888-888888888811',
 '22222222-2222-2222-2222-222222222202',
 'carlos.rivera@globaltrade.com',
 'Carlos',
 'Rivera',
 '44444444-4444-4444-4444-444444444414', -- Warehouse Supervisor role
 '["66666666-6666-6666-6666-666666666612"]', -- Warehouse team
 '33333333-3333-3333-3333-333333333314', -- Invited by Sophia (Warehouse Supervisor)
 '$2b$12$warehouseinvitationtokenhashexamplexxxxxxxxxxxxxxx', -- Token hash
 'pending',
 NOW() + INTERVAL '6 days',
 'Welcome to GlobalTrade warehouse team. Looking forward to working with you!',
 NOW() - INTERVAL '1 day'),

-- Accepted invitation (example)
('88888888-8888-8888-8888-888888888812',
 '22222222-2222-2222-2222-222222222202',
 'maria.garcia@globaltrade.com',
 'Maria',
 'Garcia',
 '44444444-4444-4444-4444-444444444416', -- Sales Rep role
 '["66666666-6666-6666-6666-666666666614"]', -- Sales team
 '33333333-3333-3333-3333-333333333312', -- Invited by Amanda (Admin)
 '$2b$12$acceptedinvitationtokenhashexamplexxxxxxxxxxxxxxx', -- Token hash
 'accepted',
 NOW() + INTERVAL '7 days',
 'Join our sales team at GlobalTrade!',
 NOW() - INTERVAL '8 months'),

-- Cancelled invitation (example)
('88888888-8888-8888-8888-888888888813',
 '22222222-2222-2222-2222-222222222202',
 'cancelled.user@globaltrade.com',
 'Cancelled',
 'User',
 '44444444-4444-4444-4444-444444444416', -- Sales Rep role
 '["66666666-6666-6666-6666-666666666614"]', -- Sales team
 '33333333-3333-3333-3333-333333333312', -- Invited by Amanda (Admin)
 '$2b$12$cancelledinvitationtokenhashexamplexxxxxxxxxxxxxxx', -- Token hash
 'cancelled',
 NOW() + INTERVAL '5 days',
 'Welcome to GlobalTrade.',
 NOW() - INTERVAL '5 days');


-- =====================================================
-- 10. ORGANIZATION_SETTINGS - Organization preferences
-- =====================================================

INSERT INTO organization_settings (id, organization_id, timezone, date_format, time_format, currency, language, 
    features, notifications, security, created_at, updated_at) VALUES

-- TechCorp Settings
('99999999-9999-9999-9999-999999999901',
 '22222222-2222-2222-2222-222222222201',
 'America/Los_Angeles',
 'MM/DD/YYYY',
 '12h',
 'USD',
 'en',
 '{"crm": true, "support": true, "billing": true, "inventory": false}',
 '{"email_notifications": true, "slack_integration": false, "webhook_enabled": false}',
 '{"mfa_required": true, "password_expiry_days": 90, "session_timeout_minutes": 60}',
 NOW() - INTERVAL '2 years',
 NOW()),

-- GlobalTrade Settings
('99999999-9999-9999-9999-999999999902',
 '22222222-2222-2222-2222-222222222202',
 'America/Chicago',
 'MM/DD/YYYY',
 '12h',
 'USD',
 'en',
 '{"crm": true, "support": false, "billing": true, "inventory": true}',
 '{"email_notifications": true, "slack_integration": true, "webhook_enabled": true}',
 '{"mfa_required": false, "password_expiry_days": 180, "session_timeout_minutes": 120}',
 NOW() - INTERVAL '3 years',
 NOW());

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================
-- Run these to verify the seed data

-- Count records by table
SELECT 
    'permissions' as table_name, COUNT(*) as count FROM permissions
UNION ALL
SELECT 'organizations', COUNT(*) FROM organizations
UNION ALL
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'roles', COUNT(*) FROM roles
UNION ALL
SELECT 'role_permissions', COUNT(*) FROM role_permissions
UNION ALL
SELECT 'user_organization_roles', COUNT(*) FROM user_organization_roles
UNION ALL
SELECT 'teams', COUNT(*) FROM teams
UNION ALL
SELECT 'team_members', COUNT(*) FROM team_members
UNION ALL
SELECT 'invitations', COUNT(*) FROM invitations
UNION ALL
SELECT 'organization_settings', COUNT(*) FROM organization_settings;

-- =====================================================
-- END OF SEED DATA SCRIPT
-- =====================================================
