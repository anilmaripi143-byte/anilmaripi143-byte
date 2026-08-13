import html
from pathlib import Path
from PIL import Image

DENSITY = " .`:-=+*cs#%@"
SVG_WIDTH = 760
SVG_LINE_HEIGHT = 14
SVG_FONT_SIZE = 11
FONT_FAMILY = "Consolas, 'Courier New', Courier, monospace"


def brightness_to_char(value: int) -> str:
    # Bright pixels = sparse characters (index 0: ' ')
    # Dark pixels = dense characters (index -1: '@')
    normalized = max(0.0, min(1.0, value / 255.0))
    inverted = 1.0 - normalized
    index = int(inverted * (len(DENSITY) - 1))
    return DENSITY[index]


def build_ascii_lines(image: Image.Image, target_width: int = 100, target_height: int = 53) -> list[str]:
    # Resize image to target character dimensions using BICUBIC
    resized = image.resize((target_width, target_height), Image.BICUBIC)
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
        '    .bg { fill: #0b1220; rx: 12px; }',
        '    .ascii-text { font-family: ' + FONT_FAMILY + f'; font-size: {SVG_FONT_SIZE}px; fill: #d8e2fd; letter-spacing: 0.6px; white-space: pre; }}',
        '  </style>',
        f'  <rect width="100%" height="100%" fill="#01080f" />',
        f'  <rect x="8" y="8" width="{SVG_WIDTH - 16}" height="{canvas_height - 16}" rx="14" fill="#0b1220" stroke="#1d2d44" stroke-width="1.5" />',
        f'  <g class="ascii-text">',
    ]

    # Calculate stagger delay per row for typed animation
    row_delay = 0.05  # seconds per row
    typing_dur = 0.35  # seconds duration to reveal each row

    for row_idx, line in enumerate(lines):
        escaped_line = html.escape(line)
        y = 28 + row_idx * SVG_LINE_HEIGHT
        clip_id = f"row-clip-{row_idx}"
        begin_sec = round(row_idx * row_delay, 3)

        # ClipPath reveals row from left to right
        svg.append(f'    <clipPath id="{clip_id}">')
        svg.append(f'      <rect x="18" y="{y - SVG_LINE_HEIGHT + 3}" width="0" height="{SVG_LINE_HEIGHT + 2}">')
        svg.append(f'        <animate attributeName="width" from="0" to="{SVG_WIDTH - 36}" dur="{typing_dur}s" begin="{begin_sec}s" fill="freeze" />')
        svg.append(f'      </rect>')
        svg.append(f'    </clipPath>')

        # Render ASCII text row clipped by the expanding clipPath
        svg.append(f'    <text x="20" y="{y}" clip-path="url(#{clip_id})">{escaped_line}</text>')

        # Optional typewriter cursor at leading edge
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
        lines = build_ascii_lines(img_gray, target_width=100, target_height=53)

    render_svg(lines, output_path)


if __name__ == "__main__":
    main()
