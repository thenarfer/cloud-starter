# Cloud Starter

Cloud Starter is a Python CLI tool called `spin` for AWS EC2 management. Sprint 2 MVP with safety-first design: dry-run by default, explicit interlocks for live operations.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

Bootstrap, build, and test the repository:
- `python -m venv .venv`
- `source .venv/bin/activate` (Linux/Mac) or `.venv\Scripts\activate` (Windows)
- `python -m pip install -U pip` -- may fail due to firewall limitations
- `pip install -e ".[test]"` -- takes 1-2 minutes. Set timeout to 5+ minutes. May fail due to network restrictions.
- `pytest -q` -- takes ~2 seconds. Set timeout to 30+ seconds.

Run the CLI tool:
- ALWAYS set `export SPIN_OWNER=@yourhandle` before using the CLI (required - will fail without it)
- ALWAYS set `export SPIN_DRY_RUN=1` for safe dry-run mode (no AWS calls)
- `spin --help` -- shows available commands (takes <1 second)
- `spin up --count 2` -- dry-run instance creation (safe, no AWS calls, takes <1 second)
- `spin status` -- dry-run status check (safe, no AWS calls when SPIN_DRY_RUN=1, takes <1 second)
- `spin down --group <id>` -- dry-run termination (safe, no AWS calls, takes <1 second)

## Validation

- ALWAYS run through complete CLI scenarios after making changes
- ALWAYS set `export SPIN_DRY_RUN=1` for safe testing (prevents accidental AWS calls)
- Test dry-run functionality: `spin up --count 1`, `spin status`, `spin down --group <id>`
- ALWAYS run `pytest -q` to validate all functionality including moto integration tests (takes ~2 seconds)
- You can build and run the CLI application - always test the actual user workflows
- NEVER attempt live AWS operations unless specifically testing AWS integration (requires AWS credentials)
- **Network connectivity issues**: pip install may fail due to firewall limitations - this is normal in restricted environments

## Environment Variables

Required:
- `SPIN_OWNER` (required): logical owner tag - set this BEFORE using any spin commands

Optional (with defaults):
- `SPIN_REGION` (default: `eu-north-1`): AWS region
- `SPIN_DRY_RUN` (default: `1`): when `1`, no AWS calls are made
- `SPIN_LIVE` (default: `0`): must be `1` AND you must pass `--apply` for live AWS operations
- `SPIN_ALLOW_GLOBAL_DOWN` (default: `0`): allow `down` without `--group` (dangerous)

## Common Tasks

The following are outputs from frequently run commands. Reference them instead of running bash commands to save time.

### Repository Structure
```
.
├── .github/
│   └── workflows/ci.yml
├── docs/
│   ├── DoD.md
│   └── DoR.md
├── src/cloud_starter/
│   ├── __init__.py
│   ├── aws.py
│   ├── cli.py
│   └── config.py
├── tests/
│   ├── conftest.py
│   ├── test_cli.py
│   ├── test_cli_moto.py
│   └── test_config.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

### Key Python Modules
- `src/cloud_starter/cli.py` -- Main CLI entry point, argument parsing
- `src/cloud_starter/aws.py` -- AWS EC2 operations with safety interlocks
- `src/cloud_starter/config.py` -- Environment variable configuration
- `tests/test_cli_moto.py` -- Integration tests using moto AWS mocking

### Project Configuration
```toml
# pyproject.toml key sections
[project]
name = "cloud-starter"
requires-python = ">=3.11"
dependencies = ["boto3>=1.34", "botocore>=1.34"]

[project.scripts]
spin = "cloud_starter.cli:main"

[project.optional-dependencies]
test = ["pytest>=8", "moto[boto3]>=5"]
```

## CLI Usage Examples

Basic dry-run workflow (safe, no AWS calls):
```bash
export SPIN_OWNER=@yourhandle
export SPIN_DRY_RUN=1
spin up --count 2
# Output: {"applied": false, "group": "abc123", "count": 2, "type": "t3.micro", "region": "eu-north-1"}

spin status
# Output: []

spin down --group abc123
# Output: {"applied": false, "terminated": []}
```

Live AWS operations (requires credentials and explicit flags):
```bash
export SPIN_OWNER=@yourhandle
export SPIN_LIVE=1
spin up --count 1 --apply          # touches AWS
spin status                        # lists real instances
spin down --group <id> --apply     # terminates real instances
```

## Development Notes

- No linting tools configured (no black, flake8, mypy)
- CI runs on Python 3.11+ with simple test execution
- Package uses setuptools with editable installation
- Sprint 2 MVP scope: AWS only, basic up/status/down commands
- Resource tagging: Project=cloud-starter, ManagedBy=spin, Owner=<your-handle>
- Safety-first design: dry-run by default, explicit interlocks for live operations