# Feature Spec: User Date of Birth and Address

**Feature name:** `user-dob-address`
**Interviewed:** 2026-04-01
**Revised:** 2026-04-01 (post-Marge review)
**Status:** Ready for Marge re-review

---

## Summary

Add date of birth and a single residential address to the `User` model. Both fields are optional and can be cleared back to blank after being set. Members can view and edit their own data on the profile page, at registration, and when accepting an invitation. Org admins and staff can view member data in the admin portal (detail view shows full DOB/address; list view shows calculated age only). Org admins can trigger a CSV export of member data which includes DOB and address. Platform admins can read and edit these fields across all tenants for support purposes.

Guardian/family membership (paying for a junior member's subscription) is explicitly out of scope — it is a separate feature.

---

## Goals

- Clubs need to record member date of birth (particularly relevant for age-category tiers such as junior/senior/veteran) and a home address.
- Members can self-serve — entering, updating, and clearing their own details without contacting an admin.
- Org admins and staff can view member DOB and address in the admin portal.
- Org admins can export full member data including DOB and address as a CSV.
- Platform admins can edit DOB and address for support purposes.

---

## Out of Scope

- Billing address (separate from residential) — one address only.
- Guardian / parent-child / family membership relationships — separate spec.
- Age-based tier restrictions or automatic junior flagging.
- Making DOB or address required (both remain optional).

---

## Data Model

### Changes to `apps/users/models.py` — `User`

Add the following optional fields to the existing `User` model:

| Field | Type | Constraints |
|---|---|---|
| `date_of_birth` | `DateField` | `null=True`, `blank=True` |
| `address_street` | `CharField(max_length=255)` | `null=True`, `blank=True` |
| `address_city` | `CharField(max_length=100)` | `null=True`, `blank=True` |
| `address_postcode` | `CharField(max_length=20)` | `null=True`, `blank=True` |
| `address_country` | `CharField(max_length=100)` | `null=True`, `blank=True` |

No new models. No index changes needed (these fields are not used in filters).

Empty strings submitted by the frontend must be coerced to `null` before saving — use a custom `to_internal_value` or serialiser `validate_<field>` to normalise `""` → `None` for all five fields.

---

## API

### Existing endpoints — extend, do not add new ones

**`GET /api/v1/profile/`** — member's own profile (renamed from `/api/v1/me/`)
Add `date_of_birth`, `address_street`, `address_city`, `address_postcode`, `address_country` to the response body. `date_of_birth` is serialised as ISO 8601 (`YYYY-MM-DD`) or `null`.

**`PATCH /api/v1/profile/`** — member updates own profile
Accept the same five new fields. All are optional in the request body. Validate `date_of_birth` as a valid date not in the future. Sending `null` or an empty string for any field clears the stored value back to `null` (clearing is explicitly allowed).

**`POST /api/v1/auth/register/`** — self-registration
Accept the five new fields as optional in the request body. Pass them through to user creation.

**`POST /api/v1/auth/invite/accept/`** — invite acceptance
Accept the five new fields as optional in the request body. Pass them through to user creation.

**`GET /api/v1/admin/members/`** — org admin member list
Add a calculated `age` field (integer, member's current age derived from `date_of_birth`, or `null` if DOB is not set). Do **not** include raw `date_of_birth` or any address fields in the list response — keep the list lightweight.

**`GET /api/v1/admin/members/{id}/`** — org admin member detail
Add all five fields: `date_of_birth`, `address_street`, `address_city`, `address_postcode`, `address_country`. Also include `age` (calculated). The detail serialiser is a superset of the list serialiser.

**`GET /api/v1/platform/members/{id}/`** — platform admin member detail
Add the same five fields. Platform admins can also **edit** these fields via `PATCH /api/v1/platform/members/{id}/` (for support purposes). Validation rules are identical to the member-facing PATCH.

**`GET /api/v1/admin/members/export/`** — new export endpoint (CSV)
This endpoint does not yet exist. Create it as part of this feature. Accessible to org admins only (not org staff). Returns a CSV file with one row per member and the following columns (in order):

`id`, `email`, `first_name`, `last_name`, `date_of_birth`, `address_street`, `address_city`, `address_postcode`, `address_country`, `role`, `is_active`, `created_at`

- `date_of_birth` exported as `YYYY-MM-DD` or empty string if null.
- Response: `Content-Type: text/csv`, `Content-Disposition: attachment; filename="members.csv"`.
- Scoped to `request.tenant` — exports only the current org's members.

---

## Serialiser Separation

| Serialiser | Location | New fields |
|---|---|---|
| `ProfileSerializer` | `apps/users/serializers.py` | All 5 fields (read + write) |
| `AdminMemberListSerializer` | `apps/admin_portal/serializers.py` | `age` (calculated, read-only) only |
| `AdminMemberDetailSerializer` | `apps/admin_portal/serializers.py` | All 5 fields + `age` (read-only) |
| `PlatformMemberSerializer` | `apps/admin_portal/serializers.py` | All 5 fields (read + write) + `age` |

The five raw fields must **not** appear in `AdminMemberListSerializer`. `age` must never appear in any member-to-member serialiser.

---

## Frontend

### Profile Page (`/profile`)

**"Personal details" card** — extend with DOB (below last name, above email):
- Label: `Date of birth`
- Input type: `date`
- Optional — no `required` attribute
- Saves with the existing "Save changes" button

**New "Address" card** — separate card below "Personal details", following the same card pattern as "Change password":
- Card title: `Address`
- Fields (all optional):
  - Street address (text, placeholder: `123 Main Street`)
  - City (text, placeholder: `City`)
  - Postcode (text, placeholder: `Postcode`)
  - Country (text, placeholder: `Country`)
- Its own "Save changes" button with its own loading/success/error state
- Success message: `✓ Address updated`

### Registration Page (`/register`)

Add the five optional fields below the password field, before the submit button:
- Date of birth (date input, label: `Date of birth`)
- A subtle section divider or label: `Address (optional)`
- Street address, City, Postcode, Country (text inputs)

All fields carry no `required` attribute. Registration remains low-friction.

### Invite Acceptance Page (`/set-password?mode=invite`)

In invite mode, first name and last name are already collected above the password field. Add the five optional fields below the name fields, above the password field:
- Date of birth
- Address (street, city, postcode, country) with a subtle label/divider

Same layout pattern as registration.

---

## Permissions

| Actor | Action | Allowed? |
|---|---|---|
| Member | Read own DOB + address | Yes |
| Member | Edit own DOB + address (including clearing) | Yes |
| Member | Read another member's DOB + address | No |
| Org staff | View member list (age only) | Yes |
| Org staff | View member detail (full DOB + address) | Yes |
| Org staff | Edit a member's DOB + address | No |
| Org staff | Trigger member export | No — admins only |
| Org admin | View member list (age only) | Yes |
| Org admin | View member detail (full DOB + address) | Yes |
| Org admin | Edit a member's DOB + address | No — members self-serve |
| Org admin | Trigger member export | Yes |
| Platform admin | Read any member's DOB + address (cross-tenant) | Yes |
| Platform admin | Edit any member's DOB + address (cross-tenant) | Yes — for support purposes |

---

## Validation Rules

- `date_of_birth`: must be a valid date; must not be in the future; no minimum age enforced; `null` and `""` both accepted to clear the field.
- `address_*` fields: free text, no format validation beyond max length; `null` and `""` both accepted to clear; postcode stored as a string (no country-specific format validation).
- Empty string inputs are coerced to `null` in the serialiser before persistence — Django CharField with `null=True, blank=True` should store `null`, not `""`.

---

## Implementation Patterns

### Backend
- Extend `User` in `apps/users/models.py` — add five nullable fields.
- Generate and commit migration.
- Extend `ProfileSerializer` in `apps/users/serializers.py` — add fields + empty-string-to-null coercion.
- Add `AdminMemberListSerializer` and `AdminMemberDetailSerializer` in `apps/admin_portal/serializers.py` (or extend existing equivalents) — list gets `age` only, detail gets all five fields + `age`.
- Add calculated `age` property/method: `(today - date_of_birth).years` using `dateutil.relativedelta` or equivalent; returns `null` if DOB is not set.
- Extend registration view (`apps/users/views.py`) — pass new fields to user creation.
- Extend invite acceptance view — same pattern.
- Create new `GET /api/v1/admin/members/export/` view returning CSV; restrict to `IsOrgAdmin`.
- Extend platform admin member detail view to accept PATCH on the five fields.

### Frontend
- Extend `editForm` ref in `ProfileView.vue` to include `date_of_birth`, `address_street`, `address_city`, `address_postcode`, `address_country`.
- Add a second address form + separate save handler `saveAddress()` — same pattern as `saveProfile()`.
- SCSS for the new Address card goes in `src/styles/views/_profile.scss`. No `<style>` blocks in Vue files.
- Extend `RegisterView.vue` and `SetPasswordView.vue` (invite mode) to capture and submit the five new fields.
- `getProfile` response already populates `profile.value = data` — new fields arrive automatically once the backend returns them.

---

## Test Coverage

- Unit: `date_of_birth` future-date validation rejects correctly.
- Unit: Empty string input for `date_of_birth` and address fields is coerced to `null` before save.
- Unit: `age` calculation returns correct integer; returns `null` when DOB is null.
- E2E: Member fills in DOB + address on profile page; values persist on reload.
- E2E: Member clears DOB by submitting empty date field; DOB shows blank on reload.
- E2E: Member provides DOB + address during registration; profile page shows the values.
- E2E: Member provides DOB + address during invite acceptance; profile page shows the values.
- E2E: Org admin views member detail — sees full DOB and address.
- E2E: Org admin views member list — sees `age` column, does not see raw DOB or address columns.
- E2E: Org admin triggers CSV export — downloaded file contains DOB and address columns.
- E2E: Org staff cannot access the export endpoint (403).
- E2E: Platform admin edits a member's DOB via platform admin portal; change is reflected in member's profile.
- Tenant isolation: Org A admin cannot read Org B member's DOB/address via the admin member detail endpoint.
- Tenant isolation: Member export returns only the current tenant's members.
