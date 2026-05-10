import random
from pathlib import Path
from PIL import Image

from .config import Config
from .services import composition, mask, transform
from .services.overlay_service import CELL_SIZE, build_overlay_layout
from .services.preview import show_preview
from .services.textrenderer import TextRenderer
from .services.post_generator import crop_to_4_5


# pipeline: crop photo -> resolve position -> generate overlay layout -> generate mask -> compose with orange -> render text -> save
def generate_post(config: Config):                      # orchestrates the entire image generation pipeline

    # Opens the image file at the path stored in config.photo, then converts it to RGBA mode.
    bg = Image.open(Path(config.photo)).convert("RGBA")
    bg = crop_to_4_5(bg)        # crop to 4:5 aspect ratio

    rng = random.Random()
    position = transform.choose_position(config.position, rng)      # chooses the position of the overlay

    overlay = build_overlay_layout(position, rng)

    generated_mask = mask.build_smooth_mask(bg.size, overlay.cells, CELL_SIZE, overlay.offset)
    result = composition.compose(bg, generated_mask)            # composites the background photo with the THWS orange overlay mask

    renderer = TextRenderer()       # instance of renderer
    result = renderer.draw_text_on_overlay(result, config.text, overlay.bounds, position, config.x, config.y)       # draw the user's text on top of the overlay

    # Sprint 1 Update:
    if config.preview:
        show_preview(result, position, config.text, config.x, config.y)

    output_dir = config.output_path if config.output_path else "."
    output_name = config.output_name if Path(config.output_name).suffix else config.output_name + ".png"
    out_path = str(Path(output_dir) / output_name)
    composition.save_output(result, out_path)

    print(f"Done. Position: {position}")
    print(f"Saved to: {out_path}")
