from pathlib import Path
from PIL import Image

ORANGE = (255, 132, 0, 255)         # THWS Brand Color

# wherever the mask is white, show oragnge; elsewhere show the photo
def compose(bg: Image.Image, mask: Image.Image) -> Image.Image:
    orange = Image.new("RGBA", bg.size, ORANGE)         # new image filled with the THWS orange
    return Image.composite(orange, bg, mask)        # blends the two together with the mask,
                                                    # where the mask is white -> show the first image (THWS orange)
                                                    # where the mask is black -> show the second image (background)
                                                    # where the mask is gray -> blend the two proportionally

# returns a path object pointing to the saved file
def save_output(result: Image.Image, output_path: str) -> Path:
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    result.save(out_path)
    return out_path
