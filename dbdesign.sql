/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
ORGANIZATIONS
////////////////////////////////////////////////////////////

Table organizations {
  id uuid [pk]
  name varchar
  address text
  created_at datetime
  updated_at datetime
}

/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
USERS & AUTH
////////////////////////////////////////////////////////////

Table users {
  id uuid [pk]
  organization_id uuid [not null, ref: > organizations.id]
  email varchar
  password_hash varchar
  user_type varchar
  status varchar
  is_active boolean
  created_at datetime
  updated_at datetime
}

Table roles {
  id uuid [pk]
  organization_id uuid [not null, ref: > organizations.id]
  name varchar
  code varchar
  is_active boolean
}

Table permissions {
  id uuid [pk]
  code varchar
  name varchar
  description text
}

Table role_permissions {
  id uuid [pk]
  role_id uuid [not null, ref: > roles.id]
  permission_id uuid [not null, ref: > permissions.id]
}

Table user_roles {
  id uuid [pk]
  user_id uuid [not null, ref: > users.id]
  role_id uuid [not null, ref: > roles.id]
}

/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
TEAMS
////////////////////////////////////////////////////////////

Table teams {
  id uuid [pk]
  organization_id uuid [not null, ref: > organizations.id]
  name varchar
  team_type varchar
  parent_id uuid [ref: - teams.id]
}

Table user_teams {
  id uuid [pk]
  user_id uuid [not null, ref: > users.id]
  team_id uuid [not null, ref: > teams.id]
  team_role varchar
}

/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
BILLING & SUBSCRIPTIONS
////////////////////////////////////////////////////////////

Table subscription_plans {
  id uuid [pk]
  name varchar
  price numeric
  billing_cycle varchar
  description text
  is_active boolean
}

Table subscriptions {
  id uuid [pk]
  organization_id uuid [not null, ref: > organizations.id]
  plan_id uuid [not null, ref: > subscription_plans.id]
  stripe_subscription_id varchar
  stripe_customer_id varchar
  status varchar
  start_date datetime
  end_date datetime
  auto_renew boolean
}

Table subscription_invoices {
  id uuid [pk]
  subscription_id uuid [not null, ref: > subscriptions.id]
  stripe_invoice_id varchar
  invoice_number varchar
  amount numeric
  status varchar
  billing_period_start datetime
  billing_period_end datetime
}

Table subscription_payments {
  id uuid [pk]
  invoice_id uuid [not null, ref: > subscription_invoices.id]
  stripe_payment_intent_id varchar
  amount numeric
  paid_at datetime
  status varchar
}

/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
ACTIVITY & AUDIT LOGS
////////////////////////////////////////////////////////////

Table activity_logs {
  id uuid [pk]
  organization_id uuid [not null, ref: > organizations.id]
  user_id uuid [not null, ref: > users.id]
  team_id uuid [ref: > teams.id]
  entity_type varchar
  entity_id uuid
  related_entity_type varchar
  related_entity_id uuid
  action varchar
  old_values text
  new_values text
  timestamp datetime
}

Table audit_logs {
  id uuid [pk]
  organization_id uuid [not null, ref: > organizations.id]
  user_id uuid [not null, ref: > users.id]
  operation varchar
  entity varchar
  entity_id uuid
  previous_data text
  new_data text
  timestamp datetime
}

/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
CRM MODULE
////////////////////////////////////////////////////////////

Table leads {
  id uuid [pk]
  organization_id uuid [not null, ref: > organizations.id]
  assigned_user_id uuid [ref: > users.id]
  name varchar
  email varchar
  phone varchar
  lead_source varchar
  status varchar
  created_at datetime
}

Table accounts {
  id uuid [pk]
  organization_id uuid [not null, ref: > organizations.id]
  name varchar
  industry varchar
  created_at datetime
}

Table contacts {
  id uuid [pk]
  account_id uuid [not null, ref: > accounts.id]
  organization_id uuid [not null, ref: > organizations.id]
  name varchar
  email varchar
  phone varchar
}

Table deals {
  id uuid [pk]
  organization_id uuid [not null, ref: > organizations.id]
  account_id uuid [not null, ref: > accounts.id]
  contact_id uuid [ref: > contacts.id]
  amount numeric
  status varchar
  created_at datetime
}

Table tickets {
  id uuid [pk]
  organization_id uuid [not null, ref: > organizations.id]
  user_id uuid [ref: > users.id]
  subject varchar
  description text
  status varchar
  priority varchar
  created_at datetime
}

/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
INVENTORY SYSTEM
////////////////////////////////////////////////////////////

Table item_groups {
  id uuid [pk]
  organization_id uuid [not null, ref: > organizations.id]
  name varchar
  parent_id uuid [ref: - item_groups.id]
}

Table items {
  id uuid [pk]
  organization_id uuid [not null, ref: > organizations.id]
  item_group_id uuid [not null, ref: > item_groups.id]
  item_name varchar
  sku varchar
  description text
  unit_of_measure varchar
  is_active boolean
}

Table warehouses {
  id uuid [pk]
  organization_id uuid [not null, ref: > organizations.id]
  name varchar
  location text
}

Table batches {
  id uuid [pk]
  organization_id uuid [not null, ref: > organizations.id]
  item_id uuid [not null, ref: > items.id]
  batch_no varchar
  expiry_date datetime
}

Table stock_ledger_entries {
  id uuid [pk]
  organization_id uuid [not null, ref: > organizations.id]
  item_id uuid [not null, ref: > items.id]
  warehouse_id uuid [not null, ref: > warehouses.id]
  batch_id uuid [ref: > batches.id]
  voucher_type varchar
  voucher_id uuid
  qty numeric
  valuation_rate numeric
  created_at datetime
}

/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
SALES & PURCHASE DOCUMENTS
////////////////////////////////////////////////////////////

Table sales_orders {
  id uuid [pk]
  organization_id uuid [not null, ref: > organizations.id]
  customer_id uuid [not null, ref: > accounts.id]
  status varchar
  created_at datetime
}

Table purchase_orders {
  id uuid [pk]
  organization_id uuid [not null, ref: > organizations.id]
  supplier_name varchar
  status varchar
  created_at datetime
}

Table purchase_receipts {
  id uuid [pk]
  purchase_order_id uuid [not null, ref: > purchase_orders.id]
  organization_id uuid [not null, ref: > organizations.id]
  receipt_date datetime
}

Table delivery_notes {
  id uuid [pk]
  sales_order_id uuid [not null, ref: > sales_orders.id]
  organization_id uuid [not null, ref: > organizations.id]
  delivery_date datetime
}

Table delivery_note_items {
  id uuid [pk]
  delivery_note_id uuid [not null, ref: > delivery_notes.id]
  item_id uuid [not null, ref: > items.id]
  qty numeric
}

/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
/
ACCOUNTING (AUTO-POSTING)
////////////////////////////////////////////////////////////

Table chart_of_accounts {
  id uuid [pk]
  organization_id uuid [not null, ref: > organizations.id]
  account_name varchar
  account_type varchar
  parent_id uuid [ref: - chart_of_accounts.id]
}

Table journal_entries {
  id uuid [pk]
  organization_id uuid [not null, ref: > organizations.id]
  entry_date datetime
  reference varchar
}

Table journal_entry_lines {
  id uuid [pk]
  journal_entry_id uuid [not null, ref: > journal_entries.id]
  account_id uuid [not null, ref: > chart_of_accounts.id]
  debit numeric
  credit numeric
}