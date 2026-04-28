from pathlib import Path
from PIL import Image, UnidentifiedImageError

INSTAGRAM_WIDTH = 1080
INSTAGRAM_HEIGHT = 1350
# each cell is 150px - 1080 divides into exactly 7.2 of thesem, 1035 into 9
CELL_SIZE = 150

# the shape of the overlay - 1 = filled cell, 0 = empty. top-left corner variant ; other corners are derived by mirroring
BASE_TEMPLATE = [
    "1111110",
    "1111111",
    "1111110",
    "1111100",
    "1110000",
    "0100000",
]

# converts the BASE_TEMPLATE into a list of individual characters
def template_to_grid(template):
    return [list(row) for row in template]

# walks through every position in the grid and collects the (x, y) coordinates of every cell that has "1".
def grid_to_cells(grid):
    cells = []
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch == "1":
                cells.append((x, y))
    return cells

# takes any image and crops it to a 4:5 aspect ratio, then resizes it to 1080x1350
def crop_to_4_5(img: Image.Image) -> Image.Image:
    target_ratio = INSTAGRAM_WIDTH / INSTAGRAM_HEIGHT
    w, h = img.size         # current widht and height of the input image
    ratio = w / h           # current aspect ratio of the input image

    if ratio > target_ratio:        # is image wider than 4:5
        new_w = int(h * target_ratio)           # new width
        left = (w - new_w) // 2                 # how many pixels to cut from the left side to center the crop horizontally
        img = img.crop((left, 0, left + new_w, h))      # crops the image horizontally
    else:       # taller than 4:5
        new_h = int(w / target_ratio)       # new height
        top = (h - new_h) // 2          # how many pixels to cut from the top to center it vertically
        img = img.crop((0, top, w, top + new_h))        # crops the image vertically

    return img.resize((INSTAGRAM_WIDTH, INSTAGRAM_HEIGHT), Image.LANCZOS)