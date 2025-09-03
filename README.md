# Cloud Starter

A transparent learning project to practice Product Ownership and delivery discipline.
**Product Goal:** Enable developers to self-serve a few on-demand servers for tests within minutes.

## Sprint 1 — MVP
**Sprint Goal:** A CLI that can start N AWS instances, report health, and tear them down.

**Scope (what we will do)**
- Single provider: **AWS**
- Commands: `spin up --count X`, `spin status`, `spin down`

**Non-goals (not in this sprint)**
- Multi-cloud (Azure/GCP), Terraform/IaC
- SSH/provisioners, IAM hardening
- Autoscaling, budgets/policies beyond teardown
- Monitoring/alerts

## Prerequisites
- Python `>= 3.11`
- AWS credentials and region configured (env vars or `~/.aws`)

## How we work
- **Board:** public Kanban  
  [![Project Board](https://img.shields.io/badge/Project-Cloud%20Starter%20Board-blue)](https://github.com/users/thenarfer/projects/1)
- **Workflow:** 1 item WIP per person, short-lived branches, PRs only (squash merge), CI required
- **Working agreements:**  
  - [Definition of Ready](docs/DoR.md)  
  - [Definition of Done](docs/DoD.md)

## Demo (once Issues #1–#3 are completed)
```bash
./spin up --count 2
./spin status
./spin down
