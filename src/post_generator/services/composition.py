from pathlib import Path
from PIL import Image

ORANGE = (255, 132, 0, 255)         # THWS Brand Color

# wherever the mask is white, show oragnge; elsewhere show the photo
def compose(bg: Image.Image, mask: Image.Image) -> Image.Image:
    orange = Image.new("RGBA", bg.size, ORANGE)
    return Image.composite(orange, bg, mask)


def save_output(result: Image.Image, output_path: str) -> Path:
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    result.save(out_path)
    return out_path
