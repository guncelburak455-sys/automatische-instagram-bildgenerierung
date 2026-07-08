import random

INSTAGRAM_WIDTH = 1080
INSTAGRAM_HEIGHT = 1350

# helper function for transform_for_position()
# flips cell coordinates within the grid - used to place the same shape in any corner
def mirror_cells(cells, width, height, horizontal=False, vertical=False):
    out = []
    for x, y in cells:                                      # takes the list of (x, y) cell coordinates to flip them inside of the photo
        nx = width - 1 - x if horizontal else x             # if horizontal true, then flip the x coordinates
        ny = height - 1 - y if vertical else y              # if vertical true, then flip the y coordinates
        out.append((nx, ny))
    return out

VALID_POSITIONS = ["top-left", "top-right", "bottom-left", "bottom-right", "left", "right"]


def choose_position(position: str, rng: random.Random) -> str:
    if position == "random" or position is None:
        return rng.choice(VALID_POSITIONS)

    return position

# given a set of cells, applies the correct mirroring to place them in the requested position
def transform_for_position(cells, width, height, position):
    if position == "top-left":
        return cells                            # starts with top-left already, so no need to do anything
    if position == "top-right":
        return mirror_cells(cells, width, height, horizontal=True)
    if position == "bottom-left":
        return mirror_cells(cells, width, height, vertical=True)
    if position == "left":
        return cells
    if position == "right":
        return mirror_cells(cells, width, height, horizontal=True)
    return mirror_cells(cells, width, height, horizontal=True, vertical=True)

# calculates the pixel offset (top-left corner) for where to start drawing the shape grid on the background photo
def anchor_offset(template_w, template_h, cell, position):
    shape_w = template_w * cell
    shape_h = template_h * cell

    if position == "top-left":
        return 0, 0
    if position == "top-right":
        return INSTAGRAM_WIDTH - shape_w, 0                         # 1080 - shape_w, 0
    if position == "bottom-left":
        return 0, INSTAGRAM_HEIGHT - shape_h                        # 0, 1350 - shape_h
    if position == "left":
        return 0, 0
    if position == "right":
        return INSTAGRAM_WIDTH - shape_w, 0
    return INSTAGRAM_WIDTH - shape_w, INSTAGRAM_HEIGHT - shape_h

# calculates the bounding rectangle where the text is outputted ; finds the min/max cell coordinates in both axes, then converts to pixel coordinates
def get_overlay_bounds(cells, cell, offset):
    ox, oy = offset

    # finding min/max cell coordinates in both x and y
    min_cell_x = min(x for x, y in cells)
    max_cell_x = max(x for x, y in cells)
    min_cell_y = min(y for x, y in cells)
    max_cell_y = max(y for x, y in cells)

    # convert the min/max to pixel coordiantes
    left = ox + min_cell_x * cell
    top = oy + min_cell_y * cell
    right = ox + (max_cell_x + 1) * cell
    bottom = oy + (max_cell_y + 1) * cell

    return left, top, right, bottom

# --- Epic B - Issue 2: True Center of Mass ---
# Change: Added get_visual_center to calculate the true center of mass / visual center based on the mask's cells.
# Reason: Previously, hardcoded bias_x and bias_y values were used, causing text to spill out of the mask,
# especially in the bottom-right corner. This helper ensures the text is perfectly centered across all 4 positions.
def get_visual_center(cells, cell_size, offset, position=None):
    """
    Calculates the exact visual center (center of mass) of the mask
    based on its grid cells. Optionally applies a shift towards the corner.
    """
    ox, oy = offset

    if not cells:
        return ox, oy

    # Side positions: keep the text inside the solid block, not over the
    # fingerprint trail. The solid block occupies columns 0..3 of the side
    # template; for "right" the cells have been horizontally mirrored, so the
    # solid block sits at the opposite end (columns 3..6 with width=7).
    if position in ("left", "right"):
        max_x = max(x for x, _ in cells)
        if position == "left":
            block_cells = [(x, y) for x, y in cells if x <= 3]
        else:
            block_cells = [(x, y) for x, y in cells if x >= max_x - 3]

        avg_cell_x = sum(x for x, _ in block_cells) / len(block_cells)
        avg_cell_y = sum(y for _, y in block_cells) / len(block_cells)
        center_x = ox + (avg_cell_x + 0.5) * cell_size
        center_y = oy + (avg_cell_y + 0.5) * cell_size
        return center_x, center_y

    avg_cell_x = sum(x for x, y in cells) / len(cells)
    avg_cell_y = sum(y for x, y in cells) / len(cells)

    center_x = ox + (avg_cell_x + 0.5) * cell_size
    center_y = oy + (avg_cell_y + 0.5) * cell_size

    if position:
        shift_amount = cell_size * 0.5
        if "left" in position:
            center_x -= shift_amount
        elif "right" in position:
            center_x += shift_amount

        if "top" in position:
            center_y -= shift_amount
        elif "bottom" in position:
            center_y += shift_amount

    return center_x, center_y