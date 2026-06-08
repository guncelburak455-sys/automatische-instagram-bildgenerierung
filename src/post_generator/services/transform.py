import random

INSTAGRAM_WIDTH = 1080
INSTAGRAM_HEIGHT = 1350


def choose_position(position: str, rng: random.Random) -> str:
    if position != "random":
        return position
    return rng.choice(["top-left", "top-right", "bottom-left", "bottom-right"])

# flips cell coordinates within the grid - used to place the same shape in any corner
def mirror_cells(cells, width, height, horizontal=False, vertical=False):
    out = []
    for x, y in cells:
        nx = width - 1 - x if horizontal else x
        ny = height - 1 - y if vertical else y
        out.append((nx, ny))
    return out

VALID_POSITIONS = ["top-left", "top-right", "bottom-left", "bottom-right", "left", "right"]


def choose_position(position: str, rng: random.Random) -> str:
    if position == "random" or position is None:
        return rng.choice(VALID_POSITIONS)

    return position
# maps each corner to the right mirroring operation
def transform_for_position(cells, width, height, position):
    if position == "top-left":
        return cells
    if position == "top-right":
        return mirror_cells(cells, width, height, horizontal=True)
    if position == "bottom-left":
        return mirror_cells(cells, width, height, vertical=True)
    if position == "left":
        return cells
    if position == "right":
        return mirror_cells(cells, width, height, horizontal=True)
    return mirror_cells(cells, width, height, horizontal=True, vertical=True)

# returns the pixel (x, y) where the top-left of the shape grid should be places so it sits flush in the chosen corner
def anchor_offset(template_w, template_h, cell, position):
    shape_w = template_w * cell
    shape_h = template_h * cell

    if position == "top-left":
        return 0, 0
    if position == "top-right":
        return INSTAGRAM_WIDTH - shape_w, 0
    if position == "bottom-left":
        return 0, INSTAGRAM_HEIGHT - shape_h
    if position == "left":
        return 0, (INSTAGRAM_HEIGHT - shape_h) // 2
    if position == "right":
        return INSTAGRAM_WIDTH - shape_w, (INSTAGRAM_HEIGHT - shape_h) // 2
    return INSTAGRAM_WIDTH - shape_w, INSTAGRAM_HEIGHT - shape_h

# function that has been replaced by get_overlay_bounds
def get_text_anchor(cells, cell, offset):
    ox, oy = offset
    min_y = min(y for x, y in cells)
    top_row_xs = [x for x, y in cells if y == min_y]
    min_x = min(top_row_xs)
    return ox + min_x * cell, oy + min_y * cell

# calculates the bounding rectangle around all filled cells ; finds the min/max cell coordinates in both axes, then converts to pixel coordinates
def get_overlay_bounds(cells, cell, offset):
    ox, oy = offset

    min_cell_x = min(x for x, y in cells)
    max_cell_x = max(x for x, y in cells)
    min_cell_y = min(y for x, y in cells)
    max_cell_y = max(y for x, y in cells)

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