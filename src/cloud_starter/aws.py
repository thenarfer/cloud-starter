from __future__ import annotations

import os
import random
import string

from botocore.exceptions import ClientError, NoCredentialsError

from .config import Settings, PROJECT, MANAGED_BY


def _live_ok() -> bool:
    """Dynamic safety interlock: only touch AWS when SPIN_LIVE=1/true/yes/on."""
    return os.getenv("SPIN_LIVE", "").lower() in {"1", "true", "yes", "on"}


# Approved AMIs for Sprint 2 (explicitly scoped)
_DEFAULT_AMIS = {
    # Amazon Linux 2023 x86_64 (as of 2025-09; track updates via follow-up issue)
    "eu-north-1": "ami-03c6121ede8ddb108",
}


def ec2_client(region: str):
    """Lazy import so dry-run works without boto3 installed.

    When a live call is requested but boto3 is missing, provide a helpful error.
    """
    try:
        import boto3  # local import to allow dry-run without boto3
    except ModuleNotFoundError as e:
        raise RuntimeError(
            "boto3 is required for live operations. Install with: pip install boto3"
        ) from e
    return boto3.client("ec2", region_name=region)


def ssm_client(region: str):
    """Lazy import so dry-run works without boto3 installed.

    When a live call is requested but boto3 is missing, provide a helpful error.
    """
    try:
        import boto3  # local import to allow dry-run without boto3
    except ModuleNotFoundError as e:
        raise RuntimeError(
            "boto3 is required for live operations. Install with: pip install boto3"
        ) from e
    return boto3.client("ssm", region_name=region)


def _spin_group_id(length: int = 8) -> str:
    alphabet = string.ascii_lowercase + string.digits
    return "".join(random.choice(alphabet) for _ in range(length))


def resolve_ami_via_ssm(region: str) -> str:
    """Resolve latest AL2023 AMI ID via SSM Parameter Store.
    
    Uses public parameter: /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-6.1-x86_64
    """
    parameter_name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-6.1-x86_64"
    
    try:
        resp = ssm_client(region).get_parameter(Name=parameter_name)
        ami_id = resp["Parameter"]["Value"]
        if not ami_id.startswith("ami-"):
            raise RuntimeError(f"Invalid AMI ID format returned from SSM: {ami_id}")
        return ami_id
    except NoCredentialsError as e:
        raise RuntimeError(
            "No AWS credentials found. "
            "To run live, set AWS_PROFILE or run `aws configure`. "
            "Otherwise omit --apply (dry-run)."
        ) from e
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code", "Unknown")
        if code == "ParameterNotFound":
            raise RuntimeError(
                f"AMI parameter not found in region {region}. "
                f"Parameter: {parameter_name}. "
                "This region may not support AL2023 or the parameter path has changed."
            ) from e
        elif code in ("AccessDenied", "UnauthorizedOperation"):
            raise RuntimeError(
                f"Access denied when fetching AMI parameter from SSM in region {region}. "
                f"Parameter: {parameter_name}. "
                "Ensure your AWS credentials have SSM:GetParameter permission."
            ) from e
        else:
            raise RuntimeError(
                f"Failed to fetch AMI from SSM in region {region} (code={code}). "
                f"Parameter: {parameter_name}."
            ) from e


def _default_ami(region: str) -> str:
    if region not in _DEFAULT_AMIS:
        raise ValueError(
            f"Region {region!r} not supported for default AMI in Sprint 2. "
            "Add a mapping or implement dynamic AMI resolution."
        )
    return _DEFAULT_AMIS[region]


def up_instances(
    settings: Settings,
    count: int,
    *,
    instance_type: str | None = None,
    group: str | None = None,
    apply: bool = False,
) -> dict:
    """Create instances for a group. In dry-run (or without live interlock), returns a preview."""
    group = group or _spin_group_id()
    itype = instance_type or settings.default_type

    if not (apply and _live_ok()):
        return {
            "applied": False,
            "group": group,
            "count": int(count),
            "type": itype,
            "region": settings.region,
        }

    image_id = resolve_ami_via_ssm(settings.region)
    tags = [
        {"Key": "Project", "Value": PROJECT},
        {"Key": "ManagedBy", "Value": MANAGED_BY},
        {"Key": "Owner", "Value": settings.owner},
        {"Key": "SpinGroup", "Value": group},
    ]
    params = {
        "ImageId": image_id,
        "InstanceType": itype,
        "MinCount": count,
        "MaxCount": count,
        "TagSpecifications": [
            {"ResourceType": "instance", "Tags": tags},
            {"ResourceType": "volume", "Tags": tags},
        ],
    }

    try:
        resp = ec2_client(settings.region).run_instances(**params)
        ids = [i["InstanceId"] for i in resp.get("Instances", [])]
        return {
            "applied": True,
            "group": group,
            "ids": ids,
            "count": len(ids),
            "type": itype,
            "region": settings.region,
        }
    except NoCredentialsError as e:
        raise RuntimeError(
            "No AWS credentials found. "
            "To run live, set AWS_PROFILE or run `aws configure`. "
            "Otherwise omit --apply (dry-run)."
        ) from e
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code", "Unknown")
        raise RuntimeError(f"Failed to launch instances (code={code}).") from e


def _status_live(settings: Settings, group: str | None) -> list[dict]:
    """Live status with pagination; **Owner**-scoped; optional group constraint."""
    filters = [
        {"Name": "tag:Project", "Values": [PROJECT]},
        {"Name": "tag:ManagedBy", "Values": [MANAGED_BY]},
        {"Name": "tag:Owner", "Values": [settings.owner]},
    ]
    if group:
        filters.append({"Name": "tag:SpinGroup", "Values": [group]})

    out: list[dict] = []
    token: str | None = None
    while True:
        kwargs = {"Filters": filters, "MaxResults": 1000}
        if token:
            kwargs["NextToken"] = token
        try:
            resp = ec2_client(settings.region).describe_instances(**kwargs)
        except NoCredentialsError as e:
            raise RuntimeError(
                "No AWS credentials found. "
                "To run live, set AWS_PROFILE or run `aws configure`. "
                "Otherwise keep dry-run."
            ) from e
        for res in resp.get("Reservations", []):
            for inst in res.get("Instances", []):
                tags = {t["Key"]: t["Value"] for t in inst.get("Tags", [])}
                out.append(
                    {
                        "id": inst["InstanceId"],
                        "state": inst.get("State", {}).get("Name", "unknown"),
                        "tags": tags,
                    }
                )
        token = resp.get("NextToken")
        if not token:
            break
    return out


def status(settings: Settings, group: str | None = None) -> list[dict]:
    """Return instance summaries.

    - If dry-run or live interlock is off → empty list (no API calls).
    - Otherwise → live query scoped to Owner (+ optional group).
    """
    if settings.dry_run or not _live_ok():
        return []
    return _status_live(settings, group)


def down(settings: Settings, group: str | None = None, *, apply: bool = False) -> dict:
    """Terminate instances in a group (or, with override, all owned)."""
    if group is None and os.getenv("SPIN_ALLOW_GLOBAL_DOWN", "").lower() not in {
        "1",
        "true",
        "yes",
        "on",
    }:
        raise ValueError(
            "Refusing to down without --group; set SPIN_ALLOW_GLOBAL_DOWN=1 to override (dangerous)."
        )

    if not (apply and _live_ok()):
        return {"applied": False, "terminated": []}

    ids = [x["id"] for x in _status_live(settings, group)]
    if not ids:
        return {"applied": True, "terminated": []}

    try:
        ec2_client(settings.region).terminate_instances(InstanceIds=ids)
        return {"applied": True, "terminated": ids}
    except NoCredentialsError as e:
        raise RuntimeError(
            "No AWS credentials found. "
            "To run live, set AWS_PROFILE or run `aws configure`. "
            "Otherwise omit --apply (dry-run)."
        ) from e
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code", "Unknown")
        raise RuntimeError(f"Failed to terminate instances (code={code}).") from e
