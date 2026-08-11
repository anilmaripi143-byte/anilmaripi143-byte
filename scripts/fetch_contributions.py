import json
import re
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup


def parse_tooltip_count(tooltip_text: str, level: str | None) -> int:
    if not tooltip_text:
        return 0 if level in (None, "0") else 1

    cleaned = tooltip_text.strip()
    if not cleaned:
        return 0 if level in (None, "0") else 1

    lowered = cleaned.lower()
    if lowered.startswith("no contributions"):
        return 0

    match = re.search(r"(\d+)\s+contribution", lowered)
    if match:
        return int(match.group(1))

    return 0 if level in (None, "0") else 1


def parse_contribution_cells(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    tooltip_by_for = {}
    for tooltip in soup.find_all("tool-tip"):
        target_id = tooltip.get("for")
        if not target_id:
            continue
        tooltip_by_for[target_id] = tooltip.get_text(" ", strip=True)

    cells = []
    for td in soup.select("td.ContributionCalendar-day[data-date]"):
        date_value = td.get("data-date")
        level_value = td.get("data-level")
        count = parse_tooltip_count(tooltip_by_for.get(td.get("id"), ""), level_value)
        if not date_value:
            continue
        cells.append(
            {
                "date": date_value,
                "count": count,
                "level": level_value,
            }
        )

    if not cells:
        for rect in soup.select("rect[data-date][data-count]"):
            date_value = rect.get("data-date")
            count_value = rect.get("data-count")
            level_value = rect.get("data-level") or rect.get("fill")
            if not date_value or count_value is None:
                continue
            try:
                count = int(count_value)
            except ValueError:
                continue
            cells.append(
                {
                    "date": date_value,
                    "count": count,
                    "level": level_value,
                }
            )

    return cells


def calculate_streaks(cells: list[dict]) -> dict:
    if not cells:
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "best_day": None,
            "total_contributions": 0,
            "monthly_totals": {},
        }

    sorted_cells = sorted(cells, key=lambda item: item["date"])
    total = sum(item["count"] for item in sorted_cells)
    today = datetime.strptime(sorted_cells[-1]["date"], "%Y-%m-%d").date()
    streak = 0
    longest = 0
    current = 0
    best_day = max(sorted_cells, key=lambda item: item["count"])
    prev_date = None
    monthly_totals = defaultdict(int)

    for cell in sorted_cells:
        date_obj = datetime.strptime(cell["date"], "%Y-%m-%d").date()
        monthly_totals[date_obj.strftime("%Y-%m")] += cell["count"]
        if prev_date is None:
            streak = 1 if cell["count"] > 0 else 0
        else:
            if date_obj == prev_date + timedelta(days=1) and cell["count"] > 0:
                streak += 1
            elif date_obj == prev_date + timedelta(days=1):
                streak = 0
            else:
                streak = 1 if cell["count"] > 0 else 0
        longest = max(longest, streak)
        prev_date = date_obj
    current = 0
    check_date = today
    counts_by_date = {cell["date"]: cell["count"] for cell in sorted_cells}
    while True:
        count = counts_by_date.get(check_date.isoformat(), 0)
        if count > 0:
            current += 1
            check_date -= timedelta(days=1)
        else:
            break

    return {
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best_day,
        "total_contributions": total,
        "monthly_totals": dict(monthly_totals),
    }


def build_output(cells: list[dict]) -> dict:
    stats = calculate_streaks(cells)
    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "username": "AnilkumarMaripi",
        "total_contributions": stats["total_contributions"],
        "current_streak": stats["current_streak"],
        "longest_streak": stats["longest_streak"],
        "best_day": stats["best_day"],
        "monthly_totals": stats["monthly_totals"],
        "cells": cells,
    }


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    url = "https://github.com/users/AnilkumarMaripi/contributions"
    response = requests.get(url, timeout=20)
    if response.status_code != 200:
        raise SystemExit(f"GitHub returned {response.status_code} when fetching contributions page.")

    cells = parse_contribution_cells(response.text)
    if not cells:
        raise SystemExit("Unable to parse GitHub contribution cells. The page structure may have changed.")

    data = build_output(cells)
    output_path = repo_root / "data" / "contributions.json"
    output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Saved contribution data to: {output_path}")


if __name__ == "__main__":
    main()
