import os
from pathlib import Path

INFO_LINES = [
    "Anil Kumar",
    "@AnilkumarMaripi",
    "",
    "Role: AI & Data Science Student",
    "",
    "Languages: Python | Java | C | JavaScript",
    "Learning: Machine Learning | Data Structures & Algorithms | Operating Systems | Embedded Systems",
    "Projects: DevGram | AI/ML Projects | Web Development",
    "Tools: Git | GitHub | VS Code | Linux | Docker",
]

SVG_WIDTH = 520
SVG_HEIGHT = 360
BACKGROUND = "#01080f"
CARD_FILL = "#0b1220"
TEXT_COLOR = "#cbd6ee"
ACCENT = "#7dd0fc"
FONT_FAMILY = "Courier New, Courier, monospace"
LINE_SPACING = 26
PADDING_X = 24
PADDING_Y = 30


def create_svg(lines: list[str], output_path: Path, animated: bool = True) -> None:
    svg = [
        f"<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{SVG_WIDTH}\" height=\"{SVG_HEIGHT}\" viewBox=\"0 0 {SVG_WIDTH} {SVG_HEIGHT}\">",
        f"  <rect width=\"100%\" height=\"100%\" fill=\"{BACKGROUND}\" />",
        f"  <rect x=\"8\" y=\"8\" width=\"{SVG_WIDTH - 16}\" height=\"{SVG_HEIGHT - 16}\" rx=\"18\" fill=\"{CARD_FILL}\" stroke=\"#2d4a69\" stroke-width=\"2\" />",
        f"  <g font-family=\"{FONT_FAMILY}\" font-size=\"15\" fill=\"{TEXT_COLOR}\">",
    ]

    for index, line in enumerate(lines):
        y = PADDING_Y + index * LINE_SPACING
        if animated:
            delay = 0.2 + index * 0.12
            svg.append(
                f"    <text x=\"{PADDING_X}\" y=\"{y}\" fill=\"{ACCENT if index < 2 else TEXT_COLOR}\" opacity=\"0\" transform=\"translate(-16,0)\">{line}"
            )
            svg.append(
                f"      <animate attributeName=\"opacity\" from=\"0\" to=\"1\" dur=\"0.35s\" begin=\"{delay}s\" fill=\"freeze\" />"
            )
            svg.append(
                f"      <animate attributeName=\"transform\" from=\"translate(-16,0)\" to=\"translate(0,0)\" dur=\"0.35s\" begin=\"{delay}s\" fill=\"freeze\" />"
            )
            svg.append("    </text>")
        else:
            svg.append(f"    <text x=\"{PADDING_X}\" y=\"{y}\" fill=\"{ACCENT if index < 2 else TEXT_COLOR}\">{line}</text>")

    svg.append("  </g>")
    svg.append("</svg>")
    output_path.write_text("\n".join(svg), encoding="utf-8")
    print(f"Saved info card SVG to: {output_path}")


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    output_path = repo_root / "info-card.svg"
    static_mode = os.getenv("STATIC", "0") == "1"
    create_svg(INFO_LINES, output_path, animated=not static_mode)


if __name__ == "__main__":
    main()
