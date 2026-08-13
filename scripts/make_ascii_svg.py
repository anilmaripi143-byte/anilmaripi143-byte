import html
from pathlib import Path
from PIL import Image

DENSITY = " .`:-=+*cs#%@"
SVG_WIDTH = 760
SVG_LINE_HEIGHT = 14
SVG_FONT_SIZE = 11
CHAR_WIDTH_PX = 7.15  # Monospace char width (11px font + 0.5px letter-spacing)
FONT_FAMILY = "Consolas, 'Courier New', Courier, monospace"


def brightness_to_char(value: int) -> str:
    # Bright pixels (255) = sparse characters (index 0: ' ')
    # Dark pixels (0) = dense characters (index -1: '@')
    normalized = max(0.0, min(1.0, value / 255.0))
    inverted = 1.0 - normalized
    index = int(inverted * (len(DENSITY) - 1))
    return DENSITY[index]


def build_ascii_lines(image: Image.Image, target_width: int = 90) -> list[str]:
    w, h = image.size
    # Calculate rows maintaining true aspect ratio (char height ~1.9x char width)
    target_height = int(round(target_width * (h / w) * 0.52))
    target_height = max(35, min(target_height, 70))

    resized = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
    pixels = resized.load()
    lines = []
    for y in range(target_height):
        row_chars = [brightness_to_char(pixels[x, y]) for x in range(target_width)]
        lines.append("".join(row_chars))
    return lines


def render_svg(lines: list[str], output_path: Path) -> None:
    rows = len(lines)
    cols = max(len(line) for line in lines)
    canvas_height = rows * SVG_LINE_HEIGHT + 40

    # Calculate exact horizontal centering offset inside 760px canvas
    text_block_width = cols * CHAR_WIDTH_PX
    start_x = max(18, int(round((SVG_WIDTH - text_block_width) / 2)))
    end_x = start_x + int(round(text_block_width))

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" height="{canvas_height}" viewBox="0 0 {SVG_WIDTH} {canvas_height}">',
        '  <style>',
        f'    .card {{ fill: #0b1220; stroke: #1d2d44; stroke-width: 1.5px; rx: 14px; }}',
        f'    .ascii-text {{ font-family: {FONT_FAMILY}; font-size: {SVG_FONT_SIZE}px; fill: #d8e2fd; letter-spacing: 0.5px; white-space: pre; }}',
        '  </style>',
        f'  <rect width="100%" height="100%" fill="#01080f" />',
        f'  <rect x="8" y="8" width="{SVG_WIDTH - 16}" height="{canvas_height - 16}" class="card" />',
        f'  <g class="ascii-text">',
    ]

    row_delay = 0.045
    typing_dur = 0.35

    for row_idx, line in enumerate(lines):
        escaped_line = html.escape(line)
        y = 28 + row_idx * SVG_LINE_HEIGHT
        clip_id = f"row-clip-{row_idx}"
        begin_sec = round(row_idx * row_delay, 3)

        svg.append(f'    <clipPath id="{clip_id}">')
        svg.append(f'      <rect x="{start_x - 2}" y="{y - SVG_LINE_HEIGHT + 3}" width="0" height="{SVG_LINE_HEIGHT + 2}">')
        svg.append(f'        <animate attributeName="width" from="0" to="{end_x - start_x + 4}" dur="{typing_dur}s" begin="{begin_sec}s" fill="freeze" />')
        svg.append(f'      </rect>')
        svg.append(f'    </clipPath>')

        svg.append(f'    <text x="{start_x}" y="{y}" clip-path="url(#{clip_id})">{escaped_line}</text>')

        # Centered Typewriter Cursor
        svg.append(f'    <rect x="{start_x}" y="{y - SVG_LINE_HEIGHT + 4}" width="7" height="11" fill="#7dd0fc" opacity="0">')
        svg.append(f'      <animate attributeName="opacity" values="0;0.8;0.8;0" keyTimes="0;0.05;0.9;1" dur="{typing_dur}s" begin="{begin_sec}s" fill="freeze" />')
        svg.append(f'      <animate attributeName="x" from="{start_x}" to="{end_x}" dur="{typing_dur}s" begin="{begin_sec}s" fill="freeze" />')
        svg.append(f'    </rect>')

    svg.append('  </g>')
    svg.append('</svg>')

    output_path.write_text("\n".join(svg), encoding="utf-8")
    print(f"Saved centered ASCII portrait SVG to: {output_path}")


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
        lines = build_ascii_lines(img_gray, target_width=90)

    render_svg(lines, output_path)


if __name__ == "__main__":
    main()
