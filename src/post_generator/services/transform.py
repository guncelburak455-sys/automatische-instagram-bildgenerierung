import random

INSTAGRAM_WIDTH = 1080
INSTAGRAM_HEIGHT = 1350


def choose_position(position: str, rng: random.Random) -> str:
    if position != "random":
        return position
    return rng.choice(["top-left", "top-right", "bottom-left", "bottom-right"])


def mirror_cells(cells, width, height, horizontal=False, vertical=False):
    out = []
    for x, y in cells:
        nx = width - 1 - x if horizontal else x
        ny = height - 1 - y if vertical else y
        out.append((nx, ny))
    return out


def transform_for_position(cells, width, height, position):
    if position == "top-left":
        return cells
    if position == "top-right":
        return mirror_cells(cells, width, height, horizontal=True)
    if position == "bottom-left":
        return mirror_cells(cells, width, height, vertical=True)
    return mirror_cells(cells, width, height, horizontal=True, vertical=True)


def anchor_offset(template_w, template_h, cell, position):
    shape_w = template_w * cell
    shape_h = template_h * cell

    if position == "top-left":
        return 0, 0
    if position == "top-right":
        return INSTAGRAM_WIDTH - shape_w, 0
    if position == "bottom-left":
        return 0, INSTAGRAM_HEIGHT - shape_h
    return INSTAGRAM_WIDTH - shape_w, INSTAGRAM_HEIGHT - shape_h

def get_text_anchor(cells, cell, offset):
    ox, oy = offset
    min_y = min(y for x, y in cells)
    top_row_xs = [x for x, y in cells if y == min_y]
    min_x = min(top_row_xs)
    return ox + min_x * cell, oy + min_y * cell


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