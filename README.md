# Horizon Sync ERP - Backend

A comprehensive, multi-tenant ERP system built with FastAPI microservices architecture, starting with CRM modules.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         API Gateway (NGINX)                          │
└─────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │           │               │               │           │
   ┌────▼────┐ ┌────▼────┐ ┌───────▼───────┐ ┌────▼────┐ ┌────▼────┐
   │  Auth   │ │  User   │ │ Lead-to-Order │ │ Support │ │Inventory│
   │ Service │ │ Mgmt    │ │   Service     │ │ Ticket  │ │ Service │
   │ :8001   │ │ :8002   │ │    :8003      │ │ :8004   │ │ :8005   │
   └────┬────┘ └────┬────┘ └───────┬───────┘ └────┬────┘ └────┬────┘
        │           │               │               │           │
        └───────────┴───────────────┼───────────────┴───────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
               ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
               │PostgreSQL│    │  Redis  │    │RabbitMQ │
               └──────────┘    └─────────┘    └─────────┘
```

## Features

### User Management
- Multi-tenant architecture (organization isolation)
- Role-Based Access Control (RBAC)
- User onboarding & invitations
- Teams & team hierarchy
- Subscription plans (Free, Basic, Pro, Enterprise)
- Audit logging

### Authentication
- JWT access & refresh tokens
- Token rotation for security
- Password reset flow
- MFA (TOTP) support
- Session management

### CRM - Lead-to-Order
- Leads with scoring & conversion
- Contacts management
- Deals pipeline
- Quotes with line items
- Orders & fulfillment

### Support Tickets
- Ticket creation & assignment
- Priority & categorization
- Comments & resolution workflow
- SLA tracking

### Inventory
- Products & categories
- Multi-warehouse support
- Stock levels & movements
- Inventory adjustments

### Billing & Accounting
- Customer & Supplier management
- Invoicing & Payments
- Chart of Accounts
- Journal Entries & General Ledger

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Manual Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your settings

# Run migrations
alembic upgrade head

# Seed data
python scripts/seed_permissions.py
python scripts/seed_subscription_plans.py

# Start services
uvicorn services.auth.main:app --port 8001
uvicorn services.user_management.main:app --port 8002
uvicorn services.lead_to_order.main:app --port 8003
uvicorn services.support_ticket.main:app --port 8004
uvicorn services.inventory.main:app --port 8005
uvicorn services.billing.main:app --port 8006
```

## API Endpoints

### Auth Service (port 8001)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/auth/login | User login |
| POST | /api/v1/auth/refresh | Refresh tokens |
| POST | /api/v1/auth/logout | User logout |
| POST | /api/v1/auth/forgot-password | Request password reset |
| POST | /api/v1/auth/reset-password | Reset password |
| POST | /api/v1/auth/mfa/enable | Enable MFA |
| POST | /api/v1/auth/mfa/verify | Verify MFA setup |

### User Management (port 8002)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/organizations/onboard | Create new organization |
| GET | /api/v1/organizations/{id} | Get organization |
| GET | /api/v1/users/me | Current user profile |
| POST | /api/v1/users/invite | Invite user |
| GET | /api/v1/roles | List roles |
| POST | /api/v1/teams | Create team |
| GET | /api/v1/subscriptions/plans | List plans |

### Lead-to-Order (port 8003)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | /api/v1/leads | List/Create leads |
| POST | /api/v1/leads/{id}/convert | Convert lead |
| GET/POST | /api/v1/contacts | List/Create contacts |
| GET/POST | /api/v1/deals | List/Create deals |
| GET/POST | /api/v1/quotes | List/Create quotes |
| GET/POST | /api/v1/orders | List/Create orders |

### Support Tickets (port 8004)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | /api/v1/tickets | List/Create tickets |
| PATCH | /api/v1/tickets/{id} | Update ticket |
| POST | /api/v1/tickets/{id}/comments | Add comment |

### Inventory (port 8005)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | /api/v1/products | List/Create products |
| GET/POST | /api/v1/warehouses | List/Create warehouses |
| POST | /api/v1/inventory/adjust | Adjust stock |

### Billing & Accounting (port 8006)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | /api/v1/customers | List/Create customers |
| GET/POST | /api/v1/invoices | List/Create invoices |
| GET/POST | /api/v1/payments | List/Create payments |
| GET/POST | /api/v1/accounting/accounts | Chart of accounts |
| POST | /api/v1/accounting/journal | Create journal entry |

## Project Structure

```
horizon-sync-be/
├── shared/                 # Shared library
│   ├── config.py          # Settings
│   ├── database/          # DB session, multi-tenant
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── security/          # JWT, password, RBAC
│   ├── middleware/        # Auth, tenant, audit
│   └── utils/             # Helpers, exceptions
├── services/
│   ├── auth/              # Authentication service
│   ├── user_management/   # Users, orgs, roles, teams
│   ├── lead_to_order/     # CRM: leads, deals, quotes
│   ├── support_ticket/    # Support tickets
│   └── inventory/         # Products, stock, warehouses
├── migrations/            # Alembic migrations
├── scripts/               # Seed scripts
├── docker-compose.yml
└── requirements.txt
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection | postgresql+asyncpg://... |
| REDIS_URL | Redis connection | redis://... |
| JWT_SECRET_KEY | JWT signing key | (required) |
| JWT_ALGORITHM | JWT algorithm | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token TTL | 30 |
| REFRESH_TOKEN_EXPIRE_DAYS | Refresh TTL | 7 |

## Security

- All endpoints require JWT authentication (except login, signup)
- Multi-tenant isolation via organization_id
- RBAC with fine-grained permissions
- Password hashing with bcrypt
- Rate limiting via NGINX
- Audit logging for compliance

## License

Proprietary - ChiperCode
