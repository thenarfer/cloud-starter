# Cloud Starter

A transparent learning project to practice Product Ownership and disciplined delivery.  
**Product Goal:** Enable developers to self-serve a few on-demand servers for tests within minutes.

---

## Sprint 3 — Hardened Live Path & UX

**Sprint Goal:** Harden the **live path** and improve **UX** for `spin`:  
- Resolve latest AL2023 AMI via SSM  
- Add bounded waiters for instance readiness  
- Add human-friendly `--table` output for `up | status | down`

### Scope (committed P0s)

- **AMI resolution:** latest Amazon Linux 2023 (`x86_64`) fetched dynamically from SSM Parameter Store  
- **Waiters:** after `up --apply`, poll instance state until running or timeout (≈90s); on timeout exit non-zero with guidance  
- **Table output:** when `--table` is passed, print:  
  `InstanceId | PublicIp | State | SpinGroup` (for `up` and `status`)  
  `InstanceId | State` (for `down`)  
- Default output remains **JSON**, preserving compatibility with earlier scripts and tests

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
- For live calls: configure AWS credentials (`AWS_PROFILE` or `~/.aws`)

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
spin up --count 1 --apply --table          # touches AWS (AMI resolved via SSM, bounded waiter)
spin status --table
spin down --group <id> --apply --table
```

---

## Environment variables

* `SPIN_OWNER` (required): logical owner tag
* `SPIN_REGION` (optional): default region (falls back to `AWS_DEFAULT_REGION` then `eu-north-1`)
* `SPIN_DRY_RUN` (default `1`): when `1`, `status` also avoids AWS
* `SPIN_LIVE` (default `0`): must be `1` **and** you must pass `--apply` to perform live actions
* `SPIN_ALLOW_GLOBAL_DOWN` (default `0`): allow `down` without `--group` (dangerous; owner-scoped still)

---

## Run tests

```bash
pytest -q
```

Tests cover dry-run behavior and a safe “live” flow under `moto`, including:

* dynamic AMI resolution via SSM
* waiter success and timeout
* table output for `up | status | down`

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

* **Sprint 3 (this sprint):** AMI resolution via SSM, bounded waiters, table output
* **Next:** richer `status` (health/uptime), `down` waiter and summaries

---

## License

MIT
