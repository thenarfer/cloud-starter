# Cloud Starter

A transparent learning project to practice Product Ownership and disciplined delivery.

**Product Goal:** Enable developers to self-serve a few on-demand servers for tests within minutes.

---

## Sprint 2 — MVP

**Sprint Goal:** Deliver an **installable `spin` CLI** (`pip install -e .`) that exposes  
`up | status | down` with **dry-run by default**, plus a deterministic tag model for upcoming AWS calls.

> **Safety model**
> - All commands are **dry-run** unless you pass `--apply` **and** set `SPIN_LIVE=1`.
> - Live operations are **owner-scoped** and **tag-scoped** to prevent touching unmanaged resources.

### Scope (this sprint)
- Single provider: **AWS**
- Commands: `spin up --count X`, `spin status`, `spin down`  
  (dry-run output by default; no AWS calls unless `SPIN_LIVE=1` + `--apply`)
- Deterministic tags for future resources:
  - `Project=cloud-starter`
  - `ManagedBy=spin`
  - `Owner=<github-handle>`  *(required via `SPIN_OWNER`)*
  - `SpinGroup=<id>`

### Non-goals (not in this sprint)
- Multi-cloud (Azure/GCP), Terraform/IaC
- SSH/provisioners, IAM hardening
- Autoscaling, budgets/policies beyond basic teardown
- Monitoring/alerts
- Real instance lifecycle improvements (start next)

---

## Prerequisites

- Python **>= 3.11**
- `SPIN_OWNER` **must** be set (your handle/email).  
- For **live** operations only (not required for dry-run):
  - AWS credentials & region (`AWS_PROFILE` / envs / `~/.aws`)
  - Default region is **eu-north-1** (override with `--region` or `SPIN_REGION`)

---

## Quick start (dev)

Create a venv and install in editable mode:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate

python -m pip install -U pip
pip install -e .
````

Verify the CLI and dry-run behavior:

```bash
export SPIN_OWNER=@you
spin --help
spin up --count 2
spin status
spin down
```

Live operations (only when you really mean it):

```bash
# Requires AWS creds + region configured
export SPIN_OWNER=@you
export SPIN_LIVE=1
spin up --count 1 --apply
spin status
spin down --group <the-group-from-up> --apply
```

---

## Run tests

```bash
pytest -q
```

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

* **Sprint 2 (this sprint):** installable CLI, dry-run commands, tag model, safety interlock
* **Next:** wire minimal AWS calls in `eu-north-1`; `status` lists instances; safe `down` flow