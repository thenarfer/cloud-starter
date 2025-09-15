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
          orderBy: {field: MERGED_AT, direction: DESC}
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
    """Calculate lead time in hours for each PR."""
    lead_times = []
    
    for pr in prs:
        if not pr["createdAt"] or not pr["mergedAt"]:
            continue
        
        created = datetime.fromisoformat(pr["createdAt"].replace('Z', '+00:00'))
        merged = datetime.fromisoformat(pr["mergedAt"].replace('Z', '+00:00'))
        
        lead_time_hours = (merged - created).total_seconds() / 3600
        
        lead_times.append((merged, lead_time_hours))
    
    return lead_times


def aggregate_weekly_stats(lead_times: List[Tuple[datetime, float]]) -> List[Dict]:
    """Aggregate lead times into weekly statistics."""
    if not lead_times:
        return []
    
    # Group by week (Monday start)
    weekly_data = {}
    
    for merged_at, lead_time in lead_times:
        # Get Monday of the week
        days_since_monday = merged_at.weekday()
        week_start = merged_at.date() - timedelta(days=days_since_monday)
        
        if week_start not in weekly_data:
            weekly_data[week_start] = []
        weekly_data[week_start].append(lead_time)
    
    # Calculate statistics
    weekly_stats = []
    for week_start in sorted(weekly_data.keys()):
        times = weekly_data[week_start]
        
        if len(times) == 0:
            continue
        
        # Calculate percentiles
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
        
        weekly_stats.append({
            "week_start": week_start.isoformat(),
            "pr_count": len(times),
            "p50_hours": round(p50, 1),
            "p90_hours": round(p90, 1),
            "median_hours": round(statistics.median(times), 1),
            "mean_hours": round(statistics.mean(times), 1)
        })
    
    return weekly_stats


def generate_svg_chart(weekly_stats: List[Dict], output_path: str) -> None:
    """Generate SVG chart of weekly metrics."""
    if not weekly_stats:
        # Create placeholder chart
        svg_content = """<svg width="600" height="300" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="150" text-anchor="middle" font-family="Arial" font-size="16">No data available yet</text>
</svg>"""
        with open(output_path, 'w') as f:
            f.write(svg_content)
        return
    
    # Simple SVG chart implementation
    width = 800
    height = 400
    margin = 60
    
    # Get data ranges
    max_hours = max(max(stat["p50_hours"], stat["p90_hours"]) for stat in weekly_stats[-12:])  # Last 12 weeks
    recent_stats = weekly_stats[-12:] if len(weekly_stats) > 12 else weekly_stats
    
    # Scale factors
    x_scale = (width - 2 * margin) / max(1, len(recent_stats) - 1)
    y_scale = (height - 2 * margin) / max(max_hours, 1)
    
    svg_parts = [
        f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
        '<style>',
        '  .axis { stroke: #666; stroke-width: 1; }',
        '  .grid { stroke: #eee; stroke-width: 0.5; }',
        '  .p50-line { stroke: #2196F3; stroke-width: 2; fill: none; }',
        '  .p90-line { stroke: #FF9800; stroke-width: 2; fill: none; }',
        '  .text { font-family: Arial, sans-serif; font-size: 12px; fill: #333; }',
        '  .legend { font-family: Arial, sans-serif; font-size: 11px; }',
        '</style>'
    ]
    
    # Background
    svg_parts.append(f'<rect width="{width}" height="{height}" fill="white"/>')
    
    # Grid lines
    for i in range(5):
        y = margin + i * (height - 2 * margin) / 4
        svg_parts.append(f'<line x1="{margin}" y1="{y}" x2="{width - margin}" y2="{y}" class="grid"/>')
    
    # Axes
    svg_parts.append(f'<line x1="{margin}" y1="{margin}" x2="{margin}" y2="{height - margin}" class="axis"/>')
    svg_parts.append(f'<line x1="{margin}" y1="{height - margin}" x2="{width - margin}" y2="{height - margin}" class="axis"/>')
    
    # Y-axis labels
    for i in range(5):
        y = height - margin - i * (height - 2 * margin) / 4
        value = i * max_hours / 4
        svg_parts.append(f'<text x="{margin - 10}" y="{y + 4}" text-anchor="end" class="text">{value:.0f}h</text>')
    
    # Data lines
    if len(recent_stats) > 1:
        # P50 line
        p50_points = []
        p90_points = []
        
        for i, stat in enumerate(recent_stats):
            x = margin + i * x_scale
            y_p50 = height - margin - stat["p50_hours"] * y_scale
            y_p90 = height - margin - stat["p90_hours"] * y_scale
            
            p50_points.append(f"{x},{y_p50}")
            p90_points.append(f"{x},{y_p90}")
        
        svg_parts.append(f'<polyline points="{" ".join(p50_points)}" class="p50-line"/>')
        svg_parts.append(f'<polyline points="{" ".join(p90_points)}" class="p90-line"/>')
    
    # Legend
    svg_parts.extend([
        f'<rect x="{width - 150}" y="20" width="120" height="50" fill="white" stroke="#ccc"/>',
        f'<line x1="{width - 140}" y1="35" x2="{width - 120}" y2="35" class="p50-line"/>',
        f'<text x="{width - 115}" y="39" class="legend">P50 (median)</text>',
        f'<line x1="{width - 140}" y1="55" x2="{width - 120}" y2="55" class="p90-line"/>',
        f'<text x="{width - 115}" y="59" class="legend">P90</text>',
    ])
    
    # Title
    svg_parts.append(f'<text x="{width // 2}" y="25" text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold">PR Lead Time (Weekly)</text>')
    
    # X-axis labels (last few weeks)
    for i, stat in enumerate(recent_stats[-6:]):  # Show last 6 weeks
        if i % 2 == 0:  # Show every other week to avoid crowding
            x = margin + (len(recent_stats) - 6 + i) * x_scale
            date_str = datetime.fromisoformat(stat["week_start"]).strftime("%m/%d")
            svg_parts.append(f'<text x="{x}" y="{height - margin + 20}" text-anchor="middle" class="text">{date_str}</text>')
    
    svg_parts.append('</svg>')
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(svg_parts))


def generate_markdown_table(weekly_stats: List[Dict], output_path: str) -> None:
    """Generate Markdown table with latest metrics."""
    if not weekly_stats:
        table_content = """| Week | PRs | P50 | P90 |
|------|-----|-----|-----|
| No data | - | - | - |
"""
    else:
        # Show last 4 weeks
        recent_stats = weekly_stats[-4:]
        
        rows = ["| Week | PRs | P50 | P90 |", "|------|-----|-----|-----|"]
        
        for stat in reversed(recent_stats):  # Most recent first
            week_date = datetime.fromisoformat(stat["week_start"]).strftime("%Y-%m-%d")
            row = f"| {week_date} | {stat['pr_count']} | {stat['p50_hours']}h | {stat['p90_hours']}h |"
            rows.append(row)
        
        table_content = '\n'.join(rows) + '\n'
    
    with open(output_path, 'w') as f:
        f.write(table_content)


def update_readme_metrics(weekly_stats: List[Dict], readme_path: str) -> None:
    """Update README.md with latest metrics table."""
    if not os.path.exists(readme_path):
        print(f"README not found at {readme_path}", file=sys.stderr)
        return
    
    with open(readme_path, 'r') as f:
        content = f.read()
    
    # Generate table content
    if not weekly_stats:
        table_content = """| Week | PRs | P50 | P90 |
|------|-----|-----|-----|
| No data | - | - | - |

*Table will be populated when PRs are merged*"""
    else:
        # Show last 4 weeks
        recent_stats = weekly_stats[-4:]
        
        rows = ["| Week | PRs | P50 | P90 |", "|------|-----|-----|-----|"]
        
        for stat in reversed(recent_stats):  # Most recent first
            week_date = datetime.fromisoformat(stat["week_start"]).strftime("%Y-%m-%d")
            row = f"| {week_date} | {stat['pr_count']} | {stat['p50_hours']}h | {stat['p90_hours']}h |"
            rows.append(row)
        
        last_updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        table_content = '\n'.join(rows) + f'\n\n*Last updated: {last_updated}*'
    
    # Find and replace the metrics section
    import re
    
    # Pattern to match the metrics table section
    pattern = r'(\*\*Recent Metrics\*\*\n\n).*?(\n\n---|\n\n## |\Z)'
    replacement = r'\1' + table_content + r'\2'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if new_content != content:
        with open(readme_path, 'w') as f:
            f.write(new_content)
        print(f"Updated README metrics table")
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
    weekly_stats = aggregate_weekly_stats(lead_times)
    
    print(f"Calculated stats for {len(weekly_stats)} weeks")
    
    # Save raw data
    with open(data_path, 'w') as f:
        json.dump({
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'weekly_stats': weekly_stats,
            'total_prs': len(prs)
        }, f, indent=2)
    
    # Generate outputs
    generate_svg_chart(weekly_stats, chart_path)
    generate_markdown_table(weekly_stats, table_path)
    update_readme_metrics(weekly_stats, readme_path)
    
    print(f"Generated outputs:")
    print(f"  - Chart: {chart_path}")
    print(f"  - Table: {table_path}")
    print(f"  - Data: {data_path}")
    print(f"  - Updated README: {readme_path}")


if __name__ == '__main__':
    main()