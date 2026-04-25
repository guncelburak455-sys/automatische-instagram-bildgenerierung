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
    parser.add_argument("--position", required=True, choices=["bottom-left", "bottom-right", "top-left", "top-right"], help="Corner for the motive")
    parser.add_argument("--text", required=True, help="Text inside of the motive")
    parser.add_argument("--x", type=int, default=0, help="Horizontal position of the text in the motive")
    parser.add_argument("--y", type=int, default=0, help="Vertical position of the text in the motive")
    parser.add_argument("--output_path", required=False, help="Path to the output file")
    parser.add_argument("--output_name", required=False, default="output.png", help="Name of the output file")

    args = parser.parse_args()

    return Config(
        photo=args.photo,
        position=args.position,
        text=args.text,
        x=args.x,
        y=args.y,
        output_path=args.output_path,
        output_name=args.output_name
    )
