## Why
<!-- brief context / problem -->

## What changed
- …

## How to test
```bash
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -e .[test]
pytest -q

export SPIN_OWNER=<you>
spin up --count 1
spin status
spin down   # expects refusal without --group
````

## Safety

* Live ops require BOTH `SPIN_LIVE=1` and `--apply`.
* `down` requires `--group` (override exists but discouraged).

## Links

* Project / Milestone: …
* Closes #<issue-ids>
