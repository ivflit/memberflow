"""E2E-style backend tests for the Events API."""
import pytest
from django.utils import timezone
from datetime import timedelta
from apps.organizations.models import Organization, OrganizationConfig
from apps.users.models import User, UserOrganizationRole
from apps.users.tokens import make_tokens_for_user
from apps.events.models import Event, EventCategory
from apps.memberships.models import MembershipTier, Membership


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def org_a(db):
    org = Organization.objects.create(name='Events Club A', slug='events-club-a')
    OrganizationConfig.objects.create(organization=org)
    return org


@pytest.fixture
def org_b(db):
    org = Organization.objects.create(name='Events Club B', slug='events-club-b')
    OrganizationConfig.objects.create(organization=org)
    return org


def make_user(org, email, role='member'):
    u = User(organization=org, email=email, first_name='Test', last_name='User')
    u.set_password('TestPass123!')
    u.save()
    UserOrganizationRole.objects.create(user=u, organization=org, role=role)
    return u


def auth_header(user):
    access, _ = make_tokens_for_user(user)
    return {'HTTP_AUTHORIZATION': f'Bearer {access}'}


def make_event(org, title='Test Event', status='published', start_offset_days=1,
               category=None):
    return Event.objects.create(
        organization=org,
        title=title,
        start_datetime=timezone.now() + timedelta(days=start_offset_days),
        status=status,
        category=category,
    )


def make_category(org, name='Match Day', colour='#3273dc'):
    return EventCategory.objects.create(organization=org, name=name, colour=colour)


def make_tier(org, name='Full Member'):
    return MembershipTier.objects.create(organization=org, name=name)


def make_membership(org, user, tier, status='active'):
    return Membership.objects.create(
        organization=org, user=user, tier=tier, status=status
    )


# ── Public list tests ─────────────────────────────────────────────────────────

class TestPublicEventList:

    def test_published_returned(self, client, org_a):
        make_event(org_a, 'Published Event', 'published')
        response = client.get('/api/v1/events/', HTTP_HOST='events-club-a.localhost')
        assert response.status_code == 200
        data = response.json()
        assert data['count'] == 1
        assert data['results'][0]['title'] == 'Published Event'

    def test_draft_excluded(self, client, org_a):
        make_event(org_a, 'Draft Event', 'draft')
        response = client.get('/api/v1/events/', HTTP_HOST='events-club-a.localhost')
        assert response.status_code == 200
        assert response.json()['count'] == 0

    def test_cancelled_included_with_status(self, client, org_a):
        make_event(org_a, 'Cancelled Event', 'cancelled')
        response = client.get('/api/v1/events/', HTTP_HOST='events-club-a.localhost')
        assert response.status_code == 200
        data = response.json()
        assert data['count'] == 1
        assert data['results'][0]['status'] == 'cancelled'

    def test_archived_excluded(self, client, org_a):
        make_event(org_a, 'Archived Event', 'archived')
        response = client.get('/api/v1/events/', HTTP_HOST='events-club-a.localhost')
        assert response.status_code == 200
        assert response.json()['count'] == 0

    def test_search_filters_by_title(self, client, org_a):
        make_event(org_a, 'Summer BBQ', 'published')
        make_event(org_a, 'AGM', 'published')
        response = client.get(
            '/api/v1/events/?search=bbq',
            HTTP_HOST='events-club-a.localhost',
        )
        assert response.status_code == 200
        data = response.json()
        assert data['count'] == 1
        assert data['results'][0]['title'] == 'Summer BBQ'

    def test_category_filter(self, client, org_a):
        cat = make_category(org_a, 'Match Day')
        make_event(org_a, 'Match Day Event', 'published', category=cat)
        make_event(org_a, 'Social Event', 'published')
        response = client.get(
            f'/api/v1/events/?category={cat.id}',
            HTTP_HOST='events-club-a.localhost',
        )
        assert response.status_code == 200
        data = response.json()
        assert data['count'] == 1
        assert data['results'][0]['title'] == 'Match Day Event'

    def test_date_from_filter(self, client, org_a):
        future = timezone.now() + timedelta(days=10)
        past_event = Event.objects.create(
            organization=org_a, title='Past Event',
            start_datetime=timezone.now() - timedelta(days=5),
            status='published',
        )
        make_event(org_a, 'Future Event', 'published', start_offset_days=10)
        date_from = future.date().isoformat()
        response = client.get(
            f'/api/v1/events/?date_from={date_from}',
            HTTP_HOST='events-club-a.localhost',
        )
        assert response.status_code == 200
        titles = [e['title'] for e in response.json()['results']]
        assert 'Future Event' in titles
        assert 'Past Event' not in titles

    def test_paginated_response_shape(self, client, org_a):
        response = client.get('/api/v1/events/', HTTP_HOST='events-club-a.localhost')
        assert response.status_code == 200
        data = response.json()
        assert 'count' in data
        assert 'next' in data
        assert 'previous' in data
        assert 'results' in data

    def test_tenant_isolation(self, client, org_a, org_b):
        make_event(org_b, 'Org B Event', 'published')
        response = client.get('/api/v1/events/', HTTP_HOST='events-club-a.localhost')
        assert response.status_code == 200
        titles = [e['title'] for e in response.json()['results']]
        assert 'Org B Event' not in titles


# ── Public detail tests ───────────────────────────────────────────────────────

class TestPublicEventDetail:

    def test_published_returns_200(self, client, org_a):
        event = make_event(org_a, 'Public Event', 'published')
        response = client.get(
            f'/api/v1/events/{event.id}/',
            HTTP_HOST='events-club-a.localhost',
        )
        assert response.status_code == 200
        assert response.json()['title'] == 'Public Event'

    def test_draft_returns_404(self, client, org_a):
        event = make_event(org_a, 'Draft Event', 'draft')
        response = client.get(
            f'/api/v1/events/{event.id}/',
            HTTP_HOST='events-club-a.localhost',
        )
        assert response.status_code == 404

    def test_archived_returns_404(self, client, org_a):
        event = make_event(org_a, 'Archived Event', 'archived')
        response = client.get(
            f'/api/v1/events/{event.id}/',
            HTTP_HOST='events-club-a.localhost',
        )
        assert response.status_code == 404

    def test_cross_tenant_detail_returns_404(self, client, org_a, org_b):
        event_b = make_event(org_b, 'Org B Event', 'published')
        response = client.get(
            f'/api/v1/events/{event_b.id}/',
            HTTP_HOST='events-club-a.localhost',
        )
        assert response.status_code == 404


# ── Agenda tests ──────────────────────────────────────────────────────────────

class TestEventAgenda:

    def test_agenda_requires_auth(self, client, org_a):
        response = client.get('/api/v1/events/agenda/', HTTP_HOST='events-club-a.localhost')
        assert response.status_code == 401

    def test_agenda_returns_upcoming_published_eligible_events(self, client, org_a):
        user = make_user(org_a, 'member@agenda.com', 'member')
        make_event(org_a, 'Future Event', 'published', start_offset_days=2)
        response = client.get(
            '/api/v1/events/agenda/',
            HTTP_HOST='events-club-a.localhost',
            **auth_header(user),
        )
        assert response.status_code == 200
        data = response.json()
        assert 'results' in data
        assert len(data['results']) == 1

    def test_agenda_excludes_draft_events(self, client, org_a):
        user = make_user(org_a, 'member2@agenda.com', 'member')
        make_event(org_a, 'Draft Event', 'draft', start_offset_days=2)
        response = client.get(
            '/api/v1/events/agenda/',
            HTTP_HOST='events-club-a.localhost',
            **auth_header(user),
        )
        assert response.status_code == 200
        assert response.json()['count'] == 0

    def test_agenda_excludes_ineligible_events(self, client, org_a):
        user = make_user(org_a, 'member3@agenda.com', 'member')
        tier = make_tier(org_a)
        event = make_event(org_a, 'Restricted Event', 'published', start_offset_days=2)
        event.restricted_to_tiers.add(tier)
        # user has no membership — ineligible
        response = client.get(
            '/api/v1/events/agenda/',
            HTTP_HOST='events-club-a.localhost',
            **auth_header(user),
        )
        assert response.status_code == 200
        assert response.json()['count'] == 0

    def test_agenda_includes_eligible_restricted_events(self, client, org_a):
        user = make_user(org_a, 'member4@agenda.com', 'member')
        tier = make_tier(org_a)
        make_membership(org_a, user, tier, 'active')
        event = make_event(org_a, 'Eligible Restricted Event', 'published', start_offset_days=2)
        event.restricted_to_tiers.add(tier)
        response = client.get(
            '/api/v1/events/agenda/',
            HTTP_HOST='events-club-a.localhost',
            **auth_header(user),
        )
        assert response.status_code == 200
        assert response.json()['count'] == 1

    def test_agenda_max_5_events(self, client, org_a):
        user = make_user(org_a, 'member5@agenda.com', 'member')
        for i in range(7):
            make_event(org_a, f'Event {i}', 'published', start_offset_days=i + 1)
        response = client.get(
            '/api/v1/events/agenda/',
            HTTP_HOST='events-club-a.localhost',
            **auth_header(user),
        )
        assert response.status_code == 200
        assert len(response.json()['results']) == 5


# ── Admin category tests ──────────────────────────────────────────────────────

class TestAdminEventCategories:

    def test_create_category(self, client, org_a):
        admin = make_user(org_a, 'admin@cat.com', 'org_admin')
        response = client.post(
            '/api/v1/admin/events/categories/',
            data='{"name": "Match Day", "colour": "#3273dc"}',
            content_type='application/json',
            HTTP_HOST='events-club-a.localhost',
            **auth_header(admin),
        )
        assert response.status_code == 201
        data = response.json()
        assert data['name'] == 'Match Day'
        assert data['colour'] == '#3273dc'

    def test_duplicate_category_name_rejected(self, client, org_a):
        admin = make_user(org_a, 'admin2@cat.com', 'org_admin')
        make_category(org_a, 'Match Day')
        response = client.post(
            '/api/v1/admin/events/categories/',
            data='{"name": "Match Day"}',
            content_type='application/json',
            HTTP_HOST='events-club-a.localhost',
            **auth_header(admin),
        )
        assert response.status_code == 400

    def test_delete_category(self, client, org_a):
        admin = make_user(org_a, 'admin3@cat.com', 'org_admin')
        cat = make_category(org_a, 'Deletable')
        response = client.delete(
            f'/api/v1/admin/events/categories/{cat.id}/',
            HTTP_HOST='events-club-a.localhost',
            **auth_header(admin),
        )
        assert response.status_code == 204

    def test_delete_category_with_events_returns_409(self, client, org_a):
        admin = make_user(org_a, 'admin4@cat.com', 'org_admin')
        cat = make_category(org_a, 'HasEvents')
        make_event(org_a, 'Event With Cat', 'published', category=cat)
        response = client.delete(
            f'/api/v1/admin/events/categories/{cat.id}/',
            HTTP_HOST='events-club-a.localhost',
            **auth_header(admin),
        )
        assert response.status_code == 409

    def test_staff_can_list_categories(self, client, org_a):
        staff = make_user(org_a, 'staff@cat.com', 'org_staff')
        response = client.get(
            '/api/v1/admin/events/categories/',
            HTTP_HOST='events-club-a.localhost',
            **auth_header(staff),
        )
        assert response.status_code == 200

    def test_member_cannot_access_admin_categories(self, client, org_a):
        member = make_user(org_a, 'member@cat.com', 'member')
        response = client.get(
            '/api/v1/admin/events/categories/',
            HTTP_HOST='events-club-a.localhost',
            **auth_header(member),
        )
        assert response.status_code == 403


# ── Admin event CRUD tests ────────────────────────────────────────────────────

class TestAdminEventCRUD:

    def test_create_draft_event(self, client, org_a):
        admin = make_user(org_a, 'admin@evt.com', 'org_admin')
        payload = '{"title": "Draft Event", "start_datetime": "2030-06-01T10:00:00Z", "status": "draft"}'
        response = client.post(
            '/api/v1/admin/events/',
            data=payload,
            content_type='application/json',
            HTTP_HOST='events-club-a.localhost',
            **auth_header(admin),
        )
        assert response.status_code == 201
        assert response.json()['status'] == 'draft'

    def test_draft_not_visible_in_public_list(self, client, org_a):
        admin = make_user(org_a, 'admin2@evt.com', 'org_admin')
        payload = '{"title": "Hidden Draft", "start_datetime": "2030-06-01T10:00:00Z", "status": "draft"}'
        client.post(
            '/api/v1/admin/events/',
            data=payload,
            content_type='application/json',
            HTTP_HOST='events-club-a.localhost',
            **auth_header(admin),
        )
        response = client.get('/api/v1/events/', HTTP_HOST='events-club-a.localhost')
        titles = [e['title'] for e in response.json()['results']]
        assert 'Hidden Draft' not in titles

    def test_publish_event_makes_it_public(self, client, org_a):
        admin = make_user(org_a, 'admin3@evt.com', 'org_admin')
        event = Event.objects.create(
            organization=org_a,
            title='To Publish',
            start_datetime=timezone.now() + timedelta(days=1),
            status='draft',
        )
        response = client.patch(
            f'/api/v1/admin/events/{event.id}/',
            data='{"status": "published"}',
            content_type='application/json',
            HTTP_HOST='events-club-a.localhost',
            **auth_header(admin),
        )
        assert response.status_code == 200
        assert response.json()['status'] == 'published'
        # Verify public list now includes it
        pub_response = client.get('/api/v1/events/', HTTP_HOST='events-club-a.localhost')
        titles = [e['title'] for e in pub_response.json()['results']]
        assert 'To Publish' in titles

    def test_cancel_event_keeps_it_public(self, client, org_a):
        admin = make_user(org_a, 'admin4@evt.com', 'org_admin')
        event = make_event(org_a, 'To Cancel', 'published')
        response = client.patch(
            f'/api/v1/admin/events/{event.id}/',
            data='{"status": "cancelled"}',
            content_type='application/json',
            HTTP_HOST='events-club-a.localhost',
            **auth_header(admin),
        )
        assert response.status_code == 200
        pub_response = client.get('/api/v1/events/', HTTP_HOST='events-club-a.localhost')
        result = next(
            (e for e in pub_response.json()['results'] if e['title'] == 'To Cancel'), None
        )
        assert result is not None
        assert result['status'] == 'cancelled'

    def test_archive_event_removes_from_public(self, client, org_a):
        admin = make_user(org_a, 'admin5@evt.com', 'org_admin')
        event = make_event(org_a, 'To Archive', 'published')
        client.patch(
            f'/api/v1/admin/events/{event.id}/',
            data='{"status": "archived"}',
            content_type='application/json',
            HTTP_HOST='events-club-a.localhost',
            **auth_header(admin),
        )
        response = client.get(
            f'/api/v1/events/{event.id}/',
            HTTP_HOST='events-club-a.localhost',
        )
        assert response.status_code == 404

    def test_delete_draft_event(self, client, org_a):
        admin = make_user(org_a, 'admin6@evt.com', 'org_admin')
        event = make_event(org_a, 'Delete Me', 'draft')
        response = client.delete(
            f'/api/v1/admin/events/{event.id}/',
            HTTP_HOST='events-club-a.localhost',
            **auth_header(admin),
        )
        assert response.status_code == 204

    def test_delete_published_event_returns_409(self, client, org_a):
        admin = make_user(org_a, 'admin7@evt.com', 'org_admin')
        event = make_event(org_a, 'Published Event', 'published')
        response = client.delete(
            f'/api/v1/admin/events/{event.id}/',
            HTTP_HOST='events-club-a.localhost',
            **auth_header(admin),
        )
        assert response.status_code == 409

    def test_end_datetime_before_start_returns_400(self, client, org_a):
        admin = make_user(org_a, 'admin8@evt.com', 'org_admin')
        payload = (
            '{"title": "Bad Dates", '
            '"start_datetime": "2030-06-01T12:00:00Z", '
            '"end_datetime": "2030-06-01T10:00:00Z"}'
        )
        response = client.post(
            '/api/v1/admin/events/',
            data=payload,
            content_type='application/json',
            HTTP_HOST='events-club-a.localhost',
            **auth_header(admin),
        )
        assert response.status_code == 400

    def test_member_cannot_access_admin_events(self, client, org_a):
        member = make_user(org_a, 'member@evt.com', 'member')
        response = client.get(
            '/api/v1/admin/events/',
            HTTP_HOST='events-club-a.localhost',
            **auth_header(member),
        )
        assert response.status_code == 403


# ── Admin permissions tests ───────────────────────────────────────────────────

class TestAdminPermissions:

    def test_staff_can_list_events(self, client, org_a):
        staff = make_user(org_a, 'staff@perm.com', 'org_staff')
        response = client.get(
            '/api/v1/admin/events/',
            HTTP_HOST='events-club-a.localhost',
            **auth_header(staff),
        )
        assert response.status_code == 200

    def test_staff_cannot_create_event(self, client, org_a):
        staff = make_user(org_a, 'staff2@perm.com', 'org_staff')
        payload = '{"title": "Staff Create", "start_datetime": "2030-06-01T10:00:00Z"}'
        response = client.post(
            '/api/v1/admin/events/',
            data=payload,
            content_type='application/json',
            HTTP_HOST='events-club-a.localhost',
            **auth_header(staff),
        )
        assert response.status_code == 403


# ── Tenant isolation tests ────────────────────────────────────────────────────

class TestTenantIsolation:

    def test_org_a_admin_cannot_get_org_b_event(self, client, org_a, org_b):
        admin_a = make_user(org_a, 'admin@iso.com', 'org_admin')
        event_b = make_event(org_b, 'Org B Event', 'draft')
        response = client.get(
            f'/api/v1/admin/events/{event_b.id}/',
            HTTP_HOST='events-club-a.localhost',
            **auth_header(admin_a),
        )
        assert response.status_code == 404

    def test_org_a_admin_cannot_patch_org_b_event(self, client, org_a, org_b):
        admin_a = make_user(org_a, 'admin2@iso.com', 'org_admin')
        event_b = make_event(org_b, 'Org B Event', 'draft')
        response = client.patch(
            f'/api/v1/admin/events/{event_b.id}/',
            data='{"title": "Hacked"}',
            content_type='application/json',
            HTTP_HOST='events-club-a.localhost',
            **auth_header(admin_a),
        )
        assert response.status_code == 404

    def test_org_a_admin_cannot_delete_org_b_event(self, client, org_a, org_b):
        admin_a = make_user(org_a, 'admin3@iso.com', 'org_admin')
        event_b = make_event(org_b, 'Org B Event', 'draft')
        response = client.delete(
            f'/api/v1/admin/events/{event_b.id}/',
            HTTP_HOST='events-club-a.localhost',
            **auth_header(admin_a),
        )
        assert response.status_code == 404

    def test_public_list_does_not_include_other_org_events(self, client, org_a, org_b):
        make_event(org_b, 'Org B Public Event', 'published')
        response = client.get('/api/v1/events/', HTTP_HOST='events-club-a.localhost')
        titles = [e['title'] for e in response.json()['results']]
        assert 'Org B Public Event' not in titles

    def test_org_a_admin_cannot_assign_org_b_category(self, client, org_a, org_b):
        admin_a = make_user(org_a, 'admin4@iso.com', 'org_admin')
        cat_b = make_category(org_b, 'Org B Category')
        payload = (
            f'{{"title": "Cross Org Event", '
            f'"start_datetime": "2030-06-01T10:00:00Z", '
            f'"category_id": {cat_b.id}}}'
        )
        response = client.post(
            '/api/v1/admin/events/',
            data=payload,
            content_type='application/json',
            HTTP_HOST='events-club-a.localhost',
            **auth_header(admin_a),
        )
        assert response.status_code == 400

    def test_org_a_admin_cannot_assign_org_b_tier(self, client, org_a, org_b):
        admin_a = make_user(org_a, 'admin5@iso.com', 'org_admin')
        tier_b = make_tier(org_b, 'Org B Tier')
        payload = (
            f'{{"title": "Cross Org Tier Event", '
            f'"start_datetime": "2030-06-01T10:00:00Z", '
            f'"restricted_to_tiers": [{tier_b.id}]}}'
        )
        response = client.post(
            '/api/v1/admin/events/',
            data=payload,
            content_type='application/json',
            HTTP_HOST='events-club-a.localhost',
            **auth_header(admin_a),
        )
        assert response.status_code == 400


# ── Eligibility integration tests ─────────────────────────────────────────────

class TestEligibilityIntegration:

    def test_unrestricted_event_is_eligible_for_all(self, client, org_a):
        make_event(org_a, 'Open Event', 'published')
        response = client.get('/api/v1/events/', HTTP_HOST='events-club-a.localhost')
        assert response.status_code == 200
        result = response.json()['results'][0]
        assert result['is_restricted'] is False
        assert result['is_eligible'] is True

    def test_restricted_event_ineligible_for_unauthenticated(self, client, org_a):
        tier = make_tier(org_a, 'Full Member Tier')
        event = make_event(org_a, 'Members Only', 'published')
        event.restricted_to_tiers.add(tier)
        response = client.get('/api/v1/events/', HTTP_HOST='events-club-a.localhost')
        result = response.json()['results'][0]
        assert result['is_restricted'] is True
        assert result['is_eligible'] is False

    def test_tier_restricted_eligible_member(self, client, org_a):
        user = make_user(org_a, 'eligible@elig.com', 'member')
        tier = make_tier(org_a, 'Gold Tier')
        make_membership(org_a, user, tier, 'active')
        event = make_event(org_a, 'Gold Members Event', 'published')
        event.restricted_to_tiers.add(tier)
        response = client.get(
            '/api/v1/events/',
            HTTP_HOST='events-club-a.localhost',
            **auth_header(user),
        )
        result = next(
            e for e in response.json()['results'] if e['title'] == 'Gold Members Event'
        )
        assert result['is_eligible'] is True

    def test_inactive_membership_does_not_grant_eligibility(self, client, org_a):
        user = make_user(org_a, 'inactive@elig.com', 'member')
        tier = make_tier(org_a, 'Silver Tier')
        make_membership(org_a, user, tier, 'inactive')
        event = make_event(org_a, 'Silver Members Event', 'published')
        event.restricted_to_tiers.add(tier)
        response = client.get(
            '/api/v1/events/',
            HTTP_HOST='events-club-a.localhost',
            **auth_header(user),
        )
        result = next(
            e for e in response.json()['results'] if e['title'] == 'Silver Members Event'
        )
        assert result['is_eligible'] is False
