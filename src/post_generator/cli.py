import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

from .config import Config


POSITIONS = ["bottom-left", "bottom-right", "top-left", "top-right", "left", "right", "random"]

# hex color format for the overlay mask, e.g. #FF8400 or #0077B6
HEX_COLOR_RE = re.compile(r"#[0-9a-fA-F]{6}")


def is_hex_color(value: str) -> bool:
    return bool(HEX_COLOR_RE.fullmatch(value))


def generate_output_name() -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"post_{timestamp}.png"


def ask_with_default(question: str, default: str | None = None) -> str:
    if default is not None:
        value = input(f"{question} [{default}]: ").strip()
        return value if value else default

    return input(f"{question}: ").strip()


def ask_yes_no(question: str, default: bool = False) -> bool:
    default_text = "yes" if default else "no"
    value = ask_with_default(question, default_text).lower()

    return value in ["yes", "y", "true", "1"]


def interactive_mode() -> Config:
    print("Interactive Instagram Post Generator")
    print("------------------------------------")

    photo = ask_with_default("Image path")
    while not Path(photo).is_file():
        print("Image not found. Please enter a valid image path.")
        photo = ask_with_default("Image path")

    text = ask_with_default("Text")
    while not text:
        print("Text cannot be empty.")
        text = ask_with_default("Text")

    print("Available positions:")
    for position in POSITIONS:
        print(f"- {position}")

    position = ask_with_default("Position", "bottom-right")
    while position not in POSITIONS:
        print("Invalid position. Please choose one of:")
        print(", ".join(POSITIONS))
        position = ask_with_default("Position", "bottom-right")

    x = ask_with_default("X offset", "0")
    while not x.lstrip("-").isdigit():
        print("X offset must be a number.")
        x = ask_with_default("X offset", "0")

    y = ask_with_default("Y offset", "0")
    while not y.lstrip("-").isdigit():
        print("Y offset must be a number.")
        y = ask_with_default("Y offset", "0")

    output_path = ask_with_default("Output folder", ".")
    output_name = ask_with_default("Output filename", generate_output_name())

    preview = ask_yes_no("Open preview?", False)

    font = ask_with_default("Custom font path", "")
    font = font if font else None

    text_color = ask_with_default("Text color", "white")

    stroke_color = ask_with_default("Stroke color", "")
    stroke_color = stroke_color if stroke_color else None

    mask_color = ask_with_default("Mask color (hex, empty keeps THWS orange)", "")
    while mask_color and not is_hex_color(mask_color):
        print("Mask color must be a hex code like #FF8400 or #0077B6.")
        mask_color = ask_with_default("Mask color (hex, empty keeps THWS orange)", "")
    mask_color = mask_color if mask_color else None

    return Config(
        photo=photo,
        position=position,
        text=text,
        x=int(x),
        y=int(y),
        output_path=output_path,
        output_name=output_name,
        preview=preview,
        font=font,
        text_color=text_color,
        stroke_color=stroke_color,
        mask_color=mask_color,
    )


def parse_args() -> Config:
    """Parse command-line arguments and return a Config object."""

    if len(sys.argv) == 1:
        return interactive_mode()

    parser = argparse.ArgumentParser(
        description=(
            "Generate a THWS-branded Instagram post.\n\n"
            "Examples:\n"
            "  python3 main.py --photo campus.jpg --position top-right --text \"THWS Partner\"\n"
            "  python3 main.py --photo campus.jpg --position random --text \"Campus Life\" --preview\n"
            "  python3 main.py --photo campus.jpg --position bottom-left --text \"Waseda University\" --x 20 --y 40\n"
            "  python3 main.py --photo campus.jpg --position top-right --text \"THWS\" --output_path outputs\n"
            "  python3 main.py --photo campus.jpg --position top-right --text \"THWS\" --font assets/fonts/DejaVuSans-Bold.ttf --text_color white --stroke_color black\n"
            "  python3 main.py --photo campus.jpg --position top-right --text \"THWS\" --mask_color \"#0077B6\"\n\n"
            "Interactive mode:\n"
            "  python3 main.py\n\n"
            "Available positions:\n"
            "  bottom-left, bottom-right, top-left, top-right, left, right, random"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument("--photo", required=True, help="Path to the input image file, e.g. campus.jpg")
    parser.add_argument(
        "--position",
        required=True,
        choices=POSITIONS,
        help="Position for the motive: bottom-left, bottom-right, top-left, top-right, left, right, random"
    )
    parser.add_argument("--text", required=True, help="Text inside of the motive")
    parser.add_argument("--x", type=int, default=0, help="Horizontal text offset in pixels")
    parser.add_argument("--y", type=int, default=0, help="Vertical text offset in pixels")
    parser.add_argument("--output_path", required=False, default=".", help="Output folder")
    parser.add_argument(
        "--output_name",
        required=False,
        default=None,
        help="Output filename. If omitted, one is generated automatically."
    )

    parser.add_argument(
        "--preview",
        dest="preview",
        action="store_true",
        help="Open a preview window of the generated image before saving"
    )

    parser.add_argument("--font", required=False, default=None, help="Path to a custom TrueType font file (.ttf)")
    parser.add_argument("--text_color", required=False, default="white", help="Color of the text, e.g. 'red' or '#FFFFFF'")
    parser.add_argument("--stroke_color", required=False, default=None, help="Optional color for the text outline, e.g. 'black'")
    parser.add_argument(
        "--mask_color",
        required=False,
        default=None,
        help="Hex color for the overlay mask, e.g. '#0077B6'. Defaults to THWS orange (#FF8400)."
    )

    args = parser.parse_args()

    if not Path(args.photo).is_file():
        parser.error(f"Image not found: {args.photo}")

    if args.font and not Path(args.font).is_file():
        parser.error(f"Font file not found: {args.font}")

    if args.mask_color and not is_hex_color(args.mask_color):
        parser.error(f"Invalid mask color: {args.mask_color}. Use a hex code like #FF8400 or #0077B6.")

    output_name = args.output_name if args.output_name else generate_output_name()

    return Config(
        photo=args.photo,
        position=args.position,
        text=args.text,
        x=args.x,
        y=args.y,
        output_path=args.output_path,
        output_name=output_name,
        preview=args.preview,
        font=args.font,
        text_color=args.text_color,
        stroke_color=args.stroke_color,
        mask_color=args.mask_color,
    )