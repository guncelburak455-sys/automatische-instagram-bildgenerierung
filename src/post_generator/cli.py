import argparse
import sys
from datetime import datetime
from pathlib import Path

from .config import Config


POSITIONS = ["bottom-left", "bottom-right", "top-left", "top-right"]


def generate_output_name() -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"post_{timestamp}.png"


def ask_with_default(question: str, default: str | None = None) -> str:
    if default:
        value = input(f"{question} [{default}]: ").strip()
        return value if value else default

    return input(f"{question}: ").strip()


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

    return Config(
        photo=photo,
        position=position,
        text=text,
        x=int(x),
        y=int(y),
        output_path=output_path,
        output_name=output_name,
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
            "  python3 main.py --photo campus.jpg --position bottom-left --text \"Waseda University\" --x 20 --y 40\n"
            "  python3 main.py --photo campus.jpg --position top-right --text \"THWS\" --output_path outputs --output_name post.png\n\n"
            "Interactive mode:\n"
            "  python3 main.py\n\n"
            "Available positions:\n"
            "  top-left, top-right, bottom-left, bottom-right"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--photo",
        required=True,
        help="Path to the input image file, e.g. campus.jpg"
    )
    parser.add_argument(
        "--position",
        required=True,
        choices=POSITIONS,
        help="Position of the orange motive: top-left, top-right, bottom-left, bottom-right"
    )
    parser.add_argument(
        "--text",
        required=True,
        help="Text that will be placed inside the orange motive"
    )
    parser.add_argument(
        "--x",
        type=int,
        default=0,
        help="Horizontal text offset in pixels, e.g. 20"
    )
    parser.add_argument(
        "--y",
        type=int,
        default=0,
        help="Vertical text offset in pixels, e.g. 40"
    )
    parser.add_argument(
        "--output_path",
        required=False,
        default=".",
        help="Output folder, default is current folder"
    )
    parser.add_argument(
        "--output_name",
        required=False,
        default=None,
        help="Output filename. If not provided, a filename is generated automatically."
    )

    args = parser.parse_args()

    if not Path(args.photo).is_file():
        parser.error(f"Image not found: {args.photo}")

    output_name = args.output_name if args.output_name else generate_output_name()

    return Config(
        photo=args.photo,
        position=args.position,
        text=args.text,
        x=args.x,
        y=args.y,
        output_path=args.output_path,
        output_name=output_name,
    )
