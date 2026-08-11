import math
from pathlib import Path
from PIL import Image

DENSITY = " .`:-=+*cs#%@"
SVG_WIDTH = 760
SVG_LINE_HEIGHT = 14
SVG_FONT_SIZE = 12
FONT_FAMILY = "Courier New, Courier, monospace"


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))


def brightness_to_char(value: int) -> str:
    ramp_length = len(DENSITY)
    index = int((value / 255) * (ramp_length - 1))
    return DENSITY[index]


def build_ascii_lines(image: Image.Image, width: int = 100) -> list[str]:
    aspect_ratio = image.height / image.width
    height = int(round(width * aspect_ratio * 0.55))
    height = max(20, min(height, 60))
    resized = image.resize((width, height), Image.BICUBIC)
    pixels = resized.load()
    lines = []
    for y in range(height):
        row_chars = [brightness_to_char(pixels[x, y]) for x in range(width)]
        lines.append("".join(row_chars))
    return lines


def render_svg(lines: list[str], output_path: Path) -> None:
    rows = len(lines)
    cols = max(len(line) for line in lines)
    canvas_height = rows * SVG_LINE_HEIGHT + 40
    svg_lines = [
        f"<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{SVG_WIDTH}\" height=\"{canvas_height}\" viewBox=\"0 0 {SVG_WIDTH} {canvas_height}\">",
        "  <rect width=\"100%\" height=\"100%\" fill=\"#0B111B\" />",
        "  <g font-family=\"Courier New, Courier, monospace\" font-size=\"12\" fill=\"#c0c5ce\" letter-spacing=\"0.5\">",
    ]

    for row_index, line in enumerate(lines):
        y = 25 + row_index * SVG_LINE_HEIGHT
        clip_id = f"clip-row-{row_index}"
        delay = row_index * 0.05
        svg_lines.append(
            f"    <clipPath id=\"{clip_id}\"><rect x=\"0\" y=\"{y - SVG_LINE_HEIGHT + 2}\" width=\"0\" height=\"{SVG_LINE_HEIGHT + 2}\">"
        )
        svg_lines.append(
            f"      <animate attributeName=\"width\" from=\"0\" to=\"{SVG_WIDTH - 40}\" dur=\"0.6s\" begin=\"{delay}s\" fill=\"freeze\" />"
        )
        svg_lines.append("    </rect></clipPath>")
        svg_lines.append(
            f"    <text x=\"20\" y=\"{y}\" clip-path=\"url(#{clip_id})\">{line}</text>"
        )
        svg_lines.append(
            f"    <rect x=\"20\" y=\"{y - SVG_LINE_HEIGHT + 4}\" width=\"8\" height=\"10\" fill=\"#c0c5ce\" opacity=\"0.55\">"
        )
        svg_lines.append(
            f"      <animate attributeName=\"x\" from=\"20\" to=\"{SVG_WIDTH - 40}\" dur=\"0.6s\" begin=\"{delay}s\" fill=\"freeze\" />"
        )
        svg_lines.append(
            f"      <animate attributeName=\"opacity\" values=\"0.55;0;0\" dur=\"0.6s\" begin=\"{delay}s\" fill=\"freeze\" />"
        )
        svg_lines.append("    </rect>")

    svg_lines.append("  </g>")
    svg_lines.append("</svg>")
    output_path.write_text("\n".join(svg_lines), encoding="utf-8")
    print(f"Saved ASCII portrait SVG to: {output_path}")


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    input_path = repo_root / "source-prepped.png"
    output_path = repo_root / "ascii-portrait.svg"

    if not input_path.exists():
        raise FileNotFoundError(
            f"Prepped photo not found: {input_path}. Run python scripts/prep_photo.py PHOTO.jpg"
        )

    image = Image.open(input_path).convert("L")
    lines = build_ascii_lines(image, width=100)
    render_svg(lines, output_path)


if __name__ == "__main__":
    main()
