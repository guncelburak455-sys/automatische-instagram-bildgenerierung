import random
from pathlib import Path
from PIL import Image

from .config import Config
from .services import composition, mask, transform
from .services.overlay_service import CELL_SIZE, build_overlay_layout
from .services.preview import show_preview, read_action, read_regenerate_choice, prompt_position, prompt_text, prompt_colors, prompt_mask_color
from .services.textrenderer import TextRenderer
from .services.post_generator import crop_to_4_5


def _resolve_output_path(config: Config) -> str:
    output_dir = config.output_path if config.output_path else "."
    output_name = config.output_name if Path(config.output_name).suffix else config.output_name + ".png"
    return str(Path(output_dir) / output_name)


# pipeline: crop photo -> resolve position -> build overlay layout -> generate mask -> compose with mask color -> render text
def _build_image(config: Config) -> tuple[Image.Image, str]:
    """Run the full generation pipeline once and return (image, resolved_position)."""
    bg = Image.open(Path(config.photo)).convert("RGBA")
    bg = crop_to_4_5(bg)

    rng = random.Random()
    position = transform.choose_position(config.position, rng)
    overlay = build_overlay_layout(position, rng)

    generated_mask = mask.build_smooth_mask(bg.size, overlay.cells, CELL_SIZE, overlay.offset)
    result = composition.compose(bg, generated_mask, config.mask_color)        # falls back to THWS orange when mask_color is None

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
        stroke_color=config.stroke_color,
        letter_spacing=config.letter_spacing
    )

    return result, position

# shows up each time we run a command with the --preview cli parameter
_HINT = "[R] regenerate   [S] save & quit   [C] color   [M] mask color   [Z] zurueck (pick previous)   [Q] quit without saving"

# takes the parsed Config CLI and the output file path ; returns nothing, driven by R/S/Q
def _interactive_loop(config: Config, out_path: str) -> None:
    from .services.preview import save_to_history, prompt_history_pick

    variation = 1                                                               # counter for each iteration
    image, position = _build_image(config)                                      # as per the issue, new pipeline run every iteration
    save_to_history(image, out_path)                                            # writes the variation in the history folder
    show_preview(image, position, config.text, config.x, config.y, variation)   # opens the image via PIL.Image.show()
    print(_HINT)                                                                # prints the command menu again to wait for R/S/Q

    while True:                                                                 # loop bis ich S/R/Q drucke
        action = read_action()
        if action == "r":
            choice = read_regenerate_choice()                                   # asks for a follow-up ; intended for random positioning
            if choice == "p":
                config.position = prompt_position(config.position)              # asks for a new position
            elif choice == "t":
                config.text = prompt_text(config.text)                          # asks for a new text parameter
            variation += 1                                                      # add to the counter after each keystroke
            print(f"Regenerating (variation #{variation}, position={config.position})...")
            image, position = _build_image(config)
            save_to_history(image, out_path)
            show_preview(image, position, config.text, config.x, config.y, variation)
            print(_HINT)
        elif action == "m":                                                     # change the overlay mask color, then regenerate
            config.mask_color = prompt_mask_color(config.mask_color)           # persists across subsequent R-presses via the shared config
            variation += 1
            mask_shown = config.mask_color if config.mask_color else "#FF8400 (default)"
            print(f"Regenerating (variation #{variation}, mask={mask_shown})...")
            image, position = _build_image(config)
            save_to_history(image, out_path)
            show_preview(image, position, config.text, config.x, config.y, variation)
            print(_HINT)
        elif action == "c":                                                     # change text / stroke color, then regenerate
            config.text_color, config.stroke_color = prompt_colors(config.text_color, config.stroke_color)
            variation += 1
            stroke_shown = config.stroke_color if config.stroke_color else "none"
            print(f"Regenerating (variation #{variation}, text={config.text_color}, stroke={stroke_shown})...")
            image, position = _build_image(config)
            save_to_history(image, out_path)
            show_preview(image, position, config.text, config.x, config.y, variation)
            print(_HINT)
        elif action == "s":                                                     # save the output
            composition.save_output(image, out_path)
            print(f"Saved variation #{variation}. Position: {position}")
            print(f"Saved to: {out_path}")
            return
        elif action == "z":                                                     # go back to an old variation
            picked = prompt_history_pick(out_path)
            if picked is None:                                                  # fallback if we clicked Z by accident
                print(_HINT)
                continue
            chosen = Image.open(picked).convert("RGBA")
            composition.save_output(chosen, out_path)
            print(f"Saved {picked.name} -> {out_path}")
            return
        elif action == "q":                                                     # in case we decide to quit the whole process
            print("Quit without saving.")
            return


def generate_post(config: Config):
    out_path = _resolve_output_path(config)                                     # build the output path ; adds .png if no extension

    if config.preview:                                                          # if we gave --preview flag in the command, run the following
        _interactive_loop(config, out_path)
        return

    image, position = _build_image(config)                                      # build the image
    composition.save_output(image, out_path)                                    # save it
    print(f"Done. Position: {position}")                                        # print the information
    print(f"Saved to: {out_path}")
