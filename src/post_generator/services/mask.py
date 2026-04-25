from PIL import Image, ImageDraw, ImageFilter


def build_smooth_mask(size, cells, cell, offset):
    scale = 4
    big_size = (size[0] * scale, size[1] * scale)
    mask = Image.new("L", big_size, 0)
    draw = ImageDraw.Draw(mask)

    ox, oy = offset
    big_cell = cell * scale

    for x, y in cells:
        px = (ox + x * cell) * scale
        py = (oy + y * cell) * scale
        draw.rectangle(
            [px, py, px + big_cell, py + big_cell],
            fill=255,
        )

    blur_radius = max(8, big_cell // 8)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    mask = mask.point(lambda p: 255 if p > 100 else 0)
    return mask.resize(size, Image.LANCZOS)
