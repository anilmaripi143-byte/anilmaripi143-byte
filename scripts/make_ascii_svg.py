import html
from pathlib import Path
from PIL import Image

DENSITY = " .`:-=+*cs#%@"
SVG_WIDTH = 760
SVG_LINE_HEIGHT = 14
SVG_FONT_SIZE = 11
FONT_FAMILY = "Consolas, 'Courier New', Courier, monospace"


def brightness_to_char(value: int) -> str:
    # Bright pixels (255) = sparse characters (index 0: ' ')
    # Dark pixels (0) = dense characters (index -1: '@')
    normalized = max(0.0, min(1.0, value / 255.0))
    inverted = 1.0 - normalized
    index = int(inverted * (len(DENSITY) - 1))
    return DENSITY[index]


def build_ascii_lines(image: Image.Image, target_width: int = 84) -> list[str]:
    w, h = image.size
    # In monospace font stacks, line height is ~1.9x character width.
    # To maintain natural aspect ratio without squashing:
    target_height = int(round(target_width * (h / w) * 0.52))
    target_height = max(30, min(target_height, 65))

    resized = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
    pixels = resized.load()
    lines = []
    for y in range(target_height):
        row_chars = [brightness_to_char(pixels[x, y]) for x in range(target_width)]
        lines.append("".join(row_chars))
    return lines


def render_svg(lines: list[str], output_path: Path) -> None:
    rows = len(lines)
    canvas_height = rows * SVG_LINE_HEIGHT + 40

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" height="{canvas_height}" viewBox="0 0 {SVG_WIDTH} {canvas_height}">',
        '  <style>',
        f'    .card {{ fill: #0b1220; stroke: #1d2d44; stroke-width: 1.5px; rx: 14px; }}',
        f'    .ascii-text {{ font-family: {FONT_FAMILY}; font-size: {SVG_FONT_SIZE}px; fill: #d8e2fd; letter-spacing: 0.6px; white-space: pre; }}',
        '  </style>',
        f'  <rect width="100%" height="100%" fill="#01080f" />',
        f'  <rect x="8" y="8" width="{SVG_WIDTH - 16}" height="{canvas_height - 16}" class="card" />',
        f'  <g class="ascii-text">',
    ]

    row_delay = 0.05
    typing_dur = 0.35

    for row_idx, line in enumerate(lines):
        escaped_line = html.escape(line)
        y = 28 + row_idx * SVG_LINE_HEIGHT
        clip_id = f"row-clip-{row_idx}"
        begin_sec = round(row_idx * row_delay, 3)

        svg.append(f'    <clipPath id="{clip_id}">')
        svg.append(f'      <rect x="18" y="{y - SVG_LINE_HEIGHT + 3}" width="0" height="{SVG_LINE_HEIGHT + 2}">')
        svg.append(f'        <animate attributeName="width" from="0" to="{SVG_WIDTH - 36}" dur="{typing_dur}s" begin="{begin_sec}s" fill="freeze" />')
        svg.append(f'      </rect>')
        svg.append(f'    </clipPath>')

        svg.append(f'    <text x="20" y="{y}" clip-path="url(#{clip_id})">{escaped_line}</text>')

        # Typewriter cursor at leading edge
        svg.append(f'    <rect x="20" y="{y - SVG_LINE_HEIGHT + 4}" width="7" height="11" fill="#7dd0fc" opacity="0">')
        svg.append(f'      <animate attributeName="opacity" values="0;0.8;0.8;0" keyTimes="0;0.05;0.9;1" dur="{typing_dur}s" begin="{begin_sec}s" fill="freeze" />')
        svg.append(f'      <animate attributeName="x" from="20" to="{SVG_WIDTH - 36}" dur="{typing_dur}s" begin="{begin_sec}s" fill="freeze" />')
        svg.append(f'    </rect>')

    svg.append('  </g>')
    svg.append('</svg>')

    output_path.write_text("\n".join(svg), encoding="utf-8")
    print(f"Saved ASCII portrait SVG to: {output_path}")


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    input_path = repo_root / "source-prepped.png"
    output_path = repo_root / "ascii-portrait.svg"

    if not input_path.exists():
        raise FileNotFoundError(
            f"Prepped photo not found at '{input_path}'. "
            "Run 'python scripts/prep_photo.py' first."
        )

    with Image.open(input_path) as img:
        img_gray = img.convert("L")
        lines = build_ascii_lines(img_gray, target_width=84)

    render_svg(lines, output_path)


if __name__ == "__main__":
    main()
