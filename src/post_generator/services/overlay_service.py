"""Overlay template generation and mutation logic.

This service owns the stair-shaped orange overlay grid. It starts from one of
several base templates and applies only small, allowed mutations so the final
shape keeps the same visual style.
"""

from dataclasses import dataclass
import random
from typing import List, Optional, Sequence, Tuple

from . import transform

# Each overlay grid cell is 150px.
CELL_SIZE = 150

Template = Sequence[str]
Grid = List[List[str]]
Cell = Tuple[int, int]
Bounds = Tuple[int, int, int, int]


@dataclass(frozen=True)
class OverlayLayout:
    """Fully prepared overlay data for the selected corner position."""

    template: List[str]
    cells: List[Cell]
    offset: Cell
    bounds: Bounds
    width: int
    height: int

# Different base stair shapes. 1 = filled overlay cell, 0 = empty cell.
# These are top-left corner variants; other corners are derived by mirroring.
BASE_TEMPLATES = [
    [
        "1111110",
        "1111111",
        "1111110",
        "1111100",
        "1110000",
        "0000100",
    ],
    [
        "1111110",
        "1111111",
        "1111110",
        "1111000",
        "1110000",
        "0000100",
    ],
    [
        "1111110",
        "1111111",
        "1111100",
        "1111000",
        "1100000",
        "0000000",
    ],
]

# Backwards-compatible name for any code that still imports BASE_TEMPLATE.
BASE_TEMPLATE = BASE_TEMPLATES[0]

# Cells where random variation is allowed. Coordinates are (x, y), 0-based.
# Avoid y=5 because it creates the extra bottom square/notch after mirroring.
ALLOWED_ADD = [(6, 2)]

ALLOWED_REMOVE = [(5, 1), (4, 3), (2, 5)]

# ---------------------------------------------------------------------------
# Side templates for "left" / "right" positions.
# These are wider, vertically-centered overlays that hug one wall and extend
# a fingerprint-style trail toward the opposite side.  Authored in the "left"
# orientation; the "right" variant is derived by horizontal mirroring in the
# transform service (same approach as corners).
#
# Design:  columns 0-3 → solid text block (where the caption is rendered)
#          columns 4-6 → sparse fingerprint trail (scattered cells)
#
# Mutation rules for side templates. Coordinates are (x, y), 0-based.
# These target cells along the fingerprint trail (right side) where adding
# or removing a dot still looks natural without breaking the solid text block.
# ---------------------------------------------------------------------------

BASE_TEMPLATES_SIDE = [
    # Variant 1 — trail reaches far right with one isolated dot
    [
        "0011000",
        "0111100",
        "1111110",
        "1111101",
        "1111110",
        "1111100",
        "0111000",
        "0010000",
    ],
    # Variant 2 — wider top, two separated fingerprint dots
    [
        "0111000",
        "1111100",
        "1111110",
        "1111001",
        "1111100",
        "0111010",
        "0011000",
        "0010000",
    ],
    # Variant 3 — denser trail, more organic silhouette
    [
        "0011000",
        "1111100",
        "1111110",
        "1111011",
        "1111110",
        "0111100",
        "0011000",
        "0010000",
    ],
]

# Cells where random variation is allowed on side templates.
# Only targets the fingerprint trail region (columns 4-6) so the solid
# text block on the left stays intact.
ALLOWED_ADD_SIDE = [(5, 1), (6, 4), (5, 6)]
ALLOWED_REMOVE_SIDE = [(6, 3), (5, 5), (6, 5)]


def template_to_grid(template: Template) -> Grid:
    """Convert the string template into a mutable 2D grid."""
    return [list(row) for row in template]


def grid_to_template(grid: Grid) -> List[str]:
    """Convert a mutable grid back into string-template format."""
    return ["".join(row) for row in grid]


def _is_inside_grid(grid: Grid, x: int, y: int) -> bool:
    return 0 <= y < len(grid) and 0 <= x < len(grid[y])


def mutate_template(template: Template, rng: Optional[random.Random] = None, max_changes: int = 1) -> List[str]:
    """Apply small allowed add/remove mutations to one base template.

    A mutation is only valid when it keeps the existing shape style:
    - ALLOWED_ADD cells may only change from 0 to 1.
    - ALLOWED_REMOVE cells may only change from 1 to 0.

    With max_changes=1, each run can create a subtle variation without making
    the stair shape look unrelated to the base template.
    """
    rng = rng or random.Random()
    grid = template_to_grid(template)
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


def random_stair_template(rng: Optional[random.Random] = None, max_changes: int = 1) -> List[str]:
    """Pick a base template and return a small random variation of it."""
    rng = rng or random.Random()
    base_template = rng.choice(BASE_TEMPLATES)
    return mutate_template(base_template, rng, max_changes)


def grid_to_cells(grid: Grid) -> List[Cell]:
    """Return the coordinates of every filled overlay cell."""
    cells = []
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch == "1":
                cells.append((x, y))
    return cells


def build_overlay_layout(position: str, rng: Optional[random.Random] = None, max_changes: int = 1) -> OverlayLayout:
    """Create the randomized overlay cells, offset and bounds for a corner.

    The template is generated in top-left orientation first. Afterwards, the
    existing transform service mirrors it for top-right, bottom-left or
    bottom-right.
    """
    rng = rng or random.Random()
    template = random_stair_template(rng, max_changes)
    grid = template_to_grid(template)

    template_height = len(grid)
    template_width = len(grid[0])
    cells = grid_to_cells(grid)

    cells = transform.transform_for_position(cells, template_width, template_height, position)
    offset = transform.anchor_offset(template_width, template_height, CELL_SIZE, position)
    bounds = transform.get_overlay_bounds(cells, CELL_SIZE, offset)

    return OverlayLayout(
        template=template,
        cells=cells,
        offset=offset,
        bounds=bounds,
        width=template_width,
        height=template_height,
    )
