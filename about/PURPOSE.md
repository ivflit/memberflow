# MemberFlow — Product Purpose

## What is MemberFlow?

MemberFlow is a multi-tenant membership and payments platform built for small clubs and community organisations. It provides each club with its own isolated environment to manage members, membership tiers, subscriptions, and payments — replacing ad-hoc spreadsheets, email chains, and fragmented payment tools with a single, purpose-built SaaS platform.

A single MemberFlow deployment serves any number of clubs simultaneously. Each club operates in full isolation: their members, membership tiers, payments, and configuration are entirely separate from every other club on the platform.

---

## The Problem

Small clubs — cricket clubs, football clubs, martial arts gyms, social organisations — share a common operational challenge: membership management is manual, error-prone, and time-consuming.

The typical setup looks like this:

- Members register via a Google Form or email
- Fees are collected via bank transfer or cash, tracked in a spreadsheet
- Membership expiry is managed manually, with no automated reminders
- Admins have no centralised view of who is current, overdue, or lapsed
- There is no self-service portal for members to update their details or check their status

This creates real costs: missed payments, outdated records, administrative overhead, and a poor experience for members. Off-the-shelf solutions are either too expensive, too generic, or too complex for small organisations to adopt and maintain.

---

## Who is it for?

MemberFlow operates at two levels:

**Platform operators** (the organisation running MemberFlow) can onboard and manage multiple clubs from a single deployment, with full visibility across all tenants.

**Club administrators** — typically a treasurer or secretary — manage their own club's members, tiers, and payments with no visibility into other clubs on the platform.

**Members** interact only with their own club's portal, with no awareness that the platform is shared.

Target clubs include:
- **Sports clubs** (cricket, football, tennis, rowing, martial arts)
- **Community organisations** (social clubs, hobby groups, associations)
- **Small membership-based businesses** with recurring fee structures

---

## Key Features

### Multi-Tenant Architecture
- Each club (tenant) is fully isolated: separate members, tiers, payment records, and configuration
- Tenant resolution via subdomain (`springfield-cc.memberflow.com`)
- Per-tenant configuration and feature flags — each club can have a different feature set enabled
- Platform-level administration separate from club-level administration

### Member Management
- Self-registration and profile management, scoped to each club
- Role-based access: member, staff, org admin, platform admin
- Membership status tracking (active, expired, pending, cancelled)

### Membership Tiers
- Configurable membership categories per club (e.g. Full, Junior, Social, Honorary)
- Per-tier pricing, duration, and renewal rules
- Support for annual, monthly, and one-time fee structures

### Payments via Stripe Connect
- Each club connects its own Stripe account — payments go directly to the club
- Secure payment collection via Stripe Checkout
- Subscription-based recurring billing (monthly/annual)
- One-time payment support for non-recurring memberships
- Automated membership activation on successful payment

### Webhook-Driven State Management
- Membership status automatically updated based on Stripe payment events, per tenant
- Handles subscription renewals, failures, cancellations, and disputes
- No manual intervention required for routine billing cycles

### Per-Tenant Configuration
- Feature flags per club (e.g. self-registration, waitlists, family memberships)
- Branding settings (club name, logo, primary colour) served to the frontend at runtime
- Configurable reminder schedules and approval workflows

### Admin Dashboard
- Club admins manage their own members, tiers, and payments in full isolation
- Platform admins have cross-tenant visibility for support and operations
- Exportable membership data per club

### Notifications
- Automated email notifications for payment confirmation, membership expiry, and renewal reminders
- Background processing via Celery, with all tasks carrying tenant context

---

## Value Proposition

MemberFlow removes administrative burden from club operators and provides members with a professional, self-service experience. As a multi-tenant platform, a single deployment scales to serve dozens of clubs with no additional infrastructure per club.

It is:
- **Focused**: built for clubs, not generic CRM use cases
- **Isolated by design**: each club's data is fully separated at the data model and query layer
- **Configurable**: feature flags and per-tenant settings allow each club to get the experience it needs without code changes
- **Production-ready**: built on proven infrastructure (Django, Stripe Connect, PostgreSQL)
- **API-first**: the backend is fully decoupled, enabling future integrations or mobile apps without rearchitecting

---

## Why it Exists

Most small clubs cannot justify the cost or complexity of platforms like Salesforce, Wild Apricot, or SportsTG. MemberFlow fills the gap: a lightweight, modern, multi-tenant platform that handles the core workflows — registration, payment, and membership lifecycle — for many clubs simultaneously, without unnecessary complexity.

---

## System Capabilities (High Level)

| Capability | Detail |
|---|---|
| Multi-tenancy | Subdomain-based tenant resolution; full data isolation per club |
| Authentication | JWT-based, tenant-scoped, with role separation at platform and org level |
| Member self-service | Registration, profile, payment history — scoped to their club |
| Membership lifecycle | Status transitions driven by Stripe events, per tenant |
| Payments | Stripe Connect — each club receives payments into their own Stripe account |
| Per-tenant config | Feature flags and branding stored in the database; no redeploy required |
| Admin tools | Club-level and platform-level admin with appropriate data isolation |
| Background processing | Celery tasks for emails, reminders, and webhook handling — all tenant-aware |
| API | REST API consumed by Vue.js frontend; all responses are tenant-scoped |
| Deployment | Dockerised, CI/CD pipeline, wildcard subdomain routing on DigitalOcean |
