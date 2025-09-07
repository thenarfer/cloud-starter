from __future__ import annotations
import json
from moto import mock_aws
from cloud_starter import cli


@mock_aws
def test_roundtrip_up_status_down_under_moto(monkeypatch, capsys):
    # Enable live behavior under moto (safe), and make owner explicit
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-north-1")
    monkeypatch.setenv("SPIN_OWNER", "pytest")
    monkeypatch.setenv("SPIN_LIVE", "1")
    monkeypatch.setenv("SPIN_DRY_RUN", "0")

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
