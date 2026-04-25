from pathlib import Path
from PIL import Image, UnidentifiedImageError

INSTAGRAM_WIDTH = 1080
INSTAGRAM_HEIGHT = 1350
CELL_SIZE = 150

BASE_TEMPLATE = [
    "1111110",
    "1111111",
    "1111110",
    "1111100",
    "1110000",
    "0100000",
]


def template_to_grid(template):
    return [list(row) for row in template]


def grid_to_cells(grid):
    cells = []
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch == "1":
                cells.append((x, y))
    return cells


def crop_to_4_5(img: Image.Image) -> Image.Image:
    target_ratio = INSTAGRAM_WIDTH / INSTAGRAM_HEIGHT
    w, h = img.size
    ratio = w / h

    if ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))

    return img.resize((INSTAGRAM_WIDTH, INSTAGRAM_HEIGHT), Image.LANCZOS)