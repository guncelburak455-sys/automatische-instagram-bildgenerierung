from PIL import Image, ImageDraw, ImageFont

# tries to load Arial Bold ; if it's not installed on the system, falls back to regular arial ; if also missing, fall back to pillow built-in font
class TextRenderer:
    def __init__(self, font_size=78):
        self.font_size = font_size

    def load_font(self):
        font_path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

        try:
            print(f"Loading font from: {font_path}")
            return ImageFont.truetype(font_path, self.font_size)
        except OSError:
            print("Arial Bold not found, using Helvetica")
            return ImageFont.truetype(
                "/System/Library/Fonts/Supplemental/Arial.ttf",
                self.font_size
            )


# word-wrapping function ; splits the text into words, then builds lines one word at a time. if adding the next word would push the line past 14
# characters, it starts a new line instead
    def format_text(self, text):
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + " " + word if current_line else word

            # smaller line width so text breaks earlier
            if len(test_line) > 14:                             # 14 chars fits the overlay width at fant size 78 ; change this if you change the font size
                if current_line:
                    lines.append(current_line)
                current_line = word
            else:
                current_line = test_line

        if current_line:
            lines.append(current_line)

        return "\n".join(lines)

    def draw_text_on_overlay(self, image, text, bounds, position="", x_offset=0, y_offset=0):
        # 1. Copy the image so we don't draw on the original
        # 2. Format the text using format_text()
        # 3. Measure the text with multiline_textbox to get the width and height
        # 4. Find the center of the orange shape, using the bounds rectangle that was passed in
        # 5. Apply a position-dependent moving-value
        # 6. Manual offsets
        # 7. Draw the text in white using multiline_text with align="center"
        result = image.copy()
        draw = ImageDraw.Draw(result)
        font = self.load_font()

        left, top, right, bottom = bounds       # (left, top, irght, bottom) rectangle of the orange overlay

        formatted_text = self.format_text(text)

        bbox = draw.multiline_textbbox((0, 0), formatted_text, font=font, spacing=8)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        # calculating the center of the overlay where the text will go
        cx = (left + right) / 2
        cy = (top + bottom) / 2

        mask_w = right - left
        mask_h = bottom - top
        #nudge text away from the pointed corner of the shape - each position is slightly different because the shape isn't symmetric
        if position == "top-left":
            bias_x = mask_w * -0.18
        elif position == "top-right":
            bias_x = mask_w * 0.16
        elif position == "bottom-left":
            bias_x = mask_w * -0.08
        elif position == "bottom-right":
            bias_x = mask_w * 0.08
        else:
            bias_x = 0
        bias_y = mask_h * 0.10 * (1 if "bottom" in position else -1 if "top" in position else 0)      # shift text toward the center of the shape vertically

        img_w, img_h = image.size
        x = cx - text_w / 2 + bias_x + x_offset
        y = cy - text_h / 2 + bias_y + y_offset
        x = max(0, min(x, img_w - text_w))
        y = max(0, min(y, img_h - text_h))

# renders the formatted text onto the image at the calculated position
        draw.multiline_text(
            (x, y),
            formatted_text,
            fill=(255, 255, 255, 255),
            font=font,
            spacing=8,
            align="center"
        )

        return result