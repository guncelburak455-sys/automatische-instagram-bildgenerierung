from PIL import Image, ImageDraw, ImageFont

# Maximum height the preview should occupy (image + info strip combined),
# so the 4:5 image fits comfortably on a typical screen.
_MAX_PREVIEW_HEIGHT = 800
_INFO_STRIP_HEIGHT = 110
_INFO_PADDING = 16
_INFO_BG = (30, 30, 30)
_INFO_FG = (240, 240, 240)
_INFO_FG_DIM = (180, 180, 180)


def _load_font(size: int) -> ImageFont.ImageFont:
    for name in ("arialbd.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _fit_to_screen(image: Image.Image, max_height: int) -> Image.Image:
    if image.height <= max_height:
        return image.copy()
    scale = max_height / image.height
    new_size = (max(1, int(image.width * scale)), max_height)
    return image.resize(new_size, Image.LANCZOS)


def _build_preview(image: Image.Image, position: str, text: str, x: int, y: int, variation: int) -> Image.Image:
    """Return a new image: the generated post with an info strip drawn underneath.

    The strip shows the run title (with variation counter), position+offset, and
    the user's text — so the user sees what produced the result without needing
    a windowing toolkit.
    """
    image_max_h = _MAX_PREVIEW_HEIGHT - _INFO_STRIP_HEIGHT
    scaled = _fit_to_screen(image.convert("RGB"), image_max_h)

    canvas = Image.new("RGB", (scaled.width, scaled.height + _INFO_STRIP_HEIGHT), _INFO_BG)
    canvas.paste(scaled, (0, 0))

    draw = ImageDraw.Draw(canvas)
    title_font = _load_font(18)
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


def show_preview(image: Image.Image, position: str, text: str, x: int, y: int, variation: int = 1) -> None:
    """Open a preview window for the generated image.

    Builds a decorated copy with an info strip and hands it to PIL.Image.show()
    so the user gets a labeled preview without needing tkinter or any extra
    pip dependency. Errors are swallowed so the save step still runs.
    """
    title = f"Preview - THWS Post (Variation #{variation}, {position})"
    try:
        preview_img = _build_preview(image, position, text, x, y, variation)
        preview_img.show(title=title)
    except Exception as exc:
        print(f"[preview] could not display preview: {exc}")


POSITIONS = ("top-left", "top-right", "bottom-left", "bottom-right")


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
            ch = msvcrt.getch()
            if not ch:
                continue
            key = ch.decode("utf-8", errors="ignore").lower()
            if key in allowed:
                return key

    prompt = f"Press [{'/'.join(k.upper() for k in allowed)}] then Enter: "
    while True:
        line = input(prompt).strip().lower()
        if line and line[0] in allowed:
            return line[0]


def read_action() -> str:
    """Top-level shortcut: R/S/Q."""
    return _read_key(("r", "s", "q"))


def read_regenerate_choice() -> str:
    """Sub-menu after R. Returns 'p' (position), 't' (text), or 'n' (no change)."""
    print("Change before regenerating?  [P] position   [T] text   [N] nothing")
    return _read_key(("p", "t", "n"))


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
