from PIL import Image, ImageDraw, ImageFont

# Maximum height the preview should occupy (image + info strip combined),
# so the 4:5 image fits comfortably on a typical screen.
_MAX_PREVIEW_HEIGHT = 800
_INFO_STRIP_HEIGHT = 90
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


def _build_preview(image: Image.Image, position: str, text: str, x: int, y: int) -> Image.Image:
    """Return a new image: the generated post with an info strip drawn underneath.

    The strip shows the run title, position+offset, and the user's text — so the
    user sees what produced the result without needing a windowing toolkit.
    """
    image_max_h = _MAX_PREVIEW_HEIGHT - _INFO_STRIP_HEIGHT
    scaled = _fit_to_screen(image.convert("RGB"), image_max_h)

    canvas = Image.new("RGB", (scaled.width, scaled.height + _INFO_STRIP_HEIGHT), _INFO_BG)
    canvas.paste(scaled, (0, 0))

    draw = ImageDraw.Draw(canvas)
    title_font = _load_font(18)
    body_font = _load_font(14)

    title = f"Preview - THWS Post  |  Position: {position}"
    body_line_1 = f"Text offset: x={x}, y={y}"
    body_line_2 = f"Text: {text}"

    strip_top = scaled.height
    draw.text(
        (_INFO_PADDING, strip_top + 10),
        title,
        font=title_font,
        fill=_INFO_FG,
    )
    draw.text(
        (_INFO_PADDING, strip_top + 38),
        body_line_1,
        font=body_font,
        fill=_INFO_FG_DIM,
    )
    draw.text(
        (_INFO_PADDING, strip_top + 58),
        body_line_2,
        font=body_font,
        fill=_INFO_FG_DIM,
    )

    return canvas


def show_preview(image: Image.Image, position: str, text: str, x: int, y: int) -> None:
    """Open a preview window for the generated image.

    Builds a decorated copy with an info strip and hands it to PIL.Image.show()
    so the user gets a labeled preview without needing tkinter or any extra
    pip dependency. Errors are swallowed so the save step still runs.
    """
    title = f"Preview - THWS Post ({position})"
    try:
        preview_img = _build_preview(image, position, text, x, y)
        preview_img.show(title=title)
    except Exception as exc:
        print(f"[preview] could not display preview: {exc}")
