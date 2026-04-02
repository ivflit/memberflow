# Marge Review — user-dob-address spec

**Spec:** `simpsons-no-jony/lisa/features/user-dob-address/spec.md`
**Reviewed:** 2026-04-01
**Score: 74 / 100**
**Result: ❌ FAIL — return to Lisa for re-interview**

Threshold is 90. Five gaps require clarification before this spec can proceed to Bart.

---

## What the spec does well

- Data model is precise: field names, types, and constraints are explicit.
- Permissions table covers all actor/action combinations including the cross-tenant case.
- Serializer separation is stated clearly — member-facing and admin-facing serialisers are kept distinct.
- Out-of-scope items are explicit and well-reasoned.
- Frontend layout describes field order and grouping for all three touch points (profile, registration, invite acceptance).
- Implementation patterns name specific files and functions — unusual for a spec but useful.
- Test coverage is outlined with meaningful scenarios.

---

## Gaps that must be resolved

### GAP 1 — Admin list vs. detail: where does DOB/address appear? (-8 pts)

The spec says: *"Add `date_of_birth`, `address_street`, `address_city`, `address_postcode`, `address_country` to the admin-facing serializer"* and references both `GET /api/v1/admin/members/` (list) and `GET /api/v1/admin/members/{id}/` (detail) in the same bullet.

**Problem:** These are two different serialisers in practice. Including all five fields in the paginated list response exposes a significant amount of PII for every row returned. It also affects list performance. The spec needs to state explicitly:
- Do the five fields appear in the **list** response?
- Do they appear in the **detail** response?
- Or detail only?

This is a design decision, not an implementation detail. Bart cannot make it.

---

### GAP 2 — Clearing fields: what happens when a member sends `null` or empty string? (-7 pts)

The profile update endpoint is PATCH. The spec defines that fields are optional in requests, but does not address the clearing case:

> If a member has previously saved a DOB and now wants to remove it, can they send `date_of_birth: null` (or omit it, or send `""`) to clear the value?

This matters because:
- `null` in a PATCH payload means "clear this field" in some APIs, "ignore this field" in others.
- DRF's default PATCH behaviour ignores omitted fields but accepts explicit `null` for nullable fields.
- If clearing is allowed, the frontend needs a "clear" mechanism (e.g. an empty date input clears the value).
- If clearing is not allowed (once set, DOB cannot be unset without admin intervention), the spec must say so.

The spec must define the intended behaviour. Assuming "allow clearing" is not the same as specifying it.

---

### GAP 3 — Export: access control and format not specified (-6 pts)

The spec says: *"when org admins export member data (CSV), include the five new columns"*

Two sub-gaps:

**3a — Who can trigger the export?**
The permissions table covers read/edit access to DOB/address via the API, but does not address export access. Can org **staff** trigger a member export, or only org **admins**? The distinction matters because staff can view data in the portal but may be more restricted in bulk data extraction.

**3b — What is the export endpoint?**
The spec references "member data export" but does not identify the existing export endpoint, its URL, or the file it lives in. Bart cannot locate the right file to extend without this. If the export feature does not yet exist, the spec should say so explicitly.

---

### GAP 4 — Profile page layout: same card or separate card? (-5 pts)

The spec says: *"Address section (new group below email, same card)"*

The current "Personal details" card contains 3 fields (first name, last name, email). Adding DOB + 4 address fields = 8 fields in one card. The spec does not consider whether this creates an unacceptably tall form card, and whether the address section should instead follow the existing pattern of being a **separate card** (as "Change password" is a separate card from "Personal details").

This is a UX layout decision that affects how the frontend work item is written. The spec must decide:
- All 8 fields in the "Personal details" card, OR
- DOB added to "Personal details" (4 fields), with a new "Address" card below it

If it's "same card", the spec should acknowledge the length and confirm it's intentional. If it's "separate card", the spec should state that.

---

### GAP 5 — Platform admin: read-only or can edit? (-4 pts)

The permissions table row for platform admin says *"Read any member's DOB + address — Yes (cross-tenant access via platform admin portal)"* but does not address **write** access.

Given that:
- Org admins are explicitly restricted to read-only (members self-serve)
- Platform admins have elevated cross-tenant access

The spec must state whether platform admins can edit a member's DOB/address (e.g. for support purposes), or whether they are also read-only. This affects the platform admin serialiser and view configuration.

---

## Minor observations (not blocking, but Bart should note)

- **DOB date format in export:** The spec doesn't specify whether DOB is exported as `YYYY-MM-DD`, `DD/MM/YYYY`, or another format. DRF serialises DateField as ISO 8601 by default — it's reasonable for Bart to use that in the export, but it's worth Lisa confirming if UK-style (`DD/MM/YYYY`) is expected for human-readable exports.
- **Registration form length:** Adding 5 optional fields to registration (total: 9 fields) may reduce conversion. The spec notes this is intentional ("low friction" via optional) but does not address whether the fields should be collapsed/hidden by default with a "Add address" toggle. Acceptable to defer, but should be a conscious decision.

---

## Required actions for Lisa

Re-interview the user on the five gaps above:

1. Should DOB and address appear in the admin **member list** response, the **member detail** response, or both?
2. Can members **clear** a previously saved DOB or address (send null to unset)? Or is it set-once?
3. Who can trigger the **member export** — org admins only, or org staff too? And does an export endpoint already exist?
4. Should address fields go in the **same "Personal details" card** or a **new "Address" card**?
5. Can **platform admins edit** a member's DOB/address, or are they read-only like org admins?
