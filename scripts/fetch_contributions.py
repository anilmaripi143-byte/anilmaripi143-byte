import os
import json
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GITHUB_REPOSITORY_OWNER", "anilmaripi143-byte")
URL = f"https://github.com/users/{USERNAME}/contributions"


def parse_tooltip_text(text: str) -> int:
    if not text:
        return 0
    cleaned = text.strip().lower()
    if "no contribution" in cleaned:
        return 0
    match = re.search(r"(\d+)\s+contribution", cleaned)
    if match:
        return int(match.group(1))
    return 0


def parse_contribution_cells(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    cells = []

    # Map tooltips by target ID (for="contribution-day-component-...")
    tooltip_map = {}
    for tt in soup.select("tool-tip"):
        for_id = tt.get("for")
        if for_id:
            tooltip_map[for_id] = tt.get_text(" ", strip=True)

    # Primary strategy: td.ContributionCalendar-day[data-date]
    td_days = soup.select("td.ContributionCalendar-day[data-date]")
    if td_days:
        for td in td_days:
            date_val = td.get("data-date")
            if not date_val:
                continue
            level_val = td.get("data-level") or "0"
            elem_id = td.get("id") or ""
            
            tooltip_str = tooltip_map.get(elem_id, "") or td.get("aria-label", "")
            count = parse_tooltip_text(tooltip_str)

            # If count couldn't be parsed from tooltip text but data-count or data-level exists
            if count == 0 and td.get("data-count"):
                try:
                    count = int(td.get("data-count"))
                except ValueError:
                    pass

            cells.append({
                "date": date_val,
                "count": count,
                "level": level_val
            })

    # Fallback strategy: rect[data-date] (older GitHub markup)
    if not cells:
        rect_days = soup.select("rect[data-date]")
        for rect in rect_days:
            date_val = rect.get("data-date")
            if not date_val:
                continue
            level_val = rect.get("data-level") or "0"
            count_val = rect.get("data-count")
            aria_label = rect.get("aria-label", "")
            title_elem = rect.find("title")
            tooltip_str = aria_label or (title_elem.get_text(" ", strip=True) if title_elem else "")

            if count_val is not None:
                try:
                    count = int(count_val)
                except ValueError:
                    count = parse_tooltip_text(tooltip_str)
            else:
                count = parse_tooltip_text(tooltip_str)

            cells.append({
                "date": date_val,
                "count": count,
                "level": level_val
            })

    return cells


def calculate_statistics(cells: list[dict]) -> dict:
    if not cells:
        return {
            "total_contributions": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "best_day": None,
            "monthly_totals": {}
        }

    sorted_cells = sorted(cells, key=lambda c: c["date"])
    total_contributions = sum(c["count"] for c in sorted_cells)
    best_day = max(sorted_cells, key=lambda c: c["count"])

    monthly_totals = defaultdict(int)
    for c in sorted_cells:
        month_key = c["date"][:7]  # YYYY-MM
        monthly_totals[month_key] += c["count"]

    # Calculate streaks
    longest_streak = 0
    running_streak = 0

    for c in sorted_cells:
        if c["count"] > 0:
            running_streak += 1
            if running_streak > longest_streak:
                longest_streak = running_streak
        else:
            running_streak = 0

    # Current streak calculation working backward from the latest day
    current_streak = 0
    # Check if latest day or yesterday has contributions
    idx = len(sorted_cells) - 1
    # Allow current day to be 0 if yesterday was > 0
    if idx >= 0 and sorted_cells[idx]["count"] == 0 and idx > 0 and sorted_cells[idx - 1]["count"] > 0:
        idx -= 1

    while idx >= 0 and sorted_cells[idx]["count"] > 0:
        current_streak += 1
        idx -= 1

    return {
        "total_contributions": total_contributions,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly_totals": dict(monthly_totals)
    }


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    output_path = repo_root / "data" / "contributions.json"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print(f"Fetching contribution data from: {URL}")
    response = requests.get(URL, headers=headers, timeout=20)
    if response.status_code != 200:
        print(f"ERROR: GitHub returned HTTP {response.status_code}")
        sys.exit(1)

    cells = parse_contribution_cells(response.text)
    if not cells:
        print("ERROR: Failed to parse GitHub contribution cells. HTML layout may have changed.")
        sys.exit(1)

    stats = calculate_statistics(cells)

    data = {
        "username": USERNAME,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "total_contributions": stats["total_contributions"],
        "current_streak": stats["current_streak"],
        "longest_streak": stats["longest_streak"],
        "best_day": stats["best_day"],
        "monthly_totals": stats["monthly_totals"],
        "cells": cells
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Successfully fetched {len(cells)} cells. Total contributions: {stats['total_contributions']}.")
    print(f"Saved contribution data to: {output_path}")


if __name__ == "__main__":
    main()
