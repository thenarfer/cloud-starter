from __future__ import annotations
import pytest

@pytest.fixture(autouse=True)
def _spin_env(monkeypatch):
    # Safe defaults for all tests
    monkeypatch.setenv("SPIN_OWNER", "pytest")
    monkeypatch.setenv("SPIN_DRY_RUN", "1")          # dry-run by default
    monkeypatch.delenv("SPIN_LIVE", raising=False)   # no live calls unless test sets it
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-north-1")

    # Ensure boto/moto don't try to read a host profile
    monkeypatch.delenv("AWS_PROFILE", raising=False)
    # Provide dummy creds so boto is satisfied when moto is active
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    yield
