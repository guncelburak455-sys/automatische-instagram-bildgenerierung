from pathlib import Path
import random
from PIL import Image, UnidentifiedImageError

INSTAGRAM_WIDTH = 1080
INSTAGRAM_HEIGHT = 1350
# each cell is 150px - 1080 divides into exactly 7.2 of thesem, 1035 into 9
CELL_SIZE = 150

# Different base stair shapes. 1 = filled overlay cell, 0 = empty cell.
# These are top-left corner variants; other corners are derived by mirroring.
BASE_TEMPLATES = [
    [
        "1111110",
        "1111111",
        "1111110",
        "1111100",
        "1110000",
        "0100000",
    ],
    [
        "1111110",
        "1111111",
        "1111110",
        "1111000",
        "1110000",
        "0110000",
    ],
    [
        "1111110",
        "1111111",
        "1111100",
        "1111000",
        "1100000",
        "0100000",
    ],
]

# Backwards-compatible name for any code that still imports BASE_TEMPLATE.
BASE_TEMPLATE = BASE_TEMPLATES[0]

# Cells where random variation is allowed. Coordinates are (x, y), 0-based.
ALLOWED_ADD = [(5, 4), (6, 2), (4, 5)]
ALLOWED_REMOVE = [(5, 1), (4, 3), (2, 5)]


def template_to_grid(template):
    # converts the template into a list of individual characters
    return [list(row) for row in template]


def grid_to_template(grid):
    # converts a grid back into the string-template format
    return ["".join(row) for row in grid]


def _is_inside_grid(grid, x, y):
    return 0 <= y < len(grid) and 0 <= x < len(grid[y])


def random_stair_template(rng=None, max_changes=1):
    """Return a random stair template using only the allowed add/remove cells.

    Steps:
    1. Pick one of BASE_TEMPLATES.
    2. Collect only valid changes:
       - add is valid only when the current cell is 0
       - remove is valid only when the current cell is 1
    3. Apply up to max_changes random changes.

    max_changes=1 keeps the THWS shape recognizable while still creating
    visible random variation. Increase it if you want stronger randomness.
    """
    rng = rng or random.Random()
    grid = template_to_grid(rng.choice(BASE_TEMPLATES))

    possible_changes = []

    for x, y in ALLOWED_ADD:
        if _is_inside_grid(grid, x, y) and grid[y][x] == "0":
            possible_changes.append((x, y, "1"))

    for x, y in ALLOWED_REMOVE:
        if _is_inside_grid(grid, x, y) and grid[y][x] == "1":
            possible_changes.append((x, y, "0"))

    if possible_changes and max_changes > 0:
        number_of_changes = rng.randint(0, min(max_changes, len(possible_changes)))
        for x, y, value in rng.sample(possible_changes, number_of_changes):
            grid[y][x] = value

    return grid_to_template(grid)

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