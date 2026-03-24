# MemberFlow — Architecture

## 1. High-Level Architecture

MemberFlow is a decoupled, API-first system. The backend exposes a REST API consumed by a Vue.js single-page application. Stripe handles all payment processing externally, communicating back via webhooks. Background tasks are offloaded to Celery workers backed by Redis.

```
┌─────────────────────────────────────────────────────────────────┐
│                          Client Browser                         │
│                      Vue.js SPA (static)                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTPS / REST API (JWT)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Django REST API                          │
│              (Gunicorn + Nginx, DigitalOcean Droplet)           │
│                                                                 │
│   ┌────────────┐  ┌─────────────┐  ┌──────────┐  ┌─────────┐  │
│   │   users    │  │ memberships │  │ payments │  │  admin  │  │
│   └────────────┘  └─────────────┘  └──────────┘  └─────────┘  │
└──────────────┬─────────────────────────────┬────────────────────┘
               │                             │
        ┌──────▼──────┐              ┌───────▼───────┐
        │  PostgreSQL │              │  Celery Worker│
        │  (primary)  │              │  + Redis      │
        └─────────────┘              └───────┬───────┘
                                             │
                                    ┌────────▼────────┐
                                    │  Stripe API /   │
                                    │  Webhooks       │
                                    └─────────────────┘
```

**Key architectural principles:**
- Frontend and backend are independently deployable
- The backend is stateless at the API layer; all state lives in PostgreSQL
- Stripe is the source of truth for payment status; webhook events drive membership state transitions
- Celery workers are isolated from the API process, preventing background jobs from impacting request latency

---

## 2. Backend Architecture

### Technology Stack

| Layer | Technology |
|---|---|
| Framework | Django 4.x + Django REST Framework |
| Database | PostgreSQL 15 |
| Auth | djangorestframework-simplejwt |
| Payments | Stripe Python SDK |
| Task Queue | Celery 5.x + Redis |
| Web Server | Gunicorn behind Nginx |
| Containerisation | Docker + Docker Compose |

### Django Project Structure

```
memberflow/
├── config/                    # Project-level settings and routing
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── users/                 # Registration, auth, profiles
│   ├── memberships/           # Tiers, membership records, status
│   ├── payments/              # Stripe integration, payment records
│   └── admin_portal/          # Admin-specific views and serializers
├── core/                      # Shared utilities, base models, permissions
├── tasks/                     # Celery task definitions
├── webhooks/                  # Stripe webhook handler
└── manage.py
```

### App Responsibilities

**`users`**
- Custom `User` model extending `AbstractBaseUser`
- Registration, login, and token refresh endpoints
- Profile management (name, contact details, club-specific fields)
- Role assignment: `member`, `staff`, `admin`

**`memberships`**
- `MembershipTier` model: defines categories, pricing, and duration
- `Membership` model: links a user to a tier with status and expiry tracking
- Status enum: `pending`, `active`, `expired`, `cancelled`, `suspended`
- Business logic for status transitions (activated on payment, expired on non-renewal)

**`payments`**
- `Payment` model: records individual payment events (amount, status, Stripe IDs)
- `Subscription` model: tracks recurring Stripe subscriptions per member
- Stripe Checkout session creation
- Stripe webhook signature validation and event routing

**`admin_portal`**
- Admin-only serializers and views with extended member data
- Endpoints for manual membership adjustments
- Aggregated reporting data (active count, revenue summary)

**`webhooks`**
- Dedicated app for receiving and processing Stripe webhook events
- Validates `Stripe-Signature` header on every inbound request
- Routes events to appropriate handlers (payment success, failure, subscription cancelled, etc.)

**`core`**
- Abstract base model with `created_at`, `updated_at`
- Custom permission classes (`IsAdmin`, `IsMember`, `IsOwnerOrAdmin`)
- Shared exception handlers and response formatting

---

## 3. Frontend Architecture

### Technology Stack

| Layer | Technology |
|---|---|
| Framework | Vue.js 3 (Composition API) |
| Routing | Vue Router 4 |
| HTTP Client | Axios |
| State | Pinia (lightweight store) |
| Build Tool | Vite |
| Hosting | DigitalOcean Spaces (static) or Nginx |

### Directory Structure

```
frontend/
├── src/
│   ├── api/                   # Axios service layer (one file per domain)
│   │   ├── auth.js
│   │   ├── memberships.js
│   │   └── payments.js
│   ├── components/            # Reusable UI components
│   │   ├── MemberCard.vue
│   │   ├── StatusBadge.vue
│   │   └── PaymentHistory.vue
│   ├── views/                 # Route-level page components
│   │   ├── LoginView.vue
│   │   ├── DashboardView.vue
│   │   ├── MembershipView.vue
│   │   └── AdminView.vue
│   ├── stores/                # Pinia stores
│   │   ├── auth.js
│   │   └── membership.js
│   ├── router/
│   │   └── index.js
│   └── main.js
├── public/
└── vite.config.js
```

### API Layer

All HTTP communication is encapsulated in `src/api/`. Views and components do not call Axios directly. Each service module exports typed async functions:

```js
// src/api/memberships.js
export const getMembership = () => api.get('/memberships/me/')
export const getMembershipTiers = () => api.get('/memberships/tiers/')
```

A shared `api.js` module configures the Axios instance with the base URL and attaches the JWT access token via a request interceptor. A response interceptor handles 401 errors by attempting a token refresh before retrying.

### Authentication Flow (Frontend)

1. User submits login credentials
2. Backend returns `access` and `refresh` tokens
3. `access` token stored in memory (Pinia store); `refresh` token stored in an `httpOnly`-equivalent session cookie or `localStorage` (tradeoff documented)
4. Axios request interceptor attaches `Authorization: Bearer <access>` header
5. On 401 response, the interceptor calls `/auth/token/refresh/`, updates the stored token, and retries
6. On logout or refresh failure, store is cleared and user redirected to login

### Routing and Guards

Vue Router is configured with navigation guards that check auth state before allowing access to protected routes:

```js
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next('/dashboard')
  } else {
    next()
  }
})
```

---

## 4. Data Model Design

### Core Entities

```
User
├── id (UUID)
├── email (unique)
├── first_name, last_name
├── role (member | staff | admin)
├── is_active
├── created_at

MembershipTier
├── id
├── name (e.g. "Full Member", "Junior")
├── price (Decimal)
├── billing_period (monthly | annual | one_time)
├── stripe_price_id
├── is_active

Membership
├── id
├── user → User (OneToOne)
├── tier → MembershipTier (ForeignKey)
├── status (pending | active | expired | cancelled | suspended)
├── start_date
├── expiry_date
├── stripe_subscription_id (nullable)
├── created_at, updated_at

Subscription
├── id
├── user → User (ForeignKey)
├── stripe_subscription_id (unique)
├── stripe_customer_id
├── status (mirrors Stripe: active | past_due | cancelled | etc.)
├── current_period_start
├── current_period_end
├── created_at, updated_at

Payment
├── id
├── user → User (ForeignKey)
├── membership → Membership (ForeignKey)
├── stripe_payment_intent_id (unique)
├── amount (Decimal)
├── currency
├── status (pending | succeeded | failed | refunded)
├── payment_method_type
├── created_at
```

### Relationships

- A `User` has at most one active `Membership` at any time (OneToOne enforced at application level)
- A `Membership` may be linked to a `Subscription` for recurring billing, or to a one-time `Payment`
- `Payment` records are append-only; each billing cycle creates a new record
- `MembershipTier` is the catalogue; `Membership` is the instance for a specific user

---

## 5. API Design

### Principles

- RESTful resource naming, JSON request/response bodies
- Versioned under `/api/v1/`
- Authentication via JWT Bearer token on all protected endpoints
- Consistent error response shape: `{ "error": "...", "detail": "..." }`
- Pagination on all list endpoints (cursor-based for large datasets)

### Key Endpoints

#### Authentication
```
POST   /api/v1/auth/register/           Register a new user
POST   /api/v1/auth/login/              Obtain JWT access + refresh tokens
POST   /api/v1/auth/token/refresh/      Refresh access token
POST   /api/v1/auth/logout/             Blacklist refresh token
GET    /api/v1/auth/me/                 Current user profile
PATCH  /api/v1/auth/me/                 Update profile
```

#### Memberships
```
GET    /api/v1/memberships/tiers/       List available membership tiers
GET    /api/v1/memberships/me/          Current user's membership
POST   /api/v1/memberships/join/        Initiate membership (select tier)
```

#### Payments
```
POST   /api/v1/payments/checkout/       Create Stripe Checkout session
GET    /api/v1/payments/history/        Current user's payment history
POST   /api/v1/payments/cancel/         Cancel active subscription
```

#### Webhooks
```
POST   /api/v1/webhooks/stripe/         Stripe webhook receiver (no auth)
```

#### Admin (staff/admin role required)
```
GET    /api/v1/admin/members/           List all members (filterable, paginated)
GET    /api/v1/admin/members/{id}/      Member detail with full payment history
PATCH  /api/v1/admin/members/{id}/      Update membership status / tier
GET    /api/v1/admin/stats/             Aggregate stats (active count, revenue)
GET    /api/v1/admin/payments/          Full payment ledger
```

### Permission Model

| Endpoint group | Required role |
|---|---|
| `/auth/*` | Unauthenticated (register/login) or Authenticated (me) |
| `/memberships/*` | Authenticated member |
| `/payments/*` | Authenticated member |
| `/admin/*` | Staff or Admin |
| `/webhooks/stripe/` | None (validated by Stripe signature) |

---

## 6. Payment Flow

### Checkout (One-time or Subscription)

```
1. Member selects a MembershipTier on the frontend
2. Frontend calls POST /api/v1/payments/checkout/ with { tier_id }
3. Backend:
   a. Retrieves or creates a Stripe Customer for the user
   b. Creates a Stripe Checkout Session (mode: subscription or payment)
   c. Sets success_url and cancel_url back to the frontend
   d. Returns { checkout_url } to the frontend
4. Frontend redirects the browser to checkout_url (Stripe-hosted page)
5. Member completes payment on Stripe
6. Stripe redirects back to success_url
7. Frontend shows confirmation screen
```

### Webhook Processing

Stripe sends payment events to `POST /api/v1/webhooks/stripe/`. All events are processed asynchronously via Celery to prevent Stripe's timeout from blocking processing.

```
1. Stripe sends event to webhook endpoint
2. Django validates Stripe-Signature header (rejects if invalid)
3. Raw event is queued as a Celery task immediately
4. Endpoint returns HTTP 200 to Stripe
5. Celery worker processes the event:
   - checkout.session.completed → activate Membership, create Payment record
   - invoice.payment_succeeded → extend expiry, create Payment record
   - invoice.payment_failed → set Membership to suspended, queue failure email
   - customer.subscription.deleted → set Membership to cancelled
```

### Membership State Transitions

```
         ┌──────────┐
         │ pending  │ ← initial state on join
         └────┬─────┘
              │ payment succeeded
              ▼
         ┌──────────┐
    ┌───▶│  active  │◀──────────────────────┐
    │    └────┬─────┘                       │
    │         │ renewal succeeded           │
    │         │                       renewal succeeded
    │    ┌────▼────────┐                    │
    │    │  (renewal   │                    │
    │    │   cycle)    │─────────────────────┘
    │    └────┬────────┘
    │         │ payment failed
    │         ▼
    │    ┌──────────────┐
    │    │  suspended   │ (grace period, retry possible)
    │    └────┬─────────┘
    │         │ manual reinstate or payment recovered
    └──────────┘
              │ subscription cancelled or not recovered
              ▼
         ┌──────────┐
         │cancelled │ (terminal)
         └──────────┘

    expiry_date < today (periodic check)
              ▼
         ┌──────────┐
         │ expired  │ (terminal for non-subscription)
         └──────────┘
```

---

## 7. Async Processing

### Celery Configuration

- **Broker**: Redis (also used as result backend)
- **Workers**: separate Docker container(s), horizontally scalable
- **Queues**: `default`, `webhooks`, `emails` (priority separation)
- **Beat scheduler**: Celery Beat for periodic tasks (runs as a separate process)

### Task Inventory

**Webhook Processing**
```python
@app.task(queue='webhooks', max_retries=5, default_retry_delay=60)
def process_stripe_event(event_id: str): ...
```
Retries with exponential backoff on transient failures. Idempotent — safe to run multiple times for the same event.

**Email Notifications**
```python
@app.task(queue='emails')
def send_payment_confirmation(user_id: int, payment_id: int): ...

@app.task(queue='emails')
def send_membership_expiry_reminder(membership_id: int): ...

@app.task(queue='emails')
def send_payment_failed_notice(user_id: int): ...
```

**Periodic Tasks (Celery Beat)**
```python
# Runs daily at 08:00 UTC
@app.task
def expire_overdue_memberships():
    """
    Finds memberships past their expiry_date with status=active
    and transitions them to expired.
    """

# Runs daily at 09:00 UTC
def send_expiry_reminders():
    """
    Queues reminder emails for memberships expiring in 7 days and 1 day.
    """
```

---

## 8. Deployment Architecture

### Docker Setup

The system is defined as a multi-service Docker Compose stack for both local development and production.

```yaml
services:
  api:          # Django + Gunicorn
  worker:       # Celery worker
  beat:         # Celery Beat scheduler
  nginx:        # Reverse proxy + static file serving
  db:           # PostgreSQL (dev only; managed DB in production)
  redis:        # Redis broker
  frontend:     # Nginx serving built Vue.js static files
```

In production, `db` is replaced by a DigitalOcean Managed PostgreSQL instance, and `redis` by DigitalOcean Managed Redis — both outside the application containers.

### Production Topology (DigitalOcean)

```
                        ┌──────────────────┐
                        │  DigitalOcean    │
                        │  Load Balancer   │
                        └────────┬─────────┘
                                 │
               ┌─────────────────┼─────────────────┐
               ▼                                   ▼
   ┌──────────────────────┐           ┌──────────────────────┐
   │  Droplet: App Server │           │  Droplet: App Server │
   │  (Nginx + Gunicorn)  │           │  (Nginx + Gunicorn)  │
   └──────────┬───────────┘           └──────────┬───────────┘
              │                                  │
              └───────────────┬──────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │  Managed     │  │  Managed     │  │  Spaces CDN  │
    │  PostgreSQL  │  │  Redis       │  │  (Frontend)  │
    └──────────────┘  └──────────────┘  └──────────────┘
```

- **Frontend** built to static files via CI, deployed to DigitalOcean Spaces with CDN enabled
- **API** served via Gunicorn behind Nginx on one or more Droplets
- **Celery workers** run on the same Droplets as the API or on dedicated worker Droplets

### CI/CD Pipeline

Implemented via GitHub Actions:

```
on: push to main

jobs:
  test:
    - Install dependencies
    - Run Django test suite (pytest)
    - Run frontend unit tests (Vitest)
    - Lint (flake8, eslint)

  build:
    - Build Docker image (backend)
    - Build Vue.js static files (frontend)
    - Push Docker image to DigitalOcean Container Registry

  deploy:
    - SSH into Droplet
    - Pull latest image
    - Run database migrations (manage.py migrate)
    - Restart Gunicorn and Celery services
    - Upload built frontend to DigitalOcean Spaces
```

Deployment only runs on a passing test job. Rollback is handled by redeploying the previous tagged Docker image.

---

## 9. Scalability Considerations

### API Layer

- Gunicorn with multiple workers (typically `2 × CPU + 1`) handles concurrent requests
- Stateless API design allows horizontal scaling behind a load balancer with no session affinity required
- Database connection pooling via `pgbouncer` or Django's `CONN_MAX_AGE` setting

### Database

- PostgreSQL indexes on frequently queried fields: `user_id`, `status`, `expiry_date`, `stripe_subscription_id`
- `Membership` and `Payment` tables are the primary hotspots; partitioning by date is an option at high volume
- Read replicas can be introduced for admin reporting queries without touching the write path

### Celery Workers

- Workers are independently scalable; additional worker containers can be deployed to increase task throughput
- Queue separation (`webhooks`, `emails`, `default`) allows targeted scaling — e.g. scaling email workers independently of webhook processors

### Frontend

- Vue.js app is compiled to static assets (HTML, JS, CSS) and served from DigitalOcean Spaces via CDN
- No server-side rendering required; all dynamic data is fetched via API at runtime
- Cache headers are set aggressively on static assets; API responses use `Cache-Control: no-store` where appropriate

### Potential Bottlenecks

| Area | Risk | Mitigation |
|---|---|---|
| Stripe webhook burst | High event volume may overwhelm workers | Celery queue depth monitoring; scale workers |
| Database write contention | Concurrent membership updates | Row-level locking on `Membership`; avoid bulk updates |
| Email delivery | Transactional email throughput | Delegate to dedicated provider (SendGrid, Postmark) |
| Token validation | JWT decode on every request | Lightweight operation; not a bottleneck at this scale |

---

## 10. Security Considerations

### Authentication

- JWT access tokens have a short expiry (15 minutes); refresh tokens are longer-lived (7 days)
- Refresh tokens are rotated on each use (SimpleJWT `ROTATE_REFRESH_TOKENS = True`)
- Used refresh tokens are blacklisted to prevent replay attacks (SimpleJWT token blacklist app)
- Tokens are never logged

### Password Handling

- Passwords are hashed using Django's default PBKDF2-SHA256 with a high iteration count
- Password reset tokens are time-limited and single-use
- Minimum password complexity enforced via Django validators

### Stripe Webhook Validation

- Every inbound webhook request validates the `Stripe-Signature` header using the Stripe SDK
- Requests failing signature validation are rejected with HTTP 400 before any processing occurs
- The webhook signing secret is stored in environment variables, never in source code

### API Protection

- All non-public endpoints require a valid JWT — unauthenticated requests receive HTTP 401
- Role-based permission classes enforce that members cannot access admin endpoints
- Rate limiting applied at the Nginx layer (e.g. 60 req/min per IP) and at the DRF layer for auth endpoints
- `CORS` headers are restricted to the known frontend origin(s) only

### Infrastructure

- All secrets (database credentials, Stripe keys, JWT secret) are stored as environment variables, managed via `.env` files excluded from version control
- HTTPS enforced end-to-end; Nginx configured with TLS 1.2+ only
- DigitalOcean Firewall restricts inbound traffic to ports 80/443 only; database and Redis are accessible only within the private VPC network
- Docker images are scanned for known vulnerabilities as part of the CI pipeline

### Data

- PII is limited to what is necessary (name, email, payment status)
- Stripe handles all card data; MemberFlow never processes or stores raw payment card information
- Audit trail: `Payment` records are append-only; `Membership` status changes are logged with timestamps
