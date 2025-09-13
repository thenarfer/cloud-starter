# Definition of Ready (DoR)

Our checklist for achieving a shared understanding before work begins. This prevents mid-sprint ambiguity and churn. It is a **living document**, used during Backlog Refinement and tuned in our Sprint Retrospectives.

---

### Core Readiness Checks (Applies to all items)
- [ ] **Well-Scoped:** The item represents a single, valuable outcome and is small enough to complete in a Sprint (ideally S/M size).
- [ ] **Value Stated ("The Why"):** A short paragraph clarifies the business or user value and links to any relevant context.
- [ ] **Acceptance Criteria are Testable:** The ACs are a clear checkbox list of observable outcomes.
  - For CLI work: Exact commands and expected output (tables, JSON, exit codes) are provided.
  - At least one "unhappy path" or error case is defined.
- [ ] **Non-Goals Defined:** 1-3 clear bullet points state what is explicitly *out of scope*.
- [ ] **Test Plan Clear:** The intended approach for verification is stated (e.g., "add unit tests to X," "manual verification via Y").
- [ ] **Dependencies Unblocked:** Any dependencies (on other teams, IAM policies, environment access) are identified and resolved.
- [ ] **Metadata Set:** `Type`, `Priority`, and `Size` labels are set. The issue is in the correct `Milestone` and `Project` column to signal it is ready for a Sprint.

---

### Type-Specific Checks

**Bug**
- [ ] **Reproducible:** Clear "Observed vs. Expected" behavior with a minimal reproduction case.
- [ ] **Impact Assessed:** Severity and potential blast radius are noted.

**Spike**
- [ ] **Question Defined:** A single, clear question or hypothesis is stated.
- [ ] **Timebox Agreed:** An explicit time limit (e.g., 4 hours) is set.
- [ ] **Deliverable Stated:** The output is defined (e.g., "a short document with findings and a recommendation").

**Docs / Fast-Track**
- [ ] **Scope Defined:** A list of pages, sections, or anchors to be updated is included.

---

### Sizing Guide
*The goal of sizing is to ensure work fits in a Sprint and to surface misunderstandings.*

- **S (Small):** ~1 day or less. Well-understood, low-risk.
- **M (Medium):** ~1-3 days. A standard, contained piece of work.
- **L (Large):** **Must be split** into smaller, valuable S/M stories before becoming "Ready."

### Hold in Refinement if...
- The scope requires multiple, distinct changes.
- The Acceptance Criteria are ambiguous or cannot be objectively verified.
- There are blocking dependencies or significant technical unknowns.
- The item is still sized as **L**.
