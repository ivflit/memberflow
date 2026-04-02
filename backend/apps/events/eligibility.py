"""
Eligibility logic for events.

is_event_eligible(event, user_or_none) -> bool

Rules (OR logic when both restriction sets are non-empty):
  1. Unrestricted event (both sets empty) → always True
  2. Unauthenticated user (None) + restricted → False
  3. restricted_to_tiers non-empty → True if user has active Membership with matching tier
  4. restricted_to_roles non-empty → True if user's UserOrganizationRole.role is in list
  5. Both sets non-empty → True if rule 3 OR rule 4 satisfied
"""
from apps.memberships.models import Membership
from apps.users.models import UserOrganizationRole


def is_event_eligible(event, user_or_none) -> bool:
    """Return True if the given user is eligible to attend the event."""
    has_tier_restriction = event.restricted_to_tiers.exists()
    has_role_restriction = bool(event.restricted_to_roles)

    # Rule 1: unrestricted event — always eligible
    if not has_tier_restriction and not has_role_restriction:
        return True

    # Rule 2: unauthenticated user on restricted event
    if user_or_none is None:
        return False

    user = user_or_none

    tier_eligible = False
    role_eligible = False

    # Rule 3: tier-based eligibility
    if has_tier_restriction:
        tier_eligible = Membership.objects.for_tenant(event.organization).filter(
            user=user,
            tier__in=event.restricted_to_tiers.all(),
            status='active',
        ).exists()

    # Rule 4: role-based eligibility
    if has_role_restriction:
        try:
            uor = UserOrganizationRole.objects.get(
                user=user, organization=event.organization
            )
            role_eligible = uor.role in event.restricted_to_roles
        except UserOrganizationRole.DoesNotExist:
            role_eligible = False

    # Rule 5/6: OR logic
    if has_tier_restriction and has_role_restriction:
        return tier_eligible or role_eligible
    elif has_tier_restriction:
        return tier_eligible
    else:
        return role_eligible
