---
name: "Feature / Enhancement PR"
about: "Add or improve behavior (user-visible or internal capability)"
---

<!-- Title rule: conventional commit.
     Example: feat(cli): add --table for status -->

## Why
One short paragraph describing the desired outcome / user value.

## What changed
- Bulleted list of changes (flags, defaults, errors, any breaking notes).
- Keep terse. Link to design/issue for details.

## How to test (copy/paste)
```bash
# Example (edit as needed)
pytest -q
export SPIN_OWNER=<you> SPIN_LIVE=1
spin up --count 1 --apply --table
spin status --table
spin down --group <id> --apply --table
````

## Acceptance Criteria verification

- [ ] AC#1 – demo evidence below (logs/screenshots)
- [ ] AC#2 – …
- [ ] README / `--help` updated if user-facing
- [ ] Tests cover happy path + one failure; CI green

## Safety

- [ ] **Breaking change?** no / yes → migration notes:
- [ ] Live ops require `SPIN_LIVE=1` **and** `--apply`
- [ ] Teardown remains owner + group scoped
- [ ] Rollback: revert this PR (no data migration)

## Evidence (screenshots / logs / links)

<attach here>

—
*This PR asserts our process docs: see `docs/DoR.md` & `docs/DoD.md`.*
**Closes #<issue-id>**
