from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

class TextRenderer:
    # --- Epic B - Issue 3: Remove Hardcoded Font Size ---
    # Change: Removed the fixed font_size=78 from __init__.
    # Reason: A dynamic font size is now used instead of a fixed value to allow for 
    # automatic font scaling (auto-fit) based on available space.
    def __init__(self):
        pass

    # --- Epic B - Issue 3: Dynamic Font Loading ---
    # Change: Implemented dynamic font loading that accepts a custom font_name and falls back to defaults.
    # Reason: To accommodate custom user fonts and support dynamic resizing in the auto-fit loop.
    def load_font(self, font_name, size):
        if font_name:
            try:
                # Prioritize custom font
                return ImageFont.truetype(font_name, size)
            except OSError:
                print(f"Warning: Could not load custom font {font_name}, falling back to defaults.")

        project_root = Path(__file__).resolve().parents[3]

        font_paths = [
            # THWS Hausschrift (Open Sans Bold, served on thws.de) — default
            project_root / "assets" / "fonts" / "OpenSans-Bold.ttf",
            project_root / "assets" / "fonts" / "DejaVuSans-Bold.ttf",
            Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
            Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
            Path("C:/Windows/Fonts/arialbd.ttf"),
            Path("C:/Windows/Fonts/arial.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ]

        for font_path in font_paths:
            try:
                if font_path.exists():
                    return ImageFont.truetype(str(font_path), size)
            except OSError:
                continue

        print("No TrueType font found, using Pillow default font")
        return ImageFont.load_default()

    # --- Epic B - Issue 3: Dynamic Word Wrapping ---
    # Change: Removed the fixed 14-character line break rule. Replaced it with Pillow's textbbox method.
    # Reason: To calculate the actual pixel width of words and enable dynamic, smart word-wrapping.
    def wrap_text(self, text, font, max_width):
        words = text.split()
        lines = []
        current_line = ""

        # Dummy image to use textbbox
        dummy_img = Image.new("RGBA", (1, 1))
        draw = ImageDraw.Draw(dummy_img)

        for word in words:
            test_line = current_line + " " + word if current_line else word
            # Measure the test line
            bbox = draw.textbbox((0, 0), test_line, font=font)
            line_width = bbox[2] - bbox[0]

            if line_width > max_width:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    # Single word is longer than max_width, just append it
                    lines.append(word)
                    current_line = ""
            else:
                current_line = test_line

        if current_line:
            lines.append(current_line)

        return "\n".join(lines)

    # --- Shape-Aware Layout: helpers -------------------------------------
    # The renderer no longer fits text into one fixed rectangle. Instead the
    # mask is analyzed row band by row band, so every text line gets its own
    # maximum width based on the filled cells at that exact height. Holes in
    # the mask split a band into separate spans, so text can never cross them.

    def _cells_by_row(self, cells):
        """Group filled cell x-coordinates by their grid row."""
        rows = {}
        for x, y in cells:
            rows.setdefault(y, set()).add(x)
        return rows

    def _band_spans(self, top, bottom, rows, cell_size, offset):
        """Contiguous horizontal pixel spans that are fully covered by filled
        cells for the whole vertical pixel band [top, bottom).

        A band that touches several grid rows only keeps the columns present
        in ALL of them (intersection), so narrowing rows and holes both shrink
        or split the usable spans. Returns a list of (left, right) tuples.
        """
        ox, oy = offset
        gy_min = int((top - oy) // cell_size)
        gy_max = int((bottom - 1 - oy) // cell_size)

        common = None
        for gy in range(gy_min, gy_max + 1):
            cols = rows.get(gy)
            if not cols:
                return []
            common = set(cols) if common is None else common & cols
            if not common:
                return []

        spans = []
        for gx in sorted(common):
            left = ox + gx * cell_size
            right = left + cell_size
            if spans and spans[-1][1] == left:
                spans[-1][1] = right
            else:
                spans.append([left, right])
        return [(left, right) for left, right in spans]

    # --- Letter spacing (tracking) support --------------------------------
    # Pillow has no native letter-spacing, so when tracking != 0 lines are
    # measured and drawn character by character with an adjusted advance.

    def _char_widths(self, draw, text, font):
        """Per-character advance cache for one font instance."""
        cache = {}
        for ch in set(text):
            cache[ch] = draw.textlength(ch, font=font)
        return cache

    def _line_width(self, draw, line, font, tracking, char_cache=None):
        if tracking == 0:
            return draw.textlength(line, font=font)
        if char_cache is None:
            char_cache = self._char_widths(draw, line, font)
        width = sum(char_cache[ch] for ch in line)
        return width + tracking * max(0, len(line) - 1)

    def _draw_line(self, draw, x, y, line, font, tracking, char_cache, **kwargs):
        if tracking == 0:
            draw.text((x, y), line, font=font, **kwargs)
            return
        cursor = x
        for ch in line:
            draw.text((cursor, y), ch, font=font, **kwargs)
            cursor += char_cache[ch] + tracking

    def _fit_words(self, draw, words, start, font, max_width, force=False, tracking=0, char_cache=None):
        """Greedily pack words[start:] into max_width.

        Returns (word_count, line_text, line_width). With force=True a single
        word wider than max_width is still accepted (last-resort mode), so the
        layout always terminates.
        """
        line = words[start]
        width = self._line_width(draw, line, font, tracking, char_cache)
        if width > max_width and not force:
            return 0, "", 0
        count = 1
        while start + count < len(words):
            candidate = line + " " + words[start + count]
            cand_width = self._line_width(draw, candidate, font, tracking, char_cache)
            if cand_width > max_width:
                break
            line, width = candidate, cand_width
            count += 1
        return count, line, width

    def _line_height(self, draw, font):
        try:
            ascent, descent = font.getmetrics()
            return ascent + descent
        except AttributeError:
            bbox = draw.textbbox((0, 0), "Ag", font=font)
            return bbox[3] - bbox[1]

    def _layout_lines(self, draw, words, font, start_y, rows, cell_size, offset, target_cx, pad, line_gap, force=False, tracking=0, char_cache=None):
        """Place all words line by line starting at start_y.

        Every line is constrained to the mask columns available at its own
        height, so the resulting block follows the mask outline (trapezoid,
        stairs, ...) instead of a fixed rectangle. Lines stay aligned to
        target_cx whenever the shape allows it and are only shifted when the
        available span forces them sideways.

        Returns a list of (text, x, y, width, height) or None if the words do
        not fit starting at this position.
        """
        line_h = self._line_height(draw, font)
        placements = []
        y = start_y
        i = 0
        while i < len(words):
            spans = self._band_spans(y - pad, y + line_h + pad, rows, cell_size, offset)
            best = None
            for left, right in spans:
                avail = (right - left) - 2 * pad
                if avail <= 0:
                    continue
                count, line, width = self._fit_words(draw, words, i, font, avail, force, tracking, char_cache)
                if count == 0:
                    continue
                center = (left + right) / 2
                key = (count, avail, -abs(center - target_cx))
                if best is None or key > best[0]:
                    best = (key, left, right, count, line, width)
            if best is None:
                return None
            _, left, right, count, line, width = best
            lo = left + pad + width / 2
            hi = right - pad - width / 2
            if lo > hi:  # force mode: overlong single word, center it in the span
                line_cx = (left + right) / 2
            else:
                line_cx = min(max(target_cx, lo), hi)
            placements.append((line, line_cx - width / 2, y, width, line_h))
            i += count
            y += line_h + line_gap
        return placements

    def _fits_in_cells(self, w, h, cx, cy, cells, cell_size, offset, padding=20):
        left = cx - w / 2 - padding
        right = cx + w / 2 + padding
        top = cy - h / 2 - padding
        bottom = cy + h / 2 + padding
        
        ox, oy = offset
        
        min_grid_x = int((left - ox) // cell_size)
        max_grid_x = int((right - ox) // cell_size)
        min_grid_y = int((top - oy) // cell_size)
        max_grid_y = int((bottom - oy) // cell_size)
        
        filled = set(cells)
        
        for gy in range(min_grid_y, max_grid_y + 1):
            for gx in range(min_grid_x, max_grid_x + 1):
                if (gx, gy) not in filled:
                    return False
        return True

    # --- Shape-Aware Text Rendering ---
    # Change: Replaced the "maximum inscribed rectangle" fit with a per-line
    # mask analysis. The mask is scanned in horizontal bands; every text line
    # is wrapped and positioned against the filled cells at its own height.
    # Reason:
    # 1. The text block now follows the mask outline (trapezoid/stair shapes)
    #    instead of being squeezed into one fixed rectangle, so uneven masks
    #    (e.g. more room at the top than at the bottom) are used fully.
    # 2. Holes inside randomly generated masks split a band into separate
    #    spans, so no line can ever cross or overlap an empty cell.
    # 3. The largest font size that fits anywhere in the mask wins; among
    #    equal sizes the placement closest to the visual center is chosen.
    def draw_text_on_overlay(self, image, text, bounds, visual_center, cells, cell_size, offset, x_offset=0, y_offset=0, font_name=None, text_color="white", stroke_color=None, letter_spacing=0):
        result = image.copy()
        draw = ImageDraw.Draw(result)

        words = text.split()
        if not words or not cells:
            return result

        rows = self._cells_by_row(cells)
        ox, oy = offset
        mask_top = oy + min(y for _, y in cells) * cell_size
        mask_bottom = oy + (max(y for _, y in cells) + 1) * cell_size

        cx, cy = visual_center
        # x/y offsets bias the preferred position but the text is still kept
        # strictly inside the mask.
        target_cx = cx + x_offset
        target_cy = cy + y_offset

        max_font_size = 120
        min_font_size = 20
        step_y = max(8, cell_size // 8)

        chosen = None
        chosen_font = None
        chosen_stroke = 0
        chosen_tracking = 0
        chosen_cache = None

        for font_size in range(max_font_size, min_font_size - 1, -3):
            font = self.load_font(font_name, font_size)
            stroke_w = max(1, font_size // 25) if stroke_color else 0
            # Padding keeps text away from mask edges (the mask corners are
            # rounded by the blur in build_smooth_mask).
            pad = 15 + stroke_w
            line_gap = max(6, font_size // 8)
            tracking = font_size * letter_spacing / 100
            char_cache = self._char_widths(draw, text + " ", font) if tracking else None

            best = None
            start_y = int(mask_top + pad)
            while start_y < mask_bottom - pad:
                placements = self._layout_lines(
                    draw, words, font, start_y, rows, cell_size, offset,
                    target_cx, pad, line_gap, tracking=tracking, char_cache=char_cache,
                )
                if placements:
                    block_top = placements[0][2]
                    block_bottom = placements[-1][2] + placements[-1][4]
                    block_left = min(p[1] for p in placements)
                    block_right = max(p[1] + p[3] for p in placements)
                    block_cx = (block_left + block_right) / 2
                    block_cy = (block_top + block_bottom) / 2
                    penalty = abs(block_cy - target_cy) + 0.5 * abs(block_cx - target_cx)
                    if best is None or penalty < best[0]:
                        best = (penalty, placements)
                start_y += step_y

            if best:
                chosen = best[1]
                chosen_font = font
                chosen_stroke = stroke_w
                chosen_tracking = tracking
                chosen_cache = char_cache
                break

        if chosen is None:
            # Last resort: minimum font size, allow single overlong words.
            font = self.load_font(font_name, min_font_size)
            stroke_w = max(1, min_font_size // 25) if stroke_color else 0
            pad = 15 + stroke_w
            line_gap = max(6, min_font_size // 8)
            tracking = min_font_size * letter_spacing / 100
            char_cache = self._char_widths(draw, text + " ", font) if tracking else None
            start_y = int(mask_top + pad)
            while start_y < mask_bottom - pad and chosen is None:
                chosen = self._layout_lines(
                    draw, words, font, start_y, rows, cell_size, offset,
                    target_cx, pad, line_gap, force=True, tracking=tracking, char_cache=char_cache,
                )
                start_y += step_y
            chosen_font = font
            chosen_stroke = stroke_w
            chosen_tracking = tracking
            chosen_cache = char_cache

        if chosen is None:
            # Absolute fallback (degenerate masks): old-style centered block
            # clamped to the image, so the pipeline never crashes.
            return self._draw_fallback_block(result, draw, words, bounds, cx, cy, x_offset, y_offset, font_name, min_font_size, text_color, stroke_color)

        for line, x, y, _w, _h in chosen:
            kwargs = {"fill": text_color}
            if stroke_color:
                kwargs["stroke_width"] = chosen_stroke
                kwargs["stroke_fill"] = stroke_color
            self._draw_line(draw, x, y, line, chosen_font, chosen_tracking, chosen_cache, **kwargs)

        return result

    def _draw_fallback_block(self, result, draw, words, bounds, cx, cy, x_offset, y_offset, font_name, font_size, text_color, stroke_color):
        """Centered multiline fallback used only when the mask has no usable
        band at all (e.g. degenerate test masks smaller than one line)."""
        font = self.load_font(font_name, font_size)
        max_width = max(50, (bounds[2] - bounds[0]) * 0.9) if bounds else 300
        formatted_text = self.wrap_text(" ".join(words), font, max_width)

        bbox = draw.multiline_textbbox((0, 0), formatted_text, font=font, spacing=8)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        img_w, img_h = result.size
        x = max(0, min(cx - text_w / 2 + x_offset, img_w - text_w))
        y = max(0, min(cy - text_h / 2 + y_offset, img_h - text_h))

        kwargs = {
            "xy": (x, y),
            "text": formatted_text,
            "fill": text_color,
            "font": font,
            "spacing": 8,
            "align": "center",
        }
        if stroke_color:
            kwargs["stroke_width"] = max(1, font_size // 25)
            kwargs["stroke_fill"] = stroke_color
        draw.multiline_text(**kwargs)
        return result