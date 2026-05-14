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

    # --- Epic B - Issue 2 & 3: Smart Text Rendering & Visual Center Integration ---
    # Change:
    # 1. Removed old hardcoded bias/bounds logic, replacing it with visual_center and a max inscribed rectangle fit algorithm.
    # 2. Added an 'auto-fit loop' that progressively shrinks the font_size until it fits within max_width.
    # 3. Added optional stroke_color (outline) support to improve text readability against the background.
    # Reason: To resolve text overflow issues with long texts and ensure perfect centering across all corners.
    def draw_text_on_overlay(self, image, text, bounds, visual_center, cells, cell_size, offset, x_offset=0, y_offset=0, font_name=None, text_color="white", stroke_color=None):
        result = image.copy()
        draw = ImageDraw.Draw(result)
        
        cx, cy = visual_center
        
        # Dynamically calculate the maximum inscribed rectangle centered at cx, cy that fits in the mask
        best_w = 100
        best_h = 100
        max_area = 0
        
        # Test various heights to find the bounding box with the maximum area
        for h in range(50, 1500, 25):
            if not self._fits_in_cells(10, h, cx, cy, cells, cell_size, offset, padding=0):
                continue
                
            low = 10
            high = 1500
            w = low
            while low <= high:
                mid = (low + high) // 2
                if self._fits_in_cells(mid, h, cx, cy, cells, cell_size, offset, padding=0):
                    w = mid
                    low = mid + 1
                else:
                    high = mid - 1
                    
            area = w * h
            if area > max_area:
                max_area = area
                best_w = w
                best_h = h
                
        # Use 90% of the best fit rectangle for text boundaries to leave a small padding
        max_width = best_w * 0.90
        max_height = best_h * 0.90
        
        # Auto-fit loop
        font_size = 120
        min_font_size = 20
        
        font = self.load_font(font_name, font_size)
        formatted_text = self.wrap_text(text, font, max_width)
        
        while font_size > min_font_size:
            bbox = draw.multiline_textbbox((0, 0), formatted_text, font=font, spacing=8)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            
            # Check if it fits the calculated max bounds AND perfectly fits in the cells (double check)
            if text_w <= max_width and text_h <= max_height and self._fits_in_cells(text_w, text_h, cx, cy, cells, cell_size, offset, padding=10):
                break
                
            font_size -= 2
            font = self.load_font(font_name, font_size)
            formatted_text = self.wrap_text(text, font, max_width)
            
        # Re-measure in case loop exited at min_font_size
        bbox = draw.multiline_textbbox((0, 0), formatted_text, font=font, spacing=8)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        img_w, img_h = image.size
        x = cx - text_w / 2 + x_offset
        y = cy - text_h / 2 + y_offset
        
        # Prevent text from going entirely off-screen
        x = max(0, min(x, img_w - text_w))
        y = max(0, min(y, img_h - text_h))

        kwargs = {
            "xy": (x, y),
            "text": formatted_text,
            "fill": text_color,
            "font": font,
            "spacing": 8,
            "align": "center"
        }
        
        if stroke_color:
            kwargs["stroke_width"] = max(1, font_size // 25)
            kwargs["stroke_fill"] = stroke_color

        draw.multiline_text(**kwargs)

        return result