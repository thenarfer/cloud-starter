#!/usr/bin/env python3
"""
Generate PR lead time metrics from GitHub GraphQL API.

This script:
1. Fetches merged PRs using GitHub GraphQL API
2. Calculates lead time (created → merged) for each PR
3. Aggregates weekly statistics (p50, p90)
4. Generates SVG chart and Markdown table
5. Stores outputs in .github/metrics/
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple, Optional
import urllib.request
import urllib.parse
import statistics
import math


class GitHubAPI:
    """Simple GitHub GraphQL API client."""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.github.com/graphql"
    
    def query(self, query: str, variables: Dict = None) -> Dict:
        """Execute GraphQL query."""
        data = {
            "query": query,
            "variables": variables or {}
        }
        
        req = urllib.request.Request(
            self.base_url,
            data=json.dumps(data).encode('utf-8'),
            headers={
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json',
                'User-Agent': 'cloud-starter-metrics/1.0'
            }
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f"Error querying GitHub API: {e}", file=sys.stderr)
            sys.exit(1)


def fetch_merged_prs(api: GitHubAPI, owner: str, repo: str, limit: int = 100) -> List[Dict]:
    """Fetch merged PRs from GitHub."""
    query = """
    query($owner: String!, $repo: String!, $limit: Int!, $cursor: String) {
      repository(owner: $owner, name: $repo) {
        pullRequests(
          states: MERGED, 
          first: $limit, 
          after: $cursor,
          orderBy: {field: CREATED_AT, direction: DESC}

        ) {
          pageInfo {
            hasNextPage
            endCursor
          }
          nodes {
            number
            title
            createdAt
            mergedAt
            author {
              login
            }
          }
        }
      }
    }
    """
    
    all_prs = []
    cursor = None
    
    while True:
        variables = {
            "owner": owner,
            "repo": repo,
            "limit": limit,
            "cursor": cursor
        }
        
        result = api.query(query, variables)
        
        if "errors" in result:
            print(f"GraphQL errors: {result['errors']}", file=sys.stderr)
            sys.exit(1)
        
        prs = result["data"]["repository"]["pullRequests"]
        all_prs.extend(prs["nodes"])
        
        if not prs["pageInfo"]["hasNextPage"]:
            break
        cursor = prs["pageInfo"]["endCursor"]
        
        # Limit to reasonable number of PRs for initial implementation
        if len(all_prs) >= 200:
            break
    
    return all_prs


def calculate_lead_times(prs: List[Dict]) -> List[Tuple[datetime, float]]:
    """Calculate lead time in hours for each PR (created -> merged)."""
    lead_times: List[Tuple[datetime, float]] = []
    for pr in prs:
        if not pr.get("createdAt") or not pr.get("mergedAt"):
            continue
        created = datetime.fromisoformat(pr["createdAt"].replace("Z", "+00:00"))
        merged = datetime.fromisoformat(pr["mergedAt"].replace("Z", "+00:00"))
        lead_time_hours = (merged - created).total_seconds() / 3600.0
        lead_times.append((merged, lead_time_hours))
    return lead_times


def aggregate_daily_stats(lead_times: List[Tuple[datetime, float]]) -> List[Dict]:
    """Aggregate lead times into daily statistics."""
    if not lead_times:
        return []

    daily_data = {}

    for merged_at, lead_time in lead_times:
        day = merged_at.date()  # just the date, no week rounding

        if day not in daily_data:
            daily_data[day] = []
        daily_data[day].append(lead_time)

    # Calculate statistics
    daily_stats = []
    for day in sorted(daily_data.keys()):
        times = daily_data[day]

        sorted_times = sorted(times)

        def percentile(data, p):
            if len(data) == 1:
                return data[0]
            index = (len(data) - 1) * p / 100
            lower = int(math.floor(index))
            upper = int(math.ceil(index))
            if lower == upper:
                return data[lower]
            return data[lower] + (data[upper] - data[lower]) * (index - lower)

        p50 = percentile(sorted_times, 50)
        p90 = percentile(sorted_times, 90)

        daily_stats.append({
            "day": day.isoformat(),
            "pr_count": len(times),
            "p50_hours": round(p50, 1),
            "p90_hours": round(p90, 1),
            "median_hours": round(statistics.median(times), 1),
            "mean_hours": round(statistics.mean(times), 1)
        })

    return daily_stats


def rolling_median(data: List[float], window: int = 7) -> List[Optional[float]]:
    """Compute rolling median with given window size."""
    result: List[Optional[float]] = []
    for i in range(len(data)):
        start = max(0, i - window + 1)
        window_slice = data[start:i+1]
        if window_slice:
            result.append(round(statistics.median(window_slice), 1))
        else:
            result.append(None)
    return result


def generate_svg_chart(daily_stats: List[Dict], output_path: str) -> None:
    """Generate SVG chart of daily P50/P90 and 7-day rolling medians."""
    if not daily_stats:
        svg_content = """<svg width="600" height="300" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="150" text-anchor="middle" font-family="Arial" font-size="16">No data available yet</text>
</svg>"""
        with open(output_path, "w") as f:
            f.write(svg_content)
        return

    # Keep last 30 days
    recent = daily_stats[-30:] if len(daily_stats) > 30 else daily_stats

    width, height, margin = 900, 420, 60
    max_hours = max(max(d["p50_hours"], d["p90_hours"]) for d in recent)
    max_hours = max(1.0, max_hours)
    x_scale = (width - 2 * margin) / max(1, len(recent) - 1)
    y_scale = (height - 2 * margin) / max_hours

    # Extract values
    p50_vals = [d["p50_hours"] for d in recent]
    p90_vals = [d["p90_hours"] for d in recent]
    p50_roll = rolling_median(p50_vals, window=7)
    p90_roll = rolling_median(p90_vals, window=7)

    svg = [
        f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
        "<style>",
        ".axis{stroke:#666;stroke-width:1}",
        ".grid{stroke:#eee;stroke-width:.5}",
        ".p50-line{stroke:#2196F3;stroke-width:1;fill:none;opacity:0.5}",   # thin
        ".p90-line{stroke:#FF9800;stroke-width:1;fill:none;opacity:0.5}",   # thin
        ".p50-roll{stroke:#0D47A1;stroke-width:2;fill:none}",              # bold
        ".p90-roll{stroke:#E65100;stroke-width:2;fill:none}",              # bold
        ".text{font-family:Arial,sans-serif;font-size:12px;fill:#333}",
        ".legend{font-family:Arial,sans-serif;font-size:11px}",
        "</style>",
        f'<rect width="{width}" height="{height}" fill="white"/>',
    ]

    # Grid
    for i in range(5):
        y = margin + i * (height - 2 * margin) / 4
        svg.append(f'<line x1="{margin}" y1="{y}" x2="{width-margin}" y2="{y}" class="grid"/>')

    # Axes
    svg.append(f'<line x1="{margin}" y1="{margin}" x2="{margin}" y2="{height-margin}" class="axis"/>')
    svg.append(f'<line x1="{margin}" y1="{height-margin}" x2="{width-margin}" y2="{height-margin}" class="axis"/>')

    # Y labels
    for i in range(5):
        val = i * max_hours / 4
        y = height - margin - (val * y_scale)
        svg.append(f'<text x="{margin-10}" y="{y+4}" text-anchor="end" class="text">{val:.0f}h</text>')

    def make_poly(values, cls):
        pts = []
        for i, val in enumerate(values):
            if val is None:
                continue
            x = margin + i * x_scale
            y = height - margin - val * y_scale
            pts.append(f"{x},{y}")
        if pts:
            svg.append(f'<polyline points="{" ".join(pts)}" class="{cls}"/>')

    # Draw daily thin lines
    make_poly(p50_vals, "p50-line")
    make_poly(p90_vals, "p90-line")

    # Draw rolling bold lines
    make_poly(p50_roll, "p50-roll")
    make_poly(p90_roll, "p90-roll")

    # Legend
    svg += [
        f'<rect x="{width-180}" y="20" width="160" height="70" fill="white" stroke="#ccc"/>',
        f'<line x1="{width-170}" y1="35" x2="{width-150}" y2="35" class="p50-line"/>',
        f'<text x="{width-145}" y="39" class="legend">P50 daily</text>',
        f'<line x1="{width-170}" y1="55" x2="{width-150}" y2="55" class="p50-roll"/>',
        f'<text x="{width-145}" y="59" class="legend">P50 7d median</text>',
        f'<line x1="{width-170}" y1="75" x2="{width-150}" y2="75" class="p90-line"/>',
        f'<text x="{width-145}" y="79" class="legend">P90 daily</text>',
        f'<line x1="{width-170}" y1="95" x2="{width-150}" y2="95" class="p90-roll"/>',
        f'<text x="{width-145}" y="99" class="legend">P90 7d median</text>',
    ]

    # Title
    svg.append(f'<text x="{width//2}" y="25" text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold">PR Lead Time (Daily + 7d median)</text>')

    # X labels (every 3rd day)
    for i, d in enumerate(recent):
        if i % 3 == 0:
            x = margin + i * x_scale
            label = datetime.fromisoformat(d["day"]).strftime("%m/%d")
            svg.append(f'<text x="{x}" y="{height - margin + 18}" text-anchor="middle" class="text">{label}</text>')

    svg.append("</svg>")
    with open(output_path, "w") as f:
        f.write("\n".join(svg))


def generate_markdown_table(daily_stats: List[Dict], output_path: str) -> None:
    if not daily_stats:
        content = """| Day | PRs | P50 | P90 |
|-----|-----|-----|-----|
| No data | - | - | - |
"""
    else:
        recent = daily_stats[-7:]
        rows = ["| Day | PRs | P50 | P90 |", "|-----|-----|-----|-----|"]
        for d in reversed(recent):
            day = datetime.fromisoformat(d["day"]).strftime("%Y-%m-%d")
            rows.append(f'| {day} | {d["pr_count"]} | {d["p50_hours"]}h | {d["p90_hours"]}h |')
        content = "\n".join(rows) + "\n"

    with open(output_path, "w") as f:
        f.write(content)



def update_readme_metrics(daily_stats: List[Dict], readme_path: str) -> None:
    if not os.path.exists(readme_path):
        print(f"README not found at {readme_path}", file=sys.stderr)
        return

    if not daily_stats:
        table = """| Day | PRs | P50 | P90 |
|-----|-----|-----|-----|
| No data | - | - | - |

*Table will be populated when PRs are merged*"""
    else:
        recent = daily_stats[-7:]
        rows = ["| Day | PRs | P50 | P90 |", "|-----|-----|-----|-----|"]
        for d in reversed(recent):
            day = datetime.fromisoformat(d["day"]).strftime("%Y-%m-%d")
            rows.append(f'| {day} | {d["pr_count"]} | {d["p50_hours"]}h | {d["p90_hours"]}h |')
        last_updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        table = "\n".join(rows) + f"\n\n*Last updated: {last_updated}*"

    import re
    pattern = r'(\*\*Recent Metrics\*\*\n\n).*?(\n\n---|\n\n## |\Z)'
    new_content = None
    with open(readme_path, "r") as f:
        content = f.read()
    new_content = re.sub(pattern, r"\1" + table + r"\2", content, flags=re.DOTALL)
    if new_content != content:
        with open(readme_path, "w") as f:
            f.write(new_content)
        print("Updated README metrics table")
    else:
        print("No changes needed for README metrics table")


def main():
    """Main entry point."""
    # Get environment variables
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        print("Error: GITHUB_TOKEN environment variable required", file=sys.stderr)
        sys.exit(1)
    
    github_repository = os.getenv('GITHUB_REPOSITORY', 'thenarfer/cloud-starter')
    if '/' not in github_repository:
        print("Error: Invalid GITHUB_REPOSITORY format, expected 'owner/repo'", file=sys.stderr)
        sys.exit(1)
    
    owner, repo = github_repository.split('/', 1)
    
    # Setup paths
    metrics_dir = os.path.join(os.path.dirname(__file__))
    chart_path = os.path.join(metrics_dir, 'pr_lead_time_chart.svg')
    table_path = os.path.join(metrics_dir, 'pr_lead_time_table.md')
    data_path = os.path.join(metrics_dir, 'pr_lead_time_data.json')
    readme_path = os.path.join(os.path.dirname(metrics_dir), '..', 'README.md')
    
    print(f"Fetching PR data for {owner}/{repo}...")
    
    # Fetch data
    api = GitHubAPI(github_token)
    prs = fetch_merged_prs(api, owner, repo)
    
    print(f"Found {len(prs)} merged PRs")
    
    # Calculate metrics
    lead_times = calculate_lead_times(prs)
    daily_stats = aggregate_daily_stats(lead_times)

    print(f"Calculated stats for {len(daily_stats)} days")

    # Save raw data
    with open(data_path, "w") as f:
        json.dump({
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "daily_stats": daily_stats,
            "total_prs": len(prs),
        }, f, indent=2)

    # Generate outputs
    generate_svg_chart(daily_stats, chart_path)
    generate_markdown_table(daily_stats, table_path)
    update_readme_metrics(daily_stats, readme_path)
    
    print(f"Generated outputs:")
    print(f"  - Chart: {chart_path}")
    print(f"  - Table: {table_path}")
    print(f"  - Data: {data_path}")
    print(f"  - Updated README: {readme_path}")


if __name__ == '__main__':
    main()