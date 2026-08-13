import html
from pathlib import Path
from PIL import Image

DENSITY = " .`:-=+*cs#%@"
SVG_WIDTH = 540
SVG_HEIGHT = 410
SVG_LINE_HEIGHT = 10.2
SVG_FONT_SIZE = 9.5
FONT_FAMILY = "Consolas, 'Courier New', Courier, monospace"


def brightness_to_char(value: int) -> str:
    # Bright pixels (255) = sparse characters (index 0: ' ')
    # Dark pixels (0) = dense characters (index -1: '@')
    normalized = max(0.0, min(1.0, value / 255.0))
    inverted = 1.0 - normalized
    index = int(inverted * (len(DENSITY) - 1))
    return DENSITY[index]


def build_ascii_lines(image: Image.Image, target_width: int = 70) -> list[str]:
    w, h = image.size
    # Calculate rows to maintain natural human aspect ratio without distortion
    target_height = int(round(target_width * (h / w) * 0.52))
    target_height = max(30, min(target_height, 36))

    resized = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
    pixels = resized.load()
    lines = []
    for y in range(target_height):
        row_chars = [brightness_to_char(pixels[x, y]) for x in range(target_width)]
        lines.append("".join(row_chars))
    return lines


def render_svg(lines: list[str], output_path: Path) -> None:
    rows = len(lines)
    
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" height="{SVG_HEIGHT}" viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}">',
        '  <style>',
        f'    .card {{ fill: #0b1220; stroke: #1d2d44; stroke-width: 1.5px; rx: 14px; }}',
        f'    .dot-red {{ fill: #ff5f56; }} .dot-yellow {{ fill: #ffbd2e; }} .dot-green {{ fill: #27c93f; }}',
        f'    .ascii-text {{ font-family: {FONT_FAMILY}; font-size: {SVG_FONT_SIZE}px; fill: #d8e2fd; letter-spacing: 0.4px; white-space: pre; }}',
        '  </style>',
        f'  <rect width="100%" height="100%" fill="#01080f" />',
        f'  <rect x="8" y="8" width="{SVG_WIDTH - 16}" height="{SVG_HEIGHT - 16}" class="card" />',
        '  <!-- Window Title Bar Buttons -->',
        '  <circle cx="28" cy="24" r="6" class="dot-red" />',
        '  <circle cx="48" cy="24" r="6" class="dot-yellow" />',
        '  <circle cx="68" cy="24" r="6" class="dot-green" />',
        f'  <g class="ascii-text">',
    ]

    start_y = 44
    row_delay = 0.04
    typing_dur = 0.32

    for row_idx, line in enumerate(lines):
        escaped_line = html.escape(line)
        y = round(start_y + row_idx * SVG_LINE_HEIGHT, 1)
        clip_id = f"row-clip-{row_idx}"
        begin_sec = round(row_idx * row_delay, 3)

        # Reveal clip path expanding across the card width
        svg.append(f'    <clipPath id="{clip_id}">')
        svg.append(f'      <rect x="16" y="{y - SVG_LINE_HEIGHT + 2}" width="0" height="{SVG_LINE_HEIGHT + 2}">')
        svg.append(f'        <animate attributeName="width" from="0" to="{SVG_WIDTH - 32}" dur="{typing_dur}s" begin="{begin_sec}s" fill="freeze" />')
        svg.append(f'      </rect>')
        svg.append(f'    </clipPath>')

        # Native SVG text-anchor="middle" x="50%" for guaranteed 100% horizontal centering
        svg.append(f'    <text x="50%" y="{y}" text-anchor="middle" clip-path="url(#{clip_id})">{escaped_line}</text>')

        # Centered typewriter cursor
        svg.append(f'    <rect x="18" y="{y - SVG_LINE_HEIGHT + 3}" width="6" height="9" fill="#7dd0fc" opacity="0">')
        svg.append(f'      <animate attributeName="opacity" values="0;0.8;0.8;0" keyTimes="0;0.05;0.9;1" dur="{typing_dur}s" begin="{begin_sec}s" fill="freeze" />')
        svg.append(f'      <animate attributeName="x" from="18" to="{SVG_WIDTH - 24}" dur="{typing_dur}s" begin="{begin_sec}s" fill="freeze" />')
        svg.append(f'    </rect>')

    svg.append('  </g>')
    svg.append('</svg>')

    output_path.write_text("\n".join(svg), encoding="utf-8")
    print(f"Saved twin-card centered ASCII portrait SVG to: {output_path}")


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
        lines = build_ascii_lines(img_gray, target_width=70)

    render_svg(lines, output_path)


if __name__ == "__main__":
    main()
