import sys
from pathlib import Path
from PIL import Image
import numpy as np
import cv2
from rembg import remove


def prep_photo(input_path: Path, output_path: Path) -> None:
    if not input_path.exists():
        repo_root = input_path.parent
        fallback_photo = repo_root / "PHOTO.jpg"
        if fallback_photo.exists():
            input_path = fallback_photo
        else:
            raise FileNotFoundError(
                f"Photo file not found at '{input_path}'. "
                "Please place your real photo as 'source-photo.jpg' in the repository root."
            )

    print(f"Loading photo from: {input_path}")
    with Image.open(input_path) as source:
        source = source.convert("RGBA")
        print("Removing background with rembg...")
        transparent = remove(source)

        # Crop to subject bounding box (full head, neck & shoulders)
        bbox = transparent.getbbox()
        if bbox:
            transparent = transparent.crop(bbox)

        # Composite over solid white background
        white_bg = Image.new("RGBA", transparent.size, (255, 255, 255, 255))
        composite = Image.alpha_composite(white_bg, transparent)
        gray = composite.convert("L")

        # Apply OpenCV CLAHE contrast enhancement for clear features
        image_np = np.asarray(gray).astype(np.uint8)
        clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))
        image_np = clahe.apply(image_np)

        # Contrast stretch
        p3, p97 = np.percentile(image_np, (3, 97))
        if p97 > p3:
            image_np = np.clip((image_np - p3) * 255.0 / (p97 - p3), 0, 255)

        output = Image.fromarray(image_np.astype(np.uint8))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output.save(output_path)

    print(f"Saved prepped photo to: {output_path}")


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    input_path = repo_root / "source-photo.jpg"
    output_path = repo_root / "source-prepped.png"

    if len(sys.argv) > 1:
        input_path = Path(sys.argv[1])

    try:
        prep_photo(input_path, output_path)
    except Exception as exc:
        print(f"Error preparing photo: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
