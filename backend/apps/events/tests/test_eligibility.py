"""Unit tests for the is_event_eligible helper."""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from apps.events.eligibility import is_event_eligible


def make_event(has_tiers=False, has_roles=False, roles=None):
    """Create a mock Event object."""
    event = MagicMock()
    event.organization = MagicMock()

    # restricted_to_tiers queryset mock
    tiers_qs = MagicMock()
    tiers_qs.exists.return_value = has_tiers
    if has_tiers:
        tiers_qs.all.return_value = [MagicMock()]
    else:
        tiers_qs.all.return_value = []
    event.restricted_to_tiers = tiers_qs

    # restricted_to_roles
    event.restricted_to_roles = roles if roles is not None else (
        ['org_staff'] if has_roles else []
    )
    return event


def make_user():
    return MagicMock()


@pytest.mark.django_db
class TestEligibilityRules:

    def test_unrestricted_event_always_eligible_for_none(self):
        """Rule 1: unrestricted event → True even for unauthenticated user."""
        event = make_event(has_tiers=False, has_roles=False)
        assert is_event_eligible(event, None) is True

    def test_unrestricted_event_always_eligible_for_authenticated_user(self):
        """Rule 1: unrestricted event → True for any authenticated user."""
        event = make_event(has_tiers=False, has_roles=False)
        assert is_event_eligible(event, make_user()) is True

    def test_unauthenticated_plus_tier_restricted_returns_false(self):
        """Rule 2: unauthenticated user + tier restriction → False."""
        event = make_event(has_tiers=True, has_roles=False)
        assert is_event_eligible(event, None) is False

    def test_unauthenticated_plus_role_restricted_returns_false(self):
        """Rule 2: unauthenticated user + role restriction → False."""
        event = make_event(has_tiers=False, has_roles=True, roles=['org_staff'])
        assert is_event_eligible(event, None) is False

    def test_tier_restricted_eligible_member(self):
        """Rule 3: user has active membership with matching tier → True."""
        event = make_event(has_tiers=True, has_roles=False)
        user = make_user()
        with patch('apps.events.eligibility.Membership') as MockMembership:
            qs = MagicMock()
            qs.exists.return_value = True
            MockMembership.objects.for_tenant.return_value.filter.return_value = qs
            assert is_event_eligible(event, user) is True

    def test_tier_restricted_ineligible_member(self):
        """Rule 3: user has no active membership with matching tier → False."""
        event = make_event(has_tiers=True, has_roles=False)
        user = make_user()
        with patch('apps.events.eligibility.Membership') as MockMembership:
            qs = MagicMock()
            qs.exists.return_value = False
            MockMembership.objects.for_tenant.return_value.filter.return_value = qs
            assert is_event_eligible(event, user) is False

    def test_inactive_membership_does_not_grant_eligibility(self):
        """Rule 3: inactive membership → False (filter includes status='active')."""
        event = make_event(has_tiers=True, has_roles=False)
        user = make_user()
        with patch('apps.events.eligibility.Membership') as MockMembership:
            qs = MagicMock()
            qs.exists.return_value = False  # inactive membership won't match
            MockMembership.objects.for_tenant.return_value.filter.return_value = qs
            result = is_event_eligible(event, user)
            assert result is False
            # Verify filter was called with status='active'
            MockMembership.objects.for_tenant.return_value.filter.assert_called_once_with(
                user=user,
                tier__in=event.restricted_to_tiers.all(),
                status='active',
            )

    def test_roles_only_restriction_eligible(self):
        """Rule 4: user has matching role → True."""
        event = make_event(has_tiers=False, has_roles=True, roles=['org_staff'])
        user = make_user()
        with patch('apps.events.eligibility.UserOrganizationRole') as MockUOR:
            uor = MagicMock()
            uor.role = 'org_staff'
            MockUOR.objects.get.return_value = uor
            assert is_event_eligible(event, user) is True

    def test_roles_only_restriction_ineligible(self):
        """Rule 4: user has a different role → False."""
        event = make_event(has_tiers=False, has_roles=True, roles=['org_staff'])
        user = make_user()
        with patch('apps.events.eligibility.UserOrganizationRole') as MockUOR:
            uor = MagicMock()
            uor.role = 'member'
            MockUOR.objects.get.return_value = uor
            assert is_event_eligible(event, user) is False

    def test_both_restrictions_tier_satisfied(self):
        """Rule 5: both sets set; tier condition satisfied → True."""
        event = make_event(has_tiers=True, has_roles=True, roles=['org_admin'])
        user = make_user()
        with patch('apps.events.eligibility.Membership') as MockMembership, \
             patch('apps.events.eligibility.UserOrganizationRole') as MockUOR:
            qs = MagicMock()
            qs.exists.return_value = True  # tier check passes
            MockMembership.objects.for_tenant.return_value.filter.return_value = qs
            uor = MagicMock()
            uor.role = 'member'  # role check fails
            MockUOR.objects.get.return_value = uor
            assert is_event_eligible(event, user) is True

    def test_both_restrictions_role_satisfied_tier_not(self):
        """Rule 5 (AC-5d): role satisfies when tier does not → True."""
        event = make_event(has_tiers=True, has_roles=True, roles=['org_staff'])
        user = make_user()
        with patch('apps.events.eligibility.Membership') as MockMembership, \
             patch('apps.events.eligibility.UserOrganizationRole') as MockUOR:
            qs = MagicMock()
            qs.exists.return_value = False  # tier check fails
            MockMembership.objects.for_tenant.return_value.filter.return_value = qs
            uor = MagicMock()
            uor.role = 'org_staff'  # role check passes
            MockUOR.objects.get.return_value = uor
            assert is_event_eligible(event, user) is True

    def test_both_restrictions_neither_satisfied(self):
        """Rule 5: both sets set; neither condition satisfied → False."""
        event = make_event(has_tiers=True, has_roles=True, roles=['org_admin'])
        user = make_user()
        with patch('apps.events.eligibility.Membership') as MockMembership, \
             patch('apps.events.eligibility.UserOrganizationRole') as MockUOR:
            qs = MagicMock()
            qs.exists.return_value = False
            MockMembership.objects.for_tenant.return_value.filter.return_value = qs
            uor = MagicMock()
            uor.role = 'member'
            MockUOR.objects.get.return_value = uor
            assert is_event_eligible(event, user) is False

    def test_roles_restriction_user_has_no_role(self):
        """Rule 4: UserOrganizationRole does not exist → False."""
        from apps.users.models import UserOrganizationRole as RealUOR
        event = make_event(has_tiers=False, has_roles=True, roles=['org_staff'])
        user = make_user()
        with patch('apps.events.eligibility.UserOrganizationRole') as MockUOR:
            MockUOR.DoesNotExist = RealUOR.DoesNotExist
            MockUOR.objects.get.side_effect = RealUOR.DoesNotExist
            assert is_event_eligible(event, user) is False
