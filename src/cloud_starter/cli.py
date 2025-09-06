from __future__ import annotations
import argparse
import os
import sys
from dataclasses import dataclass

DEFAULT_REGION = os.getenv("SPIN_REGION", "eu-north-1")

@dataclass
class Context:
    region: str
    profile: str | None
    group: str
    dry_run: bool = True

def cmd_up(ctx: Context, count: int) -> int:
    print(f"[dry-run={ctx.dry_run}] would launch {count} instance(s) in {ctx.region}")
    print(f"tags: Project=cloud-starter, ManagedBy=spin, Owner={os.getenv('USER','user')}, SpinGroup={ctx.group}")
    # real AWS call comes in #3
    return 0

def cmd_status(ctx: Context) -> int:
    print(f"[dry-run={ctx.dry_run}] would query instances for SpinGroup={ctx.group} in {ctx.region}")
    # next sprint: list instance ids & states
    return 0

def cmd_down(ctx: Context) -> int:
    print(f"[dry-run={ctx.dry_run}] would terminate instances tagged SpinGroup={ctx.group} in {ctx.region}")
    return 0

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="spin", description="Minimal cloud-starter CLI (dry-run MVP)")
    p.add_argument("--region", default=DEFAULT_REGION, help=f"AWS region (default: {DEFAULT_REGION})")
    p.add_argument("--profile", default=os.getenv("AWS_PROFILE"), help="AWS named profile (optional)")
    p.add_argument("--group", default=os.getenv("SPIN_GROUP", "dev"), help="Tag group identifier (SpinGroup)")
    p.add_argument("--no-dry-run", action="store_true", help="(reserved) perform real operations")
    sub = p.add_subparsers(dest="command", required=True)

    up = sub.add_parser("up", help="launch N instances (dry-run)")
    up.add_argument("--count", type=int, default=1, help="number of instances to launch")
    up.set_defaults(fn=lambda args, ctx: cmd_up(ctx, args.count))

    st = sub.add_parser("status", help="print health/status (dry-run)")
    st.set_defaults(fn=lambda args, ctx: cmd_status(ctx))

    dn = sub.add_parser("down", help="terminate instances (dry-run)")
    dn.set_defaults(fn=lambda args, ctx: cmd_down(ctx))
    return p

def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    ctx = Context(
        region=args.region,
        profile=args.profile,
        group=args.group,
        dry_run=not args.no_dry_run,
    )
    return args.fn(args, ctx)

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
