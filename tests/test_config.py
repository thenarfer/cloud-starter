from __future__ import annotations
import pytest
from cloud_starter.config import load_settings, DEFAULT_REGION, PROJECT, MANAGED_BY

def test_load_settings_requires_owner(monkeypatch):
    monkeypatch.delenv("SPIN_OWNER", raising=False)
    monkeypatch.delenv("GITHUB_ACTOR", raising=False)
    monkeypatch.setenv("SPIN_REGION", DEFAULT_REGION)
    with pytest.raises(ValueError) as ei:
        load_settings()
    assert "SPIN_OWNER" in str(ei.value)

def test_env_overrides(monkeypatch):
    monkeypatch.setenv("SPIN_OWNER", "alice")
    monkeypatch.setenv("SPIN_REGION", "us-east-1")
    monkeypatch.setenv("SPIN_DRY_RUN", "0")
    s = load_settings()
    assert s.region == "us-east-1"
    assert s.owner == "alice"
    assert s.dry_run is False
    assert s.base_tags["Project"] == PROJECT
    assert s.base_tags["ManagedBy"] == MANAGED_BY
