import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"


def run_script(script_name: str, args: list[str] | None = None) -> None:
    args = args or []
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")

    command = [sys.executable, str(script_path), *args]
    print("Running:", " ".join(command))
    subprocess.run(command, check=True)


def main() -> None:
    print("Generating profile README assets...")
    source_photo = REPO_ROOT / "source-photo.jpg"
    fallback_photo = REPO_ROOT / "PHOTO.jpg"

    if source_photo.exists() or fallback_photo.exists():
        run_script("prep_photo.py")
        run_script("make_ascii_svg.py")
    else:
        print("Note: source-photo.jpg not found. Skipping portrait generation.")

    run_script("make_info_card.py")
    run_script("fetch_contributions.py")
    run_script("render_heatmap_svg.py")

    print("\nAll profile README assets generated successfully!")


if __name__ == "__main__":
    main()
