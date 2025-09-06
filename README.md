# Cloud Starter

A transparent learning project to practice Product Ownership and disciplined delivery.  
**Product Goal:** Enable developers to self-serve a few on-demand servers for tests within minutes.

---

## Sprint 2 — MVP

**Sprint Goal:** Deliver an **installable `spin` CLI** (`pip install -e .`) that exposes `up | status | down`.  
By default the CLI is **dry-run** and **does not contact AWS**. Live calls only happen if **both**:
1) you pass `--apply`, **and**
2) the environment has `SPIN_LIVE=1`.

This gives us a safe “seatbelt” while we learn.

### Scope (this sprint)
- Single provider: **AWS**
- Commands: `spin up --count X`, `spin status`, `spin down`
- Deterministic tag model for future resources:
  - `Project=cloud-starter`
  - `ManagedBy=spin`
  - `Owner=<your-handle>` (required)
  - `SpinGroup=<id>`

### Non-goals (not in this sprint)
- Multi-cloud (Azure/GCP), Terraform/IaC
- SSH/provisioners, IAM hardening
- Autoscaling, budgets/policies beyond basic teardown
- Monitoring/alerts
- Real instance lifecycle beyond the minimal demo

---

## Prerequisites

- Python **>= 3.11**
- **Owner is required:** set `SPIN_OWNER` to your handle/email
- Default region: **eu-north-1** (override with `SPIN_REGION` or `--region`)
- For live calls (later): configure AWS credentials (`AWS_PROFILE` or `~/.aws`)

---

## Quick start (dev)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate

python -m pip install -U pip
pip install -e .
````

Check the CLI and try dry-run:

```bash
export SPIN_OWNER=@yourhandle
spin --help
spin up --count 2
spin status
spin down
```

**Notes**

* With no `--apply` or without `SPIN_LIVE=1`, output is JSON previews and **no AWS calls** are made.
* `spin down` requires `--group` for destructive actions (override via `SPIN_ALLOW_GLOBAL_DOWN=1` only if you really mean it).

---

## Live operations (guarded; optional)

Only when you’re ready and have credentials:

```bash
export SPIN_OWNER=@yourhandle
export SPIN_LIVE=1
spin up --count 1 --apply          # touches AWS
spin status
spin down --group <id> --apply
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

Tests cover dry-run behavior and a safe “live” flow under `moto`.

---

## How we work

* **Board:** public Kanban
  [![Project Board](https://img.shields.io/badge/Project-Cloud%20Starter%20Board-blue)](https://github.com/users/thenarfer/projects/1)
* **Workflow:** WIP=1, short-lived branches, PRs only (squash merge), CI required
* **Working agreements:**

  * [Definition of Ready](docs/DoR.md)
  * [Definition of Done](docs/DoD.md)

---

## Roadmap (high level)

* **Sprint 2 (this sprint):** installable CLI, dry-run commands, tag model, safety interlocks
* **Next:** wire minimal AWS calls in `eu-north-1`; `status` lists instances; safe `down`

---

## License

MIT
