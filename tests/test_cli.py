import pytest
from cloud_starter import cli


def test_help_exits_0():
    # argparse prints help and raises SystemExit(0)
    with pytest.raises(SystemExit) as e:
        cli.main(["--help"])
    assert e.value.code == 0


def test_up_dry_run_prints_and_exits_0(capsys):
    rc = cli.main(["up", "--count", "2"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "would launch 2 instance" in out


def test_status_and_down_exit_0():
    assert cli.main(["status"]) == 0
    assert cli.main(["down"]) == 0
