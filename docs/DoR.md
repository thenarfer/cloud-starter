# Definition of Ready (DoR)

A collaborative checklist to ensure a Product Backlog Item (PBI) is well understood before entering a Sprint. DoR is **not a gate**; it guides refinement to reduce ambiguity and churn.

---

### Guiding Principles
- **Shared understanding:** PO and Developers align on problem and outcome.
- **INVEST lens:** Independent · Negotiable · Valuable · Estimable · Small · Testable.

---

### Core readiness checks (apply to all work)
- [ ] **Value stated (“why”)** — ideally as a user story (`As a [user], I want [action], so that [value]`).
- [ ] **Sprint Goal fit** — we can say how this supports the goal.
- [ ] **Acceptance criteria are verifiable** — checklist of pass/fail conditions, incl. **at least one unhappy path**.
- [ ] **Acceptance demo plan** — how we’ll show it (commands/screenshots/URL).
- [ ] **Non-goals** — 1–3 bullets explicitly out of scope.
- [ ] **Right-sized (S/M)** — fits in one Sprint; if **L**, split before commitment.
- [ ] **Dependencies & access** — external deps/IAM/env are identified and **not blocking** (or a clear plan exists).
- [ ] **Assumptions & risks** — called out briefly, with mitigation if needed.
- [ ] **PO & Devs aligned** — PO agrees ACs are testable and is available for clarification.
- [ ] **Metadata set** — Type, Priority, Size; correct Milestone/Project column; intended PR template; **assignee (single DRI)**.

---

### Type-specific checks
**Bug**
- [ ] **Reproducible** — minimal steps, observed vs expected, impact/severity noted.

**Spike** *(time-boxed research; output is learning, not shippable code)*
- [ ] **Question defined** — one clear question/hypothesis.
- [ ] **Timebox agreed** — typically 2–4 hours.
- [ ] **Deliverable stated** — short findings doc + recommendation and follow-up issues (if any).