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
    result = renderer.draw_text_on_overlay(result, config.text, overlay.bounds, position, config.x, config.y)

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
    bg = Image.open(Path(config.photo)).convert("RGBA")
    bg = crop_to_4_5(bg)

    rng = random.Random()

    # If config.position is "random", this chooses one real corner.
    # If config.position is already "top-left", etc., it keeps that.
    position = transform.choose_position(config.position, rng)

    overlay = build_overlay_layout(position, rng)

    generated_mask = mask.build_smooth_mask(
        bg.size,
        overlay.cells,
        CELL_SIZE,
        overlay.offset
    )

    result = composition.compose(bg, generated_mask)

    renderer = TextRenderer()
    result = renderer.draw_text_on_overlay(
        result,
        config.text,
        overlay.bounds,
        position,
        config.x,
        config.y
    )

    if config.preview:
        show_preview(result, position, config.text, config.x, config.y)

    output_dir = config.output_path if config.output_path else "."
    output_name = config.output_name if Path(config.output_name).suffix else config.output_name + ".png"
    out_path = str(Path(output_dir) / output_name)

    composition.save_output(result, out_path)

    print(f"Done. Position: {position}")
    print(f"Saved to: {out_path}")
