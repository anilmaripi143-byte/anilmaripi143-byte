import argparse
from pathlib import Path
from PIL import Image
import numpy as np
from rembg import remove


def prep_photo(input_path: Path, output_path: Path) -> None:
    if not input_path.exists():
        raise FileNotFoundError(f"Input photo not found: {input_path}")

    with Image.open(input_path) as source:
        source = source.convert("RGBA")
        transparent = remove(source)
        result = Image.new("RGBA", transparent.size, (255, 255, 255, 255))
        result.alpha_composite(transparent)
        result = result.convert("RGB")
        gray = result.convert("L")

        image_np = np.asarray(gray).astype(np.float32)
        p2, p98 = np.percentile(image_np, (2, 98))
        if p98 > p2:
            image_np = np.clip((image_np - p2) * 255.0 / (p98 - p2), 0, 255)
        output = Image.fromarray(image_np.astype(np.uint8))
        output.save(output_path)

    print(f"Saved prepped image to: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a photo for ASCII portrait generation.")
    parser.add_argument("photo", type=Path, help="Path to the source photo file.")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    output_path = repo_root / "source-prepped.png"

    try:
        prep_photo(args.photo, output_path)
    except Exception as exc:
        print(f"Error preparing photo: {exc}")
        raise


if __name__ == "__main__":
    main()
