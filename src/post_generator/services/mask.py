from PIL import Image, ImageDraw, ImageFilter

# builds a smooth anti-aliased mask
# white regions in the mask = orange overlay
# black regions = photo shows through

def build_smooth_mask(size, cells, cell, offset):
    # draw at 4x resolution then shrink, so edges come out smooth
    scale = 4
    big_size = (size[0] * scale, size[1] * scale)
    mask = Image.new("L", big_size, 0)
    draw = ImageDraw.Draw(mask)                 # creates a drawing context attached to the mask image.

    ox, oy = offset                 # unpacks the offset tuple into : ox (horizontal offset) and oy (vertical offset)
    big_cell = cell * scale

    for x, y in cells:
        px = (ox + x * cell) * scale
        py = (oy + y * cell) * scale
        draw.rectangle(
            [px, py, px + big_cell, py + big_cell],             # draws the white rectangle where the mask is supposed to be with white
            fill=255,
        )

    blur_radius = max(8, big_cell // 8)                                      # blur first to soften the hard cell edges
    mask = mask.filter(ImageFilter.GaussianBlur(radius=blur_radius))        # turns the hard edges into soft transitions
    mask = mask.point(lambda p: 255 if p > 100 else 0)
    return mask.resize(size, Image.LANCZOS)                             # shrinks the oversized mask back down to the final image dimensions
                                                                        # using the Lanczos algorithm