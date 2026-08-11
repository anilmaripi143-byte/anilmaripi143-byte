import json
from datetime import datetime, timedelta
from pathlib import Path

COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
SVG_CELL = 12
SVG_GAP = 3
SVG_MARGIN_X = 30
SVG_MARGIN_Y = 30
SVG_WEEKS = 53
SVG_WIDTH = SVG_MARGIN_X * 2 + SVG_WEEKS * (SVG_CELL + SVG_GAP)
SVG_HEIGHT = SVG_MARGIN_Y * 2 + 7 * (SVG_CELL + SVG_GAP) + 120
FONT_FAMILY = "Courier New, Courier, monospace"


def map_level(count: int, level: str | None) -> int:
    if level and level.isdigit():
        index = int(level)
        return clamp(index, 0, len(COLORS) - 1)
    if count <= 0:
        return 0
    if count < 2:
        return 1
    if count < 4:
        return 2
    if count < 8:
        return 3
    if count < 15:
        return 4
    return 5


def clamp(value: int, min_value: int, max_value: int) -> int:
    return max(min_value, min(value, max_value))


def weekday_index(date_obj: datetime) -> int:
    return (date_obj.weekday() + 1) % 7


def build_positions(cells: list[dict]) -> list[tuple[dict, int, int, float]]:
    parsed = []
    for cell in cells:
        try:
            date_obj = datetime.strptime(cell["date"], "%Y-%m-%d")
        except ValueError:
            continue
        parsed.append((cell, date_obj))
    if not parsed:
        return []

    parsed.sort(key=lambda item: item[1])
    start_date = parsed[0][1]
    start_sunday = start_date - timedelta(days=weekday_index(start_date))

    positioned = []
    for cell, date_obj in parsed:
        week = (date_obj - start_sunday).days // 7
        day = weekday_index(date_obj)
        positioned.append((cell, week, day, date_obj.timestamp()))
    return positioned


def build_svg(data: dict, output_path: Path) -> None:
    positions = build_positions(data.get("cells", []))
    if not positions:
        raise ValueError("No contribution cells available to render.")

    max_week = max(week for _, week, _, _ in positions)
    width = SVG_MARGIN_X * 2 + (max_week + 1) * (SVG_CELL + SVG_GAP)
    svg = [
        f"<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{width}\" height=\"{SVG_HEIGHT}\" viewBox=\"0 0 {width} {SVG_HEIGHT}\">",
        "  <rect width=\"100%\" height=\"100%\" fill=\"#0b1019\" />",
        f"  <text x=\"{SVG_MARGIN_X}\" y=\"20\" font-family=\"{FONT_FAMILY}\" font-size=\"16\" fill=\"#9cc4ff\">Contribution heatmap</text>",
    ]

    for cell, week, day, _ in positions:
        x = SVG_MARGIN_X + week * (SVG_CELL + SVG_GAP)
        y = SVG_MARGIN_Y + day * (SVG_CELL + SVG_GAP)
        level_index = map_level(cell["count"], cell.get("level"))
        fill = COLORS[level_index]
        delay = 0.02 * (week + day)
        svg.append(
            f"  <rect x=\"{x}\" y=\"{y}\" width=\"{SVG_CELL}\" height=\"{SVG_CELL}\" rx=\"3\" fill=\"{fill}\" opacity=\"0\">"
        )
        svg.append(
            f"    <animate attributeName=\"opacity\" from=\"0\" to=\"1\" dur=\"0.25s\" begin=\"{delay}s\" fill=\"freeze\" />"
        )
        svg.append("  </rect>")

    legend_x = SVG_MARGIN_X
    legend_y = SVG_MARGIN_Y + 7 * (SVG_CELL + SVG_GAP) + 45
    svg.append(f"  <text x=\"{legend_x}\" y=\"{legend_y - 16}\" font-family=\"{FONT_FAMILY}\" font-size=\"13\" fill=\"#c0c9d9\">Less</text>")
    for index, color in enumerate(COLORS):
        x = legend_x + 40 + index * (SVG_CELL + SVG_GAP)
        svg.append(
            f"  <rect x=\"{x}\" y=\"{legend_y - 12}\" width=\"{SVG_CELL}\" height=\"{SVG_CELL}\" rx=\"3\" fill=\"{color}\" />"
        )
    svg.append(f"  <text x=\"{legend_x + 40 + len(COLORS) * (SVG_CELL + SVG_GAP)}\" y=\"{legend_y}\" font-family=\"{FONT_FAMILY}\" font-size=\"13\" fill=\"#c0c9d9\">More</text>")

    footer_y = legend_y + 38
    total = data.get("total_contributions", 0)
    current_streak = data.get("current_streak", 0)
    longest_streak = data.get("longest_streak", 0)
    svg.append(f"  <text x=\"{SVG_MARGIN_X}\" y=\"{footer_y}\" font-family=\"{FONT_FAMILY}\" font-size=\"13\" fill=\"#c0c9d9\">{total} contributions in the last year</text>")
    svg.append(f"  <text x=\"{SVG_MARGIN_X + 280}\" y=\"{footer_y}\" font-family=\"{FONT_FAMILY}\" font-size=\"13\" fill=\"#c0c9d9\">Current streak: {current_streak} days</text>")
    svg.append(f"  <text x=\"{SVG_MARGIN_X + 280}\" y=\"{footer_y + 18}\" font-family=\"{FONT_FAMILY}\" font-size=\"13\" fill=\"#c0c9d9\">Longest streak: {longest_streak} days</text>")
    svg.append("</svg>")

    output_path.write_text("\n".join(svg), encoding="utf-8")
    print(f"Saved contribution heatmap SVG to: {output_path}")


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    input_path = repo_root / "data" / "contributions.json"
    if not input_path.exists():
        raise FileNotFoundError(f"Contribution data not found: {input_path}. Run python scripts/fetch_contributions.py")

    data = json.loads(input_path.read_text(encoding="utf-8"))
    output_path = repo_root / "contrib-heatmap.svg"
    build_svg(data, output_path)


if __name__ == "__main__":
    main()
