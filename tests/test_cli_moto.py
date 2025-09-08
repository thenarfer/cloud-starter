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
def test_down_with_friendly_summary_under_moto(monkeypatch, capsys):
    """Test down command with friendly summary under moto."""
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-north-1")
    monkeypatch.setenv("SPIN_OWNER", "pytest")
    monkeypatch.setenv("SPIN_LIVE", "1")
    monkeypatch.setenv("SPIN_DRY_RUN", "0")

    # Launch an instance first
    rc = cli.main(["up", "--count", "1", "--apply"])
    assert rc == 0
    out, err = capsys.readouterr()
    up = json.loads(out)
    group = up["group"]

    # Down with friendly summary
    rc = cli.main(["down", "--group", group, "--apply"])
    assert rc == 0
    out, err = capsys.readouterr()
    
    # Should contain JSON and friendly summary
    assert "applied" in out  # JSON part
    assert "terminated" in out  # JSON part
    assert "Terminated 1 instance(s)" in out  # Summary part
    assert f"in group {group}" in out  # Summary part
    assert "(owner=pytest)" in out  # Summary part


@mock_aws
def test_status_with_table_output_under_moto(monkeypatch, capsys):
    """Test --table output for status command under moto."""
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-north-1")
    monkeypatch.setenv("SPIN_OWNER", "pytest")
    monkeypatch.setenv("SPIN_LIVE", "1")
    monkeypatch.setenv("SPIN_DRY_RUN", "0")

    # First launch an instance
    rc = cli.main(["up", "--count", "1", "--apply"])
    assert rc == 0
    out, err = capsys.readouterr()
    up = json.loads(out)
    group = up["group"]

    # Test status with table output
    rc = cli.main(["status", "--table"])
    assert rc == 0
    out, err = capsys.readouterr()
    assert "InstanceId" in out
    assert "State" in out
    assert "Health" in out
    assert "Uptime(min)" in out
    assert "SpinGroup" in out

    # Test status with JSON (enhanced fields)
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
def test_up_with_table_output_under_moto(monkeypatch, capsys):
    """Test --table output for up command under moto."""
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-north-1")
    monkeypatch.setenv("SPIN_OWNER", "pytest")
    monkeypatch.setenv("SPIN_LIVE", "1")
    monkeypatch.setenv("SPIN_DRY_RUN", "0")

    # UP with table output
    rc = cli.main(["up", "--count", "1", "--apply", "--table"])
    assert rc == 0
    out, err = capsys.readouterr()
    assert "InstanceId" in out
    assert "PublicIp" in out
    assert "State" in out
    assert "SpinGroup" in out


@mock_aws
def test_roundtrip_up_status_down_under_moto(monkeypatch, capsys):
    # Enable live behavior under moto (safe), and make owner explicit
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-north-1")
    monkeypatch.setenv("SPIN_OWNER", "pytest")
    monkeypatch.setenv("SPIN_LIVE", "1")
    monkeypatch.setenv("SPIN_DRY_RUN", "0")

    # Moto provides default AMI for the service parameter - no need to seed

    # UP (apply)
    rc = cli.main(["up", "--count", "2", "--apply"])
    assert rc == 0
    out, err = capsys.readouterr()
    up = json.loads(out)
    assert up["applied"] is True
    assert up["count"] == 2
    group = up["group"]
    assert isinstance(group, str) and group

    # STATUS (live listing via moto)
    rc = cli.main(["status"])
    assert rc == 0
    out, err = capsys.readouterr()
    st = json.loads(out or "[]")
    assert isinstance(st, list)

    # DOWN (apply) — requires group
    rc = cli.main(["down", "--group", group, "--apply"])
    assert rc == 0
    out, err = capsys.readouterr()
    # Split output - first part is JSON, second part is friendly summary
    lines = out.strip().split('\n')
    json_end = 0
    for i, line in enumerate(lines):
        if line.strip() == '}':
            json_end = i + 1
            break
    
    json_output = '\n'.join(lines[:json_end])
    summary_output = '\n'.join(lines[json_end:]).strip()
    
    dn = json.loads(json_output)
    assert dn["applied"] is True
    assert "terminated" in dn
    assert "Terminated 2 instance(s)" in summary_output
