Here’s a clean, copy-paste **README.md** that matches your Sprint-2 plan (installable CLI, dry-run commands, tag model defined; no real cloud calls yet).

````markdown
# Cloud Starter

A transparent learning project to practice Product Ownership and disciplined delivery.

**Product Goal:** Enable developers to self-serve a few on-demand servers for tests within minutes.

---

## Sprint 2 — MVP

**Sprint Goal:** Deliver an **installable `spin` CLI** (`pip install -e .`) that exposes  
`up | status | down` (dry-run only) and define a deterministic tag model for upcoming AWS calls.

**Scope (this sprint)**
- Single provider: **AWS** (no live API calls yet)
- Commands: `spin up --count X`, `spin status`, `spin down` (all **dry-run** output)
- Deterministic tags for future resources:
  - `Project=cloud-starter`
  - `ManagedBy=spin`
  - `Owner=<github-handle>`
  - `SpinGroup=<id>`

**Non-goals (not in this sprint)**
- Multi-cloud (Azure/GCP), Terraform/IaC
- SSH/provisioners, IAM hardening
- Autoscaling, budgets/policies beyond basic teardown
- Monitoring/alerts
- Real instance lifecycle (that starts next)

---

## Prerequisites

- Python **>= 3.11**
- (For later sprints) AWS credentials & region configured (`AWS_PROFILE` or envs / `~/.aws`)
- Default region used by `spin`: **eu-north-1** (override with `--region` or `SPIN_REGION`)

---

## Quick start (dev)

Install in a virtual environment using editable mode:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate

python -m pip install -U pip
pip install -e .
````

Verify the CLI and try the dry-run commands:

```bash
spin --help
spin up --count 2
spin status
spin down
```

**Notes**

* All commands are **dry-run** in Sprint 2 (they print what would happen).
* Environment overrides:

  * `SPIN_REGION` (default `eu-north-1`)
  * `AWS_PROFILE` (optional; used in later sprints)
  * `SPIN_GROUP` (default `dev`) — used in tags to group resources

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

* **Sprint 2 (this sprint):** installable CLI, dry-run commands, tag model
* **Next:** wire minimal AWS calls in `eu-north-1` using the tag schema; `status` lists instances; safe `down`

---

## License

MIT

```

If you want, I can also add a tiny **“Tags”** section (`docs/tags.md`) and link it from this README; or keep the short tag list here and expand later when you start real AWS calls.
```
