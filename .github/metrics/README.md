# PR Lead Time Metrics

This directory contains scripts and data for tracking PR lead time metrics.

## Files

- `generate_metrics.py` - Main script that fetches PR data from GitHub GraphQL API and generates metrics
- `pr_lead_time_chart.svg` - SVG chart showing weekly P50/P90 lead times
- `pr_lead_time_table.md` - Markdown table with recent metrics 
- `pr_lead_time_data.json` - Raw metrics data (generated)
- `requirements.txt` - Dependencies (none - uses Python built-ins only)

## How it works

1. **Data Collection**: Uses GitHub GraphQL API to fetch merged PRs with creation and merge timestamps
2. **Calculation**: Computes lead time (created → merged) for each PR in hours
3. **Aggregation**: Groups PRs by week and calculates P50/P90 percentiles
4. **Visualization**: Generates SVG chart and Markdown table
5. **Integration**: Updates main README.md with latest metrics

## Automation

The metrics are automatically updated by the GitHub Action `.github/workflows/update-pr-metrics.yml`:

- Triggers when a PR is merged
- Runs `generate_metrics.py` 
- Commits updated outputs back to repo
- Can also be triggered manually via `workflow_dispatch`

## Local Testing

```bash
# Test with sample data
python test_metrics.py

# Test README update
python test_readme.py

# Run actual generation (requires GITHUB_TOKEN)
export GITHUB_TOKEN=your_token
python generate_metrics.py
```

## Environment Variables

- `GITHUB_TOKEN` - Required for API access
- `GITHUB_REPOSITORY` - Defaults to 'thenarfer/cloud-starter'