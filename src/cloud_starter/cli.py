from __future__ import annotations

import argparse
import json
import sys

from .config import load_settings, Settings
from . import aws


def _settings_for_apply(args) -> Settings:
    """Return runtime settings, toggling dry_run off when --apply is used.

    Note: Actual live AWS calls still require the SPIN_LIVE interlock inside aws.py.
    """
    s = load_settings()
    if args.command in {"up", "down"} and getattr(args, "apply", False):
        # Keep same values but mark not-dry-run for apply semantics
        s = Settings(region=s.region, owner=s.owner, dry_run=False, default_type=s.default_type)
    return s


def cmd_up(args) -> int:
    s = _settings_for_apply(args)
    res = aws.up_instances(
        s,
        count=args.count,
        instance_type=args.type,
        group=args.group,
        apply=args.apply,
    )
    print(json.dumps(res, indent=2))
    return 0


def cmd_status(args) -> int:
    s = load_settings()
    res = aws.status(s, group=args.group)
    print(json.dumps(res, indent=2))
    return 0


def cmd_down(args) -> int:
    s = _settings_for_apply(args)
    try:
        res = aws.down(s, group=args.group, apply=args.apply)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2
    print(json.dumps(res, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="spin", description="Tiny EC2 MVP helper.")
    sub = p.add_subparsers(dest="command", required=True)

    # up
    sp_up = sub.add_parser("up", help="Launch N instances (dry-run unless --apply).")
    sp_up.add_argument("--count", type=int, required=True, help="Number of instances")
    sp_up.add_argument("--type", default=None, help="EC2 instance type (default t3.micro)")
    sp_up.add_argument("--group", default=None, help="Optional group id to reuse")
    sp_up.add_argument("--apply", action="store_true", help="Apply for real (requires SPIN_LIVE=1)")
    sp_up.set_defaults(func=cmd_up)

    # status
    sp_st = sub.add_parser("status", help="List instances for this owner (optionally by group).")
    sp_st.add_argument("--group", default=None, help="Group id to filter")
    sp_st.set_defaults(func=cmd_status)

    # down
    sp_dn = sub.add_parser(
        "down", help="Terminate instances for a group (dry-run unless --apply; requires --group)."
    )
    sp_dn.add_argument("--group", default=None, help="Group id (required unless override env set)")
    sp_dn.add_argument("--apply", action="store_true", help="Apply for real (requires SPIN_LIVE=1)")
    sp_dn.set_defaults(func=cmd_down)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
