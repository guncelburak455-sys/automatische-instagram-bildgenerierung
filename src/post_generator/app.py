import random
from pathlib import Path
from PIL import Image

from .config import Config
from .services import composition, mask, transform
from .services.overlay_service import CELL_SIZE, build_overlay_layout
from .services.preview import show_preview, read_action, read_regenerate_choice, prompt_position, prompt_text
from .services.textrenderer import TextRenderer
from .services.post_generator import crop_to_4_5


def _resolve_output_path(config: Config) -> str:
    output_dir = config.output_path if config.output_path else "."
    output_name = config.output_name if Path(config.output_name).suffix else config.output_name + ".png"
    return str(Path(output_dir) / output_name)


# pipeline: crop photo -> resolve position -> build overlay layout -> generate mask -> compose with orange -> render text
def _build_image(config: Config) -> tuple[Image.Image, str]:
    """Run the full generation pipeline once and return (image, resolved_position)."""
    bg = Image.open(Path(config.photo)).convert("RGBA")
    bg = crop_to_4_5(bg)

    rng = random.Random()
    position = transform.choose_position(config.position, rng)
    overlay = build_overlay_layout(position, rng)

    generated_mask = mask.build_smooth_mask(bg.size, overlay.cells, CELL_SIZE, overlay.offset)
    result = composition.compose(bg, generated_mask)

    renderer = TextRenderer()
    # --- Epic B - Issue 2 & 3: Visual Center & Text Rendering Engine ---
    # Change:
    # 1. Called transform.get_visual_center to calculate the true visual center.
    # 2. Passed new arguments (font, text_color, stroke_color) to renderer.draw_text_on_overlay.
    # Reason: To use the dynamic visual center instead of hardcoded alignment values,
    # and to pass the newly added styling config (Issue 1) to the text renderer engine.
    visual_center = transform.get_visual_center(overlay.cells, CELL_SIZE, overlay.offset, position)
    result = renderer.draw_text_on_overlay(
        image=result,
        text=config.text,
        bounds=overlay.bounds,
        visual_center=visual_center,
        cells=overlay.cells,
        cell_size=CELL_SIZE,
        offset=overlay.offset,
        x_offset=config.x,
        y_offset=config.y,
        font_name=config.font,
        text_color=config.text_color,
        stroke_color=config.stroke_color
    )

    return result, position


_HINT = "[R] regenerate   [S] save & quit   [Q] quit without saving"


def _interactive_loop(config: Config, out_path: str) -> None:
    """Show preview, read R/S/Q, regenerate / save / quit accordingly."""
    variation = 1
    image, position = _build_image(config)
    show_preview(image, position, config.text, config.x, config.y, variation)
    print(_HINT)

    while True:
        action = read_action()
        if action == "r":
            choice = read_regenerate_choice()
            if choice == "p":
                config.position = prompt_position(config.position)
            elif choice == "t":
                config.text = prompt_text(config.text)
            variation += 1
            print(f"Regenerating (variation #{variation}, position={config.position})...")
            image, position = _build_image(config)
            show_preview(image, position, config.text, config.x, config.y, variation)
            print(_HINT)
        elif action == "s":
            composition.save_output(image, out_path)
            print(f"Saved variation #{variation}. Position: {position}")
            print(f"Saved to: {out_path}")
            return
        elif action == "q":
            print("Quit without saving.")
            return


def generate_post(config: Config):
    out_path = _resolve_output_path(config)

    if config.preview:
        _interactive_loop(config, out_path)
        return

    image, position = _build_image(config)
    composition.save_output(image, out_path)
    print(f"Done. Position: {position}")
    print(f"Saved to: {out_path}")
