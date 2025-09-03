# Definition of Done (DoD)

This DoD applies to every Product Backlog Item (PBI) in this repository.

## For each PBI
- Code is merged via **pull request** to `main` (no direct pushes).
- **Acceptance Criteria are met** and demonstrated with exact commands/output in the PR.
- README / CLI `--help` updated if user-visible behavior changed.
- **Teardown leaves the account clean**: `spin down` removes managed instances; no stray resources.
- Only **tagged resources** are touched (`Project=cloud-starter`, `Owner=<alias>`, `Session=<timestamp>`).
- Commands are **idempotent** where practical (e.g., safe re-runs, “nothing to do” is not an error).
- Errors are **clear and actionable** (non-zero exit codes; message suggests remedy).
- Issue hygiene:
  - Issue is linked to the PR (`Closes #<id>`), labeled (type, priority), and in the Project.
  - Milestone set for the current sprint; Project status ends at **Done** (automation OK).

## For the sprint (meta)
- Sprint Review demo matches the Sprint Goal.
- Sprint Retro captured with max **two** action items (owners & due dates).