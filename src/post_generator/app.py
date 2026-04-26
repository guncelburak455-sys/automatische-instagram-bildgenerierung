import random
from pathlib import Path
from PIL import Image

from .config import Config
from .services import composition, mask, transform
from .services.textrenderer import TextRenderer
from .services.post_generator import crop_to_4_5, template_to_grid, grid_to_cells, BASE_TEMPLATE, CELL_SIZE

# pipeline: crop photo -> resolve position -> build cell grid -> mirror for corner -> generate mask -> compose with orange -> render text -> save
def generate_post(config: Config):                      # orchestrates the entire image generation pipeline

    # opens the image file at the path stored in config.photo ; then converts it to RGBA mode, RGB + transparency channel for opacity etc.
    bg = Image.open(Path(config.photo)).convert("RGBA")
    bg = crop_to_4_5(bg)        # cropt to 4:5 aspect ratio

    position = transform.choose_position(config.position, random.Random())      # chooses the position of the overlay

    grid = template_to_grid(BASE_TEMPLATE)          # converts base template into a 2D list of characters - X for "filled with overlay"
    cells = grid_to_cells(grid)         # extracts all coordinates of X filled cells
    template_h = len(grid)          # number of rows in the gird
    template_w = len(grid[0])       # number of colums in the grid

    cells = transform.transform_for_position(cells, template_w, template_h, position)       # for every position, it mirrors horizontally and/or vertically
    offset = transform.anchor_offset(template_w, template_h, CELL_SIZE, position)       # x,y coordinates for text inside of the mask overlay

    generated_mask = mask.build_smooth_mask(bg.size, cells, CELL_SIZE, offset)
    result = composition.compose(bg, generated_mask)            # composites the background photo uploaded with the THWS orange overlay mask

    bounds = transform.get_overlay_bounds(cells, CELL_SIZE, offset)         # bounds for the text
    renderer = TextRenderer()       # instance of renderer
    result = renderer.draw_text_on_overlay(result, config.text, bounds, position, config.x, config.y)       # drawing the user's tet ontop of the verlay

    output_dir = config.output_path if config.output_path else "."
    output_name = config.output_name if Path(config.output_name).suffix else config.output_name + ".png"
    out_path = str(Path(output_dir) / output_name)
    composition.save_output(result, out_path)

    print(f"Done. Position: {position}")
    print(f"Saved to: {out_path}")
