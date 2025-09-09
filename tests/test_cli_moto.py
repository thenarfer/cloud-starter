from __future__ import annotations
import json
from moto import mock_aws
import pytest
from cloud_starter import cli
from cloud_starter.aws import resolve_ami_via_ssm


@mock_aws
def test_resolve_ami_via_ssm_success():
    """Test successful AMI resolution via SSM."""
    ami_id = resolve_ami_via_ssm("eu-north-1")
    assert ami_id.startswith("ami-")  # moto provides a default AMI


@mock_aws
def test_up_with_table_output_under_moto(monkeypatch, capsys):
    """Test --table output for up command under moto."""
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-north-1")
    monkeypatch.setenv("SPIN_OWNER", "pytest")
    monkeypatch.setenv("SPIN_LIVE", "1")
    monkeypatch.setenv("SPIN_DRY_RUN", "0")

    rc = cli.main(["up", "--count", "1", "--apply", "--table"])
    assert rc == 0
    out, err = capsys.readouterr()
    assert "InstanceId" in out
    assert "PublicIp" in out
    assert "State" in out
    assert "SpinGroup" in out


@mock_aws
def test_status_with_table_and_json_output(monkeypatch, capsys):
    """Test --table and JSON output for status under moto."""
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-north-1")
    monkeypatch.setenv("SPIN_OWNER", "pytest")
    monkeypatch.setenv("SPIN_LIVE", "1")
    monkeypatch.setenv("SPIN_DRY_RUN", "0")

    # Launch an instance
    rc = cli.main(["up", "--count", "1", "--apply"])
    assert rc == 0
    out, err = capsys.readouterr()
    up = json.loads(out)
    group = up["group"]

    # Table output
    rc = cli.main(["status", "--table"])
    assert rc == 0
    out, err = capsys.readouterr()
    assert "InstanceId" in out
    assert "State" in out
    assert "Health" in out
    assert "Uptime(min)" in out
    assert "SpinGroup" in out

    # JSON output (enriched fields)
    rc = cli.main(["status"])
    assert rc == 0
    out, err = capsys.readouterr()
    status_data = json.loads(out)
    assert len(status_data) > 0
    inst = status_data[0]
    assert "health" in inst
    assert "uptime_min" in inst
    assert isinstance(inst["uptime_min"], int)
    assert inst["health"] in ("OK", "IMPAIRED", "INITIALIZING", "UNKNOWN")

    # Clean up
    rc = cli.main(["down", "--group", group, "--apply"])
    assert rc == 0


@mock_aws
def test_status_initializing_health(monkeypatch, capsys):
    """Force INITIALIZING health status via monkeypatch."""
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-north-1")
    monkeypatch.setenv("SPIN_OWNER", "pytest")
    monkeypatch.setenv("SPIN_LIVE", "1")
    monkeypatch.setenv("SPIN_DRY_RUN", "0")

    # Launch instance
    rc = cli.main(["up", "--count", "1", "--apply"])
    assert rc == 0
    capsys.readouterr()

    # Monkeypatch status to simulate INITIALIZING
    def fake_status_live(settings, group=None):
        return [{
            "id": "i-1234567890abcdef0",
            "state": "pending",
            "health": "INITIALIZING",
            "uptime_min": 0,
            "tags": {"SpinGroup": "demo"},
        }]

    monkeypatch.setattr("cloud_starter.aws._status_live", fake_status_live)

    rc = cli.main(["status"])
    assert rc == 0
    out, err = capsys.readouterr()
    data = json.loads(out)
    assert data[0]["health"] == "INITIALIZING"


def test_status_api_error_exit_code(monkeypatch, capsys):
    """Simulate API error and ensure CLI exits non-zero with message."""
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-north-1")
    monkeypatch.setenv("SPIN_OWNER", "pytest")

    def fake_status(settings, group=None):
        raise RuntimeError("simulated API error")

    monkeypatch.setattr("cloud_starter.aws.status", fake_status)

    rc = cli.main(["status"])
    assert rc == 1
    out, err = capsys.readouterr()
    assert "simulated API error" in err


@mock_aws
def test_roundtrip_up_status_down_under_moto(monkeypatch, capsys):
    """Full roundtrip test: up → status → down under moto."""
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-north-1")
    monkeypatch.setenv("SPIN_OWNER", "pytest")
    monkeypatch.setenv("SPIN_LIVE", "1")
    monkeypatch.setenv("SPIN_DRY_RUN", "0")

    # UP
    rc = cli.main(["up", "--count", "2", "--apply"])
    assert rc == 0
    out, err = capsys.readouterr()
    up = json.loads(out)
    assert up["applied"] is True
    assert up["count"] == 2
    group = up["group"]

    # STATUS
    rc = cli.main(["status"])
    assert rc == 0
    out, err = capsys.readouterr()
    st = json.loads(out or "[]")
    assert isinstance(st, list)

    # DOWN
    rc = cli.main(["down", "--group", group, "--apply"])
    assert rc == 0
    out, err = capsys.readouterr()
    dn = json.loads(out)
    assert dn["applied"] is True
    assert "terminated" in dn


@mock_aws
def test_up_waiter_timeout(monkeypatch, capsys):
    """Simulate waiter timeout and check non-zero exit + warning."""
    monkeypatch.setenv("SPIN_LIVE", "1")
    monkeypatch.setenv("SPIN_DRY_RUN", "0")

    # Force waiter to fail
    monkeypatch.setattr("cloud_starter.aws.wait_for_instances_running", lambda *a, **k: False)

    rc = cli.main(["up", "--count", "1", "--apply"])
    assert rc == 1
    out, err = capsys.readouterr()
    assert "timed out" in err or "Warning" in err


@mock_aws
def test_down_with_table_output(monkeypatch, capsys):
    """Test --table output for down command."""
    monkeypatch.setenv("SPIN_LIVE", "1")
    monkeypatch.setenv("SPIN_DRY_RUN", "0")

    cli.main(["up", "--count", "1", "--apply"])
    out, _ = capsys.readouterr()
    group = json.loads(out)["group"]

    rc = cli.main(["down", "--group", group, "--apply", "--table"])
    assert rc == 0
    out, err = capsys.readouterr()
    assert "InstanceId" in out
    assert "terminated" in out
    assert err == ""
