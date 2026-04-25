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
