import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

CELL_SIZE = 12
CELL_GAP = 3
STEP = CELL_SIZE + CELL_GAP
MARGIN_X = 40
MARGIN_Y = 55
WEEKS_COUNT = 53

SVG_WIDTH = MARGIN_X * 2 + WEEKS_COUNT * STEP  # 865px
SVG_HEIGHT = MARGIN_Y + 7 * STEP + 105          # 265px

FONT_FAMILY = "Consolas, 'Courier New', Courier, monospace"


def map_level(count: int, level_str: str | None = None) -> int:
    if level_str is not None and str(level_str).isdigit():
        lvl = int(level_str)
        return max(0, min(len(COLORS) - 1, lvl))
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


def get_weekday_index(dt: datetime) -> int:
    # 0 = Sunday, 1 = Monday, ..., 6 = Saturday
    return (dt.weekday() + 1) % 7


def build_positioned_cells(cells: list[dict]) -> list[dict]:
    parsed = []
    for c in cells:
        try:
            dt = datetime.strptime(c["date"], "%Y-%m-%d")
            parsed.append({
                "cell": c,
                "dt": dt
            })
        except ValueError:
            continue

    if not parsed:
        return []

    parsed.sort(key=lambda item: item["dt"])
    first_dt = parsed[0]["dt"]
    # Align to nearest preceding Sunday
    start_sunday = first_dt - timedelta(days=get_weekday_index(first_dt))

    result = []
    for item in parsed:
        dt = item["dt"]
        week_idx = (dt - start_sunday).days // 7
        day_idx = get_weekday_index(dt)
        result.append({
            "cell": item["cell"],
            "week": week_idx,
            "day": day_idx,
            "date_str": item["cell"]["date"],
            "count": item["cell"].get("count", 0),
            "level": item["cell"].get("level")
        })
    return result


def render_heatmap_svg(data: dict, output_path: Path) -> None:
    cells_data = data.get("cells", [])
    positioned = build_positioned_cells(cells_data)

    if not positioned:
        print("ERROR: No contribution cells found to render.")
        sys.exit(1)

    max_week = max(p["week"] for p in positioned)
    actual_width = MARGIN_X * 2 + (max_week + 1) * STEP

    total = data.get("total_contributions", 0)
    current_streak = data.get("current_streak", 0)
    longest_streak = data.get("longest_streak", 0)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{actual_width}" height="{SVG_HEIGHT}" viewBox="0 0 {actual_width} {SVG_HEIGHT}">',
        '  <style>',
        f'    .bg {{ fill: #01080f; }}',
        f'    .card {{ fill: #0b1220; stroke: #1d2d44; stroke-width: 1.5px; rx: 14px; }}',
        f'    .hdr {{ font-family: {FONT_FAMILY}; font-size: 14px; fill: #7dd0fc; font-weight: bold; white-space: pre; }}',
        f'    .txt {{ font-family: {FONT_FAMILY}; font-size: 12px; fill: #c5d1ec; }}',
        f'    .lbl {{ font-family: {FONT_FAMILY}; font-size: 11px; fill: #657b9d; }}',
        '  </style>',
        f'  <rect width="100%" height="100%" class="bg" />',
        f'  <rect x="8" y="8" width="{actual_width - 16}" height="{SVG_HEIGHT - 16}" class="card" />',
        
        '  <!-- Header -->',
        f'  <text x="{MARGIN_X}" y="35" class="hdr">anil@github ~ $ ./contributions.sh</text>',

        '  <!-- Contribution Grid -->',
        '  <g>',
    ]

    # Staggered diagonal animation
    for p in positioned:
        x = MARGIN_X + p["week"] * STEP
        y = MARGIN_Y + p["day"] * STEP
        color_idx = map_level(p["count"], p["level"])
        fill_color = COLORS[color_idx]
        delay = round((p["week"] + p["day"]) * 0.012, 3)

        svg.append(f'    <rect x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" rx="3" fill="{fill_color}" opacity="0">')
        svg.append(f'      <animate attributeName="opacity" from="0" to="1" dur="0.25s" begin="{delay}s" fill="freeze" />')
        svg.append(f'    </rect>')

    svg.append('  </g>')

    # Legend & Statistics Footer
    legend_y = MARGIN_Y + 7 * STEP + 28
    svg.append(f'  <text x="{MARGIN_X}" y="{legend_y}" class="lbl">Less</text>')

    for idx, col in enumerate(COLORS):
        lx = MARGIN_X + 35 + idx * STEP
        ly = legend_y - 10
        svg.append(f'  <rect x="{lx}" y="{ly}" width="{CELL_SIZE}" height="{CELL_SIZE}" rx="3" fill="{col}" />')

    svg.append(f'  <text x="{MARGIN_X + 35 + len(COLORS) * STEP + 8}" y="{legend_y}" class="lbl">More</text>')

    # Real statistics
    stat_line_1 = f"{total} contributions in the last year"
    stat_line_2 = f"Current streak: {current_streak} days  |  Longest streak: {longest_streak} days"

    svg.append(f'  <text x="{actual_width - MARGIN_X}" y="{legend_y}" class="txt" text-anchor="end">{stat_line_1}</text>')
    svg.append(f'  <text x="{actual_width - MARGIN_X}" y="{legend_y + 20}" class="txt" text-anchor="end">{stat_line_2}</text>')

    svg.append('</svg>')

    output_path.write_text("\n".join(svg), encoding="utf-8")
    print(f"Saved contribution heatmap SVG to: {output_path}")


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    input_path = repo_root / "data" / "contributions.json"
    output_path = repo_root / "contrib-heatmap.svg"

    if not input_path.exists():
        print(f"ERROR: Contribution data not found at '{input_path}'. Run 'python scripts/fetch_contributions.py' first.")
        sys.exit(1)

    data = json.loads(input_path.read_text(encoding="utf-8"))
    render_heatmap_svg(data, output_path)


if __name__ == "__main__":
    main()
