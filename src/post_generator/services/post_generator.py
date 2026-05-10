from PIL import Image

from .overlay_service import (
    ALLOWED_ADD,
    ALLOWED_REMOVE,
    BASE_TEMPLATE,
    BASE_TEMPLATES,
    CELL_SIZE,
    grid_to_cells,
    grid_to_template,
    mutate_template,
    random_stair_template,
    template_to_grid,
)

INSTAGRAM_WIDTH = 1080
INSTAGRAM_HEIGHT = 1350


# Takes any image and crops it to a 4:5 aspect ratio, then resizes it to 1080x1350.
def crop_to_4_5(img: Image.Image) -> Image.Image:
    target_ratio = INSTAGRAM_WIDTH / INSTAGRAM_HEIGHT
    w, h = img.size         # current width and height of the input image
    ratio = w / h           # current aspect ratio of the input image

    if ratio > target_ratio:        # image is wider than 4:5
        new_w = int(h * target_ratio)           # new width
        left = (w - new_w) // 2                 # pixels to cut from the left side to center crop horizontally
        img = img.crop((left, 0, left + new_w, h))      # crop horizontally
    else:       # image is taller than 4:5
        new_h = int(w / target_ratio)       # new height
        top = (h - new_h) // 2              # pixels to cut from the top to center crop vertically
        img = img.crop((0, top, w, top + new_h))        # crop vertically

    return img.resize((INSTAGRAM_WIDTH, INSTAGRAM_HEIGHT), Image.LANCZOS)
