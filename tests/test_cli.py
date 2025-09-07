from __future__ import annotations
import json
import re
import pytest
from cloud_starter import cli

def _parse_json(capsys):
    out = capsys.readouterr()
    return out.out.strip(), out.err.strip()

def test_up_dry_run_json_and_exit0(capsys):
    rc = cli.main(["up", "--count", "2"])
    assert rc == 0
    out, err = _parse_json(capsys)
    assert err == ""
    data = json.loads(out)
    assert data["applied"] is False
    assert data["count"] == 2
    assert isinstance(data["group"], str) and len(data["group"]) > 0
    assert data["type"] == "t3.micro"
    assert data["region"]  # has some default (eu-north-1)

def test_status_dry_run_empty(capsys):
    rc = cli.main(["status"])
    assert rc == 0
    out, err = _parse_json(capsys)
    assert err == ""
    data = json.loads(out or "[]")
    assert isinstance(data, list)
    assert data == []

def test_down_requires_group_returns_error(capsys):
    rc = cli.main(["down"])
    assert rc == 2  # safety: must supply --group unless override env set
    out, err = _parse_json(capsys)
    assert out == ""
    assert "Refusing to down without --group" in err

def test_down_with_group_dry_run_ok(capsys):
    # Reuse a group from a dry-run 'up' so the JSON shape is consistent
    cli.main(["up", "--count", "1"])
    out, _ = _parse_json(capsys)
    group = json.loads(out)["group"]

    rc = cli.main(["down", "--group", group])
    assert rc == 0
    out2, err2 = _parse_json(capsys)
    assert err2 == ""
    data = json.loads(out2)
    assert data["applied"] is False
    assert "terminated" in data
    assert isinstance(data["terminated"], list)
