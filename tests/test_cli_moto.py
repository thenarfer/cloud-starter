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

    # UP with table output
    rc = cli.main(["up", "--count", "1", "--apply", "--table"])
    assert rc == 0
    out, err = capsys.readouterr()
    assert "InstanceId" in out
    assert "PublicIp" in out
    assert "State" in out
    assert "SpinGroup" in out
from cloud_starter.aws import resolve_ami_via_ssm


@mock_aws
def test_resolve_ami_via_ssm_success():
    """Test successful AMI resolution via SSM."""
    ami_id = resolve_ami_via_ssm("eu-north-1")
    assert ami_id.startswith("ami-")  # moto provides a default AMI


@mock_aws
def test_roundtrip_up_status_down_under_moto(monkeypatch, capsys):
    # Enable live behavior under moto (safe), and make owner explicit
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-north-1")
    monkeypatch.setenv("SPIN_OWNER", "pytest")
    monkeypatch.setenv("SPIN_LIVE", "1")
    monkeypatch.setenv("SPIN_DRY_RUN", "0")

    # Moto provides default AMI for the service parameter - no need to seed

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
    dn = json.loads(out)
    assert dn["applied"] is True
    assert "terminated" in dn

from cloud_starter import cli

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
def test_status_with_table_output(monkeypatch, capsys):
    """Test --table output for status command."""
    monkeypatch.setenv("SPIN_LIVE", "1")
    monkeypatch.setenv("SPIN_DRY_RUN", "0")

    cli.main(["up", "--count", "1", "--apply"])
    capsys.readouterr()  # clear buffer

    rc = cli.main(["status", "--table"])
    assert rc == 0
    out, err = capsys.readouterr()
    assert "InstanceId" in out
    assert "PublicIp" in out
    assert "State" in out
    assert "SpinGroup" in out
    assert err == ""


@mock_aws
def test_down_with_table_output(monkeypatch, capsys):
    """Test --table output for down command."""
    monkeypatch.setenv("SPIN_LIVE", "1")
    monkeypatch.setenv("SPIN_DRY_RUN", "0")

    # Launch an instance first
    cli.main(["up", "--count", "1", "--apply"])
    out, _ = capsys.readouterr()
    group = json.loads(out)["group"]

    rc = cli.main(["down", "--group", group, "--apply", "--table"])
    assert rc == 0
    out, err = capsys.readouterr()
    assert "InstanceId" in out
    assert "terminated" in out
    assert err == ""
