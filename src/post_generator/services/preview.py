from pathlib import Path

from PIL import Image, ImageColor, ImageDraw, ImageFont

# 2 main components:
# (1) displaying a preview of the composed image with metadata
# (2) providing all the terminal-based menus/prompts that let the user regenrate, save or quit

HISTORY_DIR_NAME = "history"                    # subfolder name
HISTORY_MAX_KEEP = 5                            # max number of previews you can have with regenerate

# Maximum height the preview should occupy (image + info strip combined),
# so the 4:5 image fits comfortably on a typical screen.
_MAX_PREVIEW_HEIGHT = 800
_INFO_STRIP_HEIGHT = 110
_INFO_PADDING = 16
_INFO_BG = (30, 30, 30)             # dark gray color
_INFO_FG = (240, 240, 240)          # light gray color
_INFO_FG_DIM = (180, 180, 180)      # natural gray color

# helper method for _build_preview() ---> tries different system fonts, falls back to PIL default in case of error
def _load_font(size: int) -> ImageFont.ImageFont:
    for name in ("arialbd.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:                                                         # in case of MacOS, which doesn't accept ImageFont library
            continue
    return ImageFont.load_default()


# helper method for _build_preview() --> scales the iamge down to fit a max height while preserving aspect ratio
def _fit_to_screen(image: Image.Image, max_height: int) -> Image.Image:
    if image.height <= max_height:
        return image.copy()                                                                 # no scaling needed if image shorter than max_height
    scale = max_height / image.height                                                       # if not shorter, then compute the shrink factor
    new_size = (max(1, int(image.width * scale)), max_height)
    return image.resize(new_size, Image.LANCZOS)


# helper method for show_preview() ---> composites the scaled image onto a canvas with a dark footer showing the values of the parameters
def _build_preview(image: Image.Image, position: str, text: str, x: int, y: int, variation: int) -> Image.Image:

    image_max_h = _MAX_PREVIEW_HEIGHT - _INFO_STRIP_HEIGHT
    scaled = _fit_to_screen(image.convert("RGB"), image_max_h)              # preserves the aspect ratio

    canvas = Image.new("RGB", (scaled.width, scaled.height + _INFO_STRIP_HEIGHT), _INFO_BG)     # create an empty preview canvas
    canvas.paste(scaled, (0, 0))                                                                      # drops the scaled post into the canvas

    draw = ImageDraw.Draw(canvas)                           # wraps the canvas in a Draw Object, PIL's drawing handle
    title_font = _load_font(18)                             # loading the font sizes for the title and the info bar at the bottom
    body_font = _load_font(14)

    title = f"Preview - THWS Post  |  Variation #{variation}  |  Position: {position}"
    body_line_1 = f"Text offset: x={x}, y={y}"
    body_line_2 = f"Text: {text}"
    body_line_3 = "[R] regenerate   [S] save & quit   [Q] quit without saving"

    strip_top = scaled.height
    draw.text((_INFO_PADDING, strip_top + 8), title, font=title_font, fill=_INFO_FG)
    draw.text((_INFO_PADDING, strip_top + 34), body_line_1, font=body_font, fill=_INFO_FG_DIM)
    draw.text((_INFO_PADDING, strip_top + 52), body_line_2, font=body_font, fill=_INFO_FG_DIM)
    draw.text((_INFO_PADDING, strip_top + 78), body_line_3, font=body_font, fill=_INFO_FG)

    return canvas

# opens an OS image viewer with the labeled preview of the generated post
def show_preview(image: Image.Image, position: str, text: str, x: int, y: int, variation: int = 1) -> None:

    title = f"Preview - THWS Post (Variation #{variation}, {position})"
    try:
        preview_img = _build_preview(image, position, text, x, y, variation)
        preview_img.show(title=title)
    except Exception as exc:                                                                        # failure exception for any failed use case
        print(f"[preview] could not display preview: {exc}")


POSITIONS = ("top-left", "top-right", "bottom-left", "bottom-right")

# used by all of the interactive prompts (read_action, read_regenerate_choice, prompt_position, prompt_history_pick)
def _read_key(allowed: tuple[str, ...]) -> str:
    """Block until the user presses one of `allowed` keys. Returns the lowercase char.

    Uses msvcrt on Windows for single-keypress reading without Enter. Falls back
    to line-based input on other platforms (also stdlib-only, no extra deps).
    """
    try:
        import msvcrt  # Windows stdlib
    except ImportError:
        msvcrt = None

    if msvcrt is not None:
        while True:
            ch = msvcrt.getch()                                             # read the character inputted
            if not ch:
                continue
            key = ch.decode("utf-8", errors="ignore").lower()
            if key in allowed:                                              # only return when the press is in the menu's valid options
                return key

    prompt = f"Press [{'/'.join(k.upper() for k in allowed)}] then Enter: "
    while True:
        line = input(prompt).strip().lower()                                # reads the input
        if line and line[0] in allowed:                                     # only lok at the first character
            return line[0]


def read_action() -> str:
    """Top-level shortcut: R/S/C/Q/Z."""
    return _read_key(("r", "s", "c", "q", "z"))

# parses the user's given output path into the three pieces the history operation needs
def _history_paths(out_path: str, max_keep: int = HISTORY_MAX_KEEP) -> tuple[Path, str, str]:
    out = Path(out_path)                                                        # wraps the string in a pathlib.Path
    history_dir = out.parent / HISTORY_DIR_NAME                                 # compute where the history files live
    stem = out.stem
    suffix = out.suffix or ".png"                                               # default to PNG if not extension from user
    return history_dir, stem, suffix


def save_to_history(image: Image.Image, out_path: str, max_keep: int = HISTORY_MAX_KEEP) -> None:
    """Rotate <stem>_v{N-1} -> <stem>_vN (deleting the oldest), then write the new image as _v1.

    Lives next to the resolved output file in a `history/` folder. Errors are swallowed
    so a flaky filesystem can't break the interactive loop.
    """
    try:
        history_dir, stem, suffix = _history_paths(out_path, max_keep)      # calls history_paths to derive the folder, base name and extension
        history_dir.mkdir(parents=True, exist_ok=True)                      # creates the history/ folder

        oldest = history_dir / f"{stem}_v{max_keep}{suffix}"                # drops the oldest slot first
        if oldest.exists():
            oldest.unlink()
        for i in range(max_keep - 1, 0, -1):                                # shift every remaining file up by one slot
            src = history_dir / f"{stem}_v{i}{suffix}"
            if src.exists():
                src.rename(history_dir / f"{stem}_v{i + 1}{suffix}")

        target = history_dir / f"{stem}_v1{suffix}"                         # builds the path for the new file
        if target.suffix.lower() == ".png":
            image.save(target, compress_level=1)
        else:
            image.save(target)
    except Exception as exc:
        print(f"[history] could not write history snapshot: {exc}")

# returns the existing history snapshots
def list_history(out_path: str, max_keep: int = HISTORY_MAX_KEEP) -> list[Path]:
    history_dir, stem, suffix = _history_paths(out_path, max_keep)                  # re-derive the folder, base name and extension from output path
    if not history_dir.exists():                                                    # if first time running preview, nothing to list
        return []
    return [
        p for p in (history_dir / f"{stem}_v{i}{suffix}" for i in range(1, max_keep + 1))   # builds the list
        if p.exists()
    ]


def prompt_history_pick(out_path: str, max_keep: int = HISTORY_MAX_KEEP) -> Path | None:
    """List rolling history files and let the user pick one to save (or cancel)."""
    paths = list_history(out_path, max_keep)
    if not paths:
        print("No previous variations in history yet.")
        return None
    print("Pick a previous variation to save:")
    for idx, p in enumerate(paths, 1):
        label = "newest" if idx == 1 else f"{idx - 1} regen(s) ago"
        print(f"  [{idx}] {p.name}   ({label})")
    print("  [C] cancel")
    allowed = tuple(str(i) for i in range(1, len(paths) + 1)) + ("c",)
    key = _read_key(allowed)
    if key == "c":
        return None
    return paths[int(key) - 1]


def read_regenerate_choice() -> str:
    """Sub-menu after R. Returns 'p' (position), 't' (text), or 'n' (no change)."""
    print("Change before regenerating?  [P] position   [T] text   [N] nothing")
    return _read_key(("p", "t", "n"))


def _read_color(label: str, current):
    """Prompt for a single color, accepting hex (#FF0000) or a name (orange).

    Empty input keeps `current`. Invalid input is rejected and re-prompted, so a
    typo can't crash the loop. Returns the chosen color string (or `current`).
    """
    while True:
        shown = current if current else "(none)"
        raw = input(f"New {label} color (hex like #FF0000 or name like orange, Enter to keep '{shown}'): ").strip()
        if not raw:
            return current
        try:
            ImageColor.getrgb(raw)                                              # validates hex codes and named colors via PIL
        except ValueError:
            print(f"  '{raw}' is not a valid color. Try a hex code like #FF0000 or a name like orange.")
            continue
        return raw


def prompt_colors(text_color, stroke_color):
    """Sub-menu after C. Change text color, stroke color, or both.

    Returns the (text_color, stroke_color) to use; unchanged or cancelled values
    are kept as-is.
    """
    stroke_shown = stroke_color if stroke_color else "(none)"
    print(f"Current colors -> text: {text_color}   stroke: {stroke_shown}")
    print("Change which color?  [T] text   [S] stroke   [B] both   [C] cancel")
    key = _read_key(("t", "s", "b", "c"))
    if key == "c":
        return text_color, stroke_color
    if key in ("t", "b"):
        text_color = _read_color("text", text_color)
    if key in ("s", "b"):
        stroke_color = _read_color("stroke", stroke_color)
    return text_color, stroke_color


def prompt_position(current: str) -> str:
    """Prompt for a new corner. Returns the chosen position, or `current` on cancel."""
    print(f"Current position: {current}")
    print("  [1] top-left      [2] top-right")
    print("  [3] bottom-left   [4] bottom-right")
    print("  [C] cancel")
    key = _read_key(("1", "2", "3", "4", "c"))
    if key == "c":
        return current
    return POSITIONS[int(key) - 1]


def prompt_text(current: str) -> str:
    """Prompt for new overlay text. Empty input keeps the current value."""
    print(f"Current text: {current}")
    new = input("New text (Enter to keep current): ")
    return new if new.strip() else current
