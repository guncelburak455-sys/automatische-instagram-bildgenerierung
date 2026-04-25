import random
from pathlib import Path
from PIL import Image

from .config import Config
from .services import composition, mask, transform
from .services.textrenderer import TextRenderer
from .services.post_generator import crop_to_4_5, template_to_grid, grid_to_cells, BASE_TEMPLATE, CELL_SIZE

# pipeline: crop photo -> resolve position -> build cell grid -> mirror for corner -> generate mask -> compose with orange -> render text -> save
def generate_post(config: Config):
    bg = Image.open(Path(config.photo)).convert("RGBA")
    bg = crop_to_4_5(bg)

    position = transform.choose_position(config.position, random.Random())

    grid = template_to_grid(BASE_TEMPLATE)
    cells = grid_to_cells(grid)
    template_h = len(grid)
    template_w = len(grid[0])

    cells = transform.transform_for_position(cells, template_w, template_h, position)
    offset = transform.anchor_offset(template_w, template_h, CELL_SIZE, position)

    generated_mask = mask.build_smooth_mask(bg.size, cells, CELL_SIZE, offset)
    result = composition.compose(bg, generated_mask)

    bounds = transform.get_overlay_bounds(cells, CELL_SIZE, offset)
    renderer = TextRenderer()
    result = renderer.draw_text_on_overlay(result, config.text, bounds, position, config.x, config.y)

    output_dir = config.output_path if config.output_path else "."
    output_name = config.output_name if Path(config.output_name).suffix else config.output_name + ".png"
    out_path = str(Path(output_dir) / output_name)
    composition.save_output(result, out_path)

    print(f"Done. Position: {position}")
    print(f"Saved to: {out_path}")
