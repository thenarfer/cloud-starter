from __future__ import annotations

import argparse
import json
import sys

from .config import load_settings, Settings
from . import aws


def _format_table(headers: list[str], rows: list[list[str]]) -> str:
    """Format data as a simple table."""
    if not rows:
        return f"{' | '.join(headers)}\n{'-' * (len(' | '.join(headers)))}\n"
    
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Format header
    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    separator = "-" * len(header_line)
    
    # Format rows  
    row_lines = []
    for row in rows:
        row_line = " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
        row_lines.append(row_line)
    
    return "\n".join([header_line, separator] + row_lines)


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
    
    if args.table:
        # For table format, we need to show instance details
        if res.get("applied") and res.get("ids"):
            # Get current status for table display
            status_res = aws.status(s, group=res["group"])
            headers = ["InstanceId", "PublicIp", "State", "SpinGroup"]
            rows = []
            for inst in status_res:
                public_ip = inst.get("public_ip", "N/A")
                rows.append([
                    inst["id"], 
                    public_ip,
                    inst["state"], 
                    inst.get("tags", {}).get("SpinGroup", "N/A")
                ])
            
            if rows:
                print(_format_table(headers, rows))
            else:
                print(_format_table(headers, []))
        else:
            # Dry-run or no instances - show preview table
            headers = ["InstanceId", "PublicIp", "State", "SpinGroup"]
            if res.get("applied") is False:  # dry-run
                rows = [["(dry-run)", "N/A", "pending", res.get("group", "N/A")]]
                print(_format_table(headers, rows))
                print(f"\nDry-run: Would launch {res.get('count', 0)} instance(s) of type {res.get('type', 'N/A')}")
            else:
                print(_format_table(headers, []))
    else:
        # Default JSON output
        print(json.dumps(res, indent=2))
    
    # Check for timeout warning and exit non-zero
    if res.get("warning"):
        print(f"Warning: {res['warning']}", file=sys.stderr)
        return 1
    
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
    sp_up.add_argument("--table", action="store_true", help="Output in table format instead of JSON")
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
