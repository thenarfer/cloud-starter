# Definition of Done (DoD)

Our team's shared commitment to delivering a high-quality, valuable Increment. This checklist ensures every change is stable, maintainable, and secure. It is a **living document**, reviewed and refined in Sprint Retrospectives.

---

### Guiding Principles
- **Boy Scout Rule:** Leave the code cleaner than you found it.
- **Clarity over cleverness:** Optimize for the next reader.

> **N/A Rule:** When selecting **N/A**, add a one-line justification in the PR.

---

### Tier 1: Non-Negotiables (apply to all work)
- [ ] **Merged via Pull Request** to `main` (no direct pushes; **squash/merge OK**).
- [ ] **Peer review approved** by **at least one non-author** reviewer (self-approval prohibited).
- [ ] **AC proven in PR:** Provide at least one form of direct evidence:
  - [ ] Commands/output, screenshots, or a short screen recording.
  *(Links to CI/jobs are supporting evidence only.)*
- [ ] **CI green on required matrix** (tests, linters, security scanners).
- [ ] **Conventional Commits** PR title (e.g., `feat(cli): …`, `fix(aws): …`, `chore(ci): …`, `docs(readme): …`).
- [ ] **Secrets & security:** No secrets committed; security checks green.
- [ ] **Rollback noted:** e.g., `git revert <merge-commit>`; mention any data/infra cleanup.
- [ ] **Bug fix has regression test** (where feasible).
- [ ] **Docs updated:**
  - [ ] User-facing behavior changes are documented (`README.md`, `--help`).
  - [ ] N/A with justification.
- [ ] **Error paths handled:**
  - [ ] Clear messages and correct exit codes are implemented.
  - [ ] N/A with justification.
- [ ] **Issue hygiene:** PR links the primary issue (`Resolves/Closes #<id>` for completion; plain link for partials). Labels, milestone, and project column are correct.

---

### Tier 2: Conditional (apply when relevant)
- [ ] **PO acceptance** for user-visible work (comment or approval).
- [ ] **AWS guardrails respected:** Required tags (`Project`, `ManagedBy`, `Owner`, `SpinGroup`), **SPIN\_OWNER set**, and safety interlock (`SPIN_LIVE=1` + `--apply`). **`down` used `--group` unless override.** Proof via `spin status` or console filter screenshot — or **N/A**.
- [ ] **Temporary resources cleaned up:** Test VMs/buckets destroyed. Proof via `spin status` (**terminated may linger briefly**) or console screenshot.

---

### Tier 3: Professional polish (strive for features/tech-debt)
- [ ] **Observability considered** (logs/metrics for usage, performance, errors).
- [ ] **No material performance regressions** on critical paths.

---

### Type matrix
*Legend: ✅ Required · ⚪ If applicable · ➖ Not required*

| Type        | Tier 1 | Tier 2 | Tier 3 |
|-------------|--------|--------|--------|
| **Feature** | ✅     | ⚪     | ⚪     |
| **Bug**     | ✅ *(+ regression test where feasible)* | ⚪ | ➖ |
| **Tech Debt** | ✅   | ⚪     | ✅     |
| **Docs**    | ✅ *(docs-only CI)* | ⚪ | ➖ |
| **Spike**   | ✅ *(docs/findings merged; CI green)* | ➖ | ➖ |
| **Chore**   | ✅     | ⚪     | ➖     |

> **Fast-track:** Trivial changes (typo/link) may use Tier 1 only **and carry `flow: fast-track`**. Typically **Docs** or **Chore**. When in doubt, ask.