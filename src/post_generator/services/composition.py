from pathlib import Path
from PIL import Image

ORANGE = (255, 132, 0, 255)         # THWS Brand Color (#FF8400)

# takes a background photo and a mask, then overlays the given color wherever the mask dictates
def compose(bg: Image.Image, mask: Image.Image, color: str | tuple | None = None) -> Image.Image:
    fill = color if color is not None else ORANGE   # fall back to the THWS orange when no color is passed
    layer = Image.new("RGBA", bg.size, fill)        # new image filled with the overlay color
    return Image.composite(layer, bg, mask)         # blends the two together with the mask,
                                                    # where the mask is white -> show the first image (overlay color)
                                                    # where the mask is black -> show the second image (background)
                                                    # where the mask is gray -> blend the two proportionally

# saves the PIL image to the disk | creates any missing parent directories, saves the image to the gegebene out_path and returns it as a Path object
def save_output(result: Image.Image, output_path: str) -> Path:
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    result.save(out_path)
    return out_path
