import argparse
from .config import Config
def parse_args() -> Config:
    """Parse command-line arguments and return a Config object."""
    parser = argparse.ArgumentParser(
        description="Generate a THWS-branded Instagram Post!\n"
                    "The general and recommended order of commands is the following:\n"
                    "py main.py --photo PHOTO --position POSITION --text TEXT --x X --y Y --output_path OUTPUT_PATH --output_name OUTPUT_NAME"
    )

    parser.add_argument("--photo", required=True, help="Path to the input photo")
    parser.add_argument("--position", required=True, choices=["bottom-left", "bottom-right", "top-left", "top-right", "random"], help="Corner for the motive")
    parser.add_argument("--text", required=True, help="Text inside of the motive")
    parser.add_argument("--x", type=int, default=0, help="Horizontal position of the text in the motive")
    parser.add_argument("--y", type=int, default=0, help="Vertical position of the text in the motive")
    parser.add_argument("--output_path", required=False, help="Path to the output file")
    parser.add_argument("--output_name", required=False, default="output.png", help="Name of the output file")
    # --preview flag update in Sprint 1 for UX Isses/User Stories
    parser.add_argument("--preview", dest="preview", action="store_true", help="Open a preview window of the generated image before saving")
    
    # --- Epic B - Issue 1: Text Styling CLI Args ---
    # Change: Added --font, --text_color, and --stroke_color command line arguments.
    # Reason: To provide flexibility and allow external text styling instead of hardcoded values.
    # If these arguments are omitted, sensible default values will be applied via Config.
    parser.add_argument("--font", required=False, default=None, help="Path to a custom TrueType font file (.ttf)")
    parser.add_argument("--text_color", required=False, default="white", help="Color of the text (e.g., 'red', '#FFFFFF'). Defaults to white.")
    parser.add_argument("--stroke_color", required=False, default=None, help="Optional color for the text outline (e.g., 'black').")
    args = parser.parse_args()

    return Config(
        photo=args.photo,
        position=args.position,
        text=args.text,
        x=args.x,
        y=args.y,
        output_path=args.output_path,
        output_name=args.output_name,
        preview=args.preview,
        font=args.font,
        text_color=args.text_color,
        stroke_color=args.stroke_color,
    )
