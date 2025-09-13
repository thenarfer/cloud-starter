# Definition of Done (DoD)

Our team's shared commitment to quality. This checklist ensures every change is stable, maintainable, and delivers value. It is a **living document**, reviewed and refined in our Sprint Retrospectives.

---

### Tier 1: Non-Negotiables (Applies to ALL work)
- [ ] **Merged via Pull Request** to the `main` branch.
- [ ] **Peer Review Approved:** At least one other developer has approved the PR for logic, clarity, and standards.
- [ ] **CI Pipeline is Green:** All automated tests pass reliably.
- [ ] **Acceptance Criteria Proven:** All ACs are demonstrated in the PR description with commands, outputs, or screenshots.
- [ ] **User-Facing Documentation Updated:** `README.md`, `--help` text, or other relevant docs are updated.
- [ ] **Errors are Actionable:** The change provides clear error messages and appropriate exit codes for failure cases.
- [ ] **Issue Hygiene Maintained:** The PR `Closes #<issue-id>` and the issue's labels, milestone, and project status are correct.

---

### Tier 2: Conditional Checks (Apply when relevant)
- [ ] **Product Owner Acceptance:** The PO has verified the change meets the story's intent (via demo, screenshot, or ACK) for all user-visible work.
- [ ] **AWS Guardrails Respected:** All live operations use required tags (`Project`, `ManagedBy`, `Owner`, `SpinGroup`).
- [ ] **AWS Safety Interlock Used:** Live resource changes require the `SPIN_LIVE=1` + `--apply` flags.
- [ ] **AWS Teardown Verified:** `spin down` command is run and verified to leave no stray resources.

---

### Tier 3: Professional Polish (Strive for this)
- [ ] **Observability Considered:** Basic logging or metrics are added to monitor the feature's health and usage.
- [ ] **Code is Cleaner:** The change leaves the affected code area cleaner than it was found (the "Boy Scout Rule").

---

### Type Matrix
*Legend: ✅ = Required, ⚪ = If Applicable, ➖ = Not Required*

| Type            | Tier 1: Non-negotiables | Tier 2: Conditional | Tier 3: Polish |
|-----------------|-------------------------|---------------------|----------------|
| **Feature**     | ✅                      | ⚪                  | ⚪              |
| **Bug**         | ✅ (plus a regression test) | ⚪                  | ➖              |
| **Tech Debt**   | ✅                      | ➖                  | ✅              |
| **Docs**        | ✅ (docs-only CI)       | ➖                  | ➖              |
| **Spike**       | PR merges docs/findings only; CI green | ➖                  | ➖              |

> **Fast-Track Proviso:** Trivial changes (e.g., fixing a typo in comments) need only meet the Non-negotiables. If in doubt, ask.