import html
import os
from pathlib import Path

# Easy to edit information structure
HEADER_USER = "anil@github"
HEADER_CMD = "~ $ neofetch --profile"

INFO_LINES = [
    ("OS", "Windows 10/11 / Linux (WSL)"),
    ("Host", "KL University (AI & Data Science)"),
    ("User", "Anil Kumar (@AnilkumarMaripi)"),
    ("Role", "AI & Data Science Student"),
    ("Languages", "Python, Java, C, JavaScript"),
    ("Learning", "Machine Learning, DSA, OS, Embedded Systems"),
    ("Tools", "Git, GitHub, VS Code, Linux"),
    ("Projects", "DevGram, AI/ML Projects, Web Apps"),
]

SVG_WIDTH = 540
SVG_HEIGHT = 380
BACKGROUND = "#01080f"
CARD_BG = "#0b1220"
CARD_BORDER = "#1d2d44"
TEXT_COLOR = "#c5d1ec"
ACCENT_GREEN = "#39d353"
ACCENT_BLUE = "#7dd0fc"
ACCENT_MUTED = "#577093"
FONT_FAMILY = "Consolas, 'Courier New', Courier, monospace"


def build_info_card_svg(output_path: Path, animated: bool = True) -> None:
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" height="{SVG_HEIGHT}" viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}">',
        '  <style>',
        f'    .card {{ fill: {CARD_BG}; stroke: {CARD_BORDER}; stroke-width: 1.5px; rx: 14px; }}',
        f'    .dot-red {{ fill: #ff5f56; }} .dot-yellow {{ fill: #ffbd2e; }} .dot-green {{ fill: #27c93f; }}',
        f'    .text-base {{ font-family: {FONT_FAMILY}; font-size: 13px; fill: {TEXT_COLOR}; white-space: pre; }}',
        f'    .accent-hdr {{ fill: {ACCENT_GREEN}; font-weight: bold; }}',
        f'    .accent-lbl {{ fill: {ACCENT_BLUE}; font-weight: bold; }}',
        f'    .separator {{ stroke: {ACCENT_MUTED}; stroke-width: 1px; stroke-dasharray: 4 4; }}',
        '  </style>',
        f'  <rect width="100%" height="100%" fill="{BACKGROUND}" />',
        f'  <rect x="8" y="8" width="{SVG_WIDTH - 16}" height="{SVG_HEIGHT - 16}" class="card" />',
        '  <!-- Window Title Bar Buttons -->',
        '  <circle cx="28" cy="26" r="6" class="dot-red" />',
        '  <circle cx="48" cy="26" r="6" class="dot-yellow" />',
        '  <circle cx="68" cy="26" r="6" class="dot-green" />',
    ]

    all_display_lines = []
    # Line 0: Header prompt line
    all_display_lines.append(('header', f'<tspan class="accent-hdr">{html.escape(HEADER_USER)}</tspan> <tspan fill="{TEXT_COLOR}">{html.escape(HEADER_CMD)}</tspan>'))
    # Line 1: Separator line
    all_display_lines.append(('separator', '-' * 46))

    # Next lines: key-value pairs
    for label, val in INFO_LINES:
        lbl_str = f"{label:<10}: "
        line_content = f'<tspan class="accent-lbl">{html.escape(lbl_str)}</tspan><tspan fill="{TEXT_COLOR}">{html.escape(val)}</tspan>'
        all_display_lines.append(('kv', line_content))

    start_y = 62
    line_height = 28

    svg.append(f'  <g class="text-base">')

    for idx, (kind, content) in enumerate(all_display_lines):
        y = start_y + idx * line_height
        delay = round(0.15 + idx * 0.10, 3)

        if kind == 'separator':
            if animated:
                svg.append(f'    <line x1="28" y1="{y - 8}" x2="{SVG_WIDTH - 28}" y2="{y - 8}" class="separator" opacity="0">')
                svg.append(f'      <animate attributeName="opacity" from="0" to="0.6" dur="0.3s" begin="{delay}s" fill="freeze" />')
                svg.append(f'    </line>')
            else:
                svg.append(f'    <line x1="28" y1="{y - 8}" x2="{SVG_WIDTH - 28}" y2="{y - 8}" class="separator" opacity="0.6" />')
        else:
            if animated:
                svg.append(f'    <g transform="translate(-16, 0)" opacity="0">')
                svg.append(f'      <animate attributeName="opacity" from="0" to="1" dur="0.35s" begin="{delay}s" fill="freeze" />')
                svg.append(f'      <animate attributeName="transform" from="translate(-16, 0)" to="translate(0, 0)" dur="0.35s" begin="{delay}s" fill="freeze" />')
                svg.append(f'      <text x="28" y="{y}">{content}</text>')
                svg.append(f'    </g>')
            else:
                svg.append(f'    <text x="28" y="{y}">{content}</text>')

    svg.append('  </g>')
    svg.append('</svg>')

    output_path.write_text("\n".join(svg), encoding="utf-8")
    print(f"Saved info card SVG (animated={animated}) to: {output_path}")


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    output_path = repo_root / "info-card.svg"
    is_static = os.getenv("STATIC", "0").strip() == "1"
    build_info_card_svg(output_path, animated=not is_static)


if __name__ == "__main__":
    main()
