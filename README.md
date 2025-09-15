# Cloud Starter

A transparent learning project to practice Product Ownership and disciplined delivery.  
**Product Goal:** Enable developers to self-serve a few on-demand servers for tests within minutes.

The `spin` CLI is functional and provides three basic commands: `up`, `status`, and `down`.  
Dry-run is the default (safe), and live operations are explicitly guarded.

---

## Prerequisites

- Python **>= 3.11**
- **Owner is required:** set `SPIN_OWNER` to your handle/email
- Default region: **eu-north-1** (override with `SPIN_REGION` or `--region`)
- For live calls (optional): configure AWS credentials (`AWS_PROFILE` or `~/.aws`)

---

## Quick start (dev)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate

python -m pip install -U pip
pip install -e .[test]
````

Check the CLI and try dry-run:

```bash
export SPIN_OWNER=@yourhandle
spin --help
spin up --count 2 --table
spin status --table
spin down --group demo --table
```

**Notes**

* With no `--apply` or without `SPIN_LIVE=1`, output is JSON/table previews and **no AWS calls** are made.
* `spin down` requires `--group` for destructive actions (override via `SPIN_ALLOW_GLOBAL_DOWN=1` only if you really mean it).

---

## Live operations (guarded; optional)

Only when you’re ready and have credentials:

```bash
export SPIN_OWNER=@yourhandle
export SPIN_LIVE=1
spin up --count 1 --apply --table
spin status --table
spin down --group <id> --apply --table
```

---

## Environment variables

* `SPIN_OWNER` (required): logical owner tag.
* `SPIN_REGION` (optional): default region (falls back to `AWS_DEFAULT_REGION` then `eu-north-1`).
* `SPIN_DRY_RUN` (default `1`): when `1`, `status` also avoids AWS.
* `SPIN_LIVE` (default `0`): must be `1` **and** you must pass `--apply` to perform live actions.
* `SPIN_ALLOW_GLOBAL_DOWN` (default `0`): allow `down` without `--group` (dangerous; owner-scoped still).

---

## Run tests

```bash
pytest -q
```

Tests cover dry-run behavior, waiter paths, table outputs, health/uptime enrichment, down waiter/summary, and moto-based roundtrips.

---

## How we work

* **Board:** public Kanban
  [![Project Board](https://img.shields.io/badge/Project-Cloud%20Starter%20Board-blue)](https://github.com/users/thenarfer/projects/1)
* **Workflow:** WIP=1, short-lived branches, PRs only (squash merge), CI required
* **Working agreements:**

  * [Definition of Ready](docs/DoR.md)
  * [Definition of Done](docs/DoD.md)

---

## Sprints = Milestones (templated, low-friction)

We plan the sprint in a **Sprint Plan Issue** (Issue Form), then **sync** it to a **Milestone** description with a comment command. This keeps milestones consistent without blocking any work.

### 1) Create the Sprint Plan (Issue Form)

* New issue → **Sprint Plan**.
* Fill the form:

  * **Milestone name (exact)** → e.g. `Sprint 5 — Hardening & UX (2025-09-15 → 2025-09-16)`
  * **Start/End dates (YYYY-MM-DD)**
  * **Sprint Goal**, **Scope (Committed P0s)**, *(optional)* **Stretch**, **Non-goals**, **Demo Script**, **Risks & Mitigations**, **Ways of Working**, **Done when**

> The Issue is the **source of truth**; it gets labeled `sprint-plan`.

### 2) Preview & publish to Milestone

Comment on the Sprint Plan Issue:

* **`/preview-sprint`** → renders the milestone description as a comment (no changes).
* **`/sync-sprint`** → creates/updates the milestone:

  * **Title** = the **Milestone name (exact)** from the form
  * **Due date** = Sprint **End date** (23:59:59Z)
  * **Description** = templated sections + backlink to the Sprint Plan Issue

Re-running `/sync-sprint` is safe and idempotent.

### 3) Assign work as usual

* Assign issues to the sprint milestone manually (unchanged).
* Merging PRs **does not require** being in a sprint milestone.

### Optional automations

* **Daily digest**: weekday summary comment on the Sprint Plan Issue (closed/total %, days left).
* **Normalizer (warn-only)**: gentle reminder if the milestone description drifts from the plan.

---

## Roadmap

We track work via **GitHub Milestones (Sprints)** and the **Project board**. Upcoming work is planned in Sprint Plan issues and published to milestones as needed.

---

## License

MIT
