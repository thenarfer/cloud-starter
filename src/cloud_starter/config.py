from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_REGION = "eu-north-1"
PROJECT = "cloud-starter"
MANAGED_BY = "spin"


@dataclass(frozen=True)
class Settings:
    region: str
    owner: str
    dry_run: bool
    default_type: str = "t3.micro"

    @property
    def base_tags(self) -> dict[str, str]:
        return {
            "Project": PROJECT,
            "ManagedBy": MANAGED_BY,
            "Owner": self.owner,
        }


def _bool_env(name: str, default: bool) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in {"1", "true", "yes", "on"}


def load_settings() -> Settings:
    """Load runtime settings from environment.

    Security posture:
      - Region: SPIN_REGION > AWS_DEFAULT_REGION > DEFAULT_REGION
      - Owner: **required** via SPIN_OWNER (no fallback to generic USER/root).
      - Dry-run: default True unless SPIN_DRY_RUN disables it.
    """
    region = os.getenv("SPIN_REGION") or os.getenv("AWS_DEFAULT_REGION") or DEFAULT_REGION

    owner = os.getenv("SPIN_OWNER")
    if not owner:
        raise ValueError(
            "SPIN_OWNER is required (set to your handle/email). "
            "Refusing to proceed without an explicit owner."
        )

    dry_run = _bool_env("SPIN_DRY_RUN", default=True)

    return Settings(region=region, owner=owner, dry_run=dry_run)
