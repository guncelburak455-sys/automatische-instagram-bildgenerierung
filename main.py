import argparse


def main():
    parser = argparse.ArgumentParser(                                   # creates the parses object
        description="Generate a THWS-branded Instagram Post!"
                    "The general and recommended order of commands is the following:"       # text when running "main.py --help"
                    "py main.py --photo PHOTO --position POSITION --text TEXT --x X --y Y --output_path OUTPUT_PATH --output_name OUTPUT_NAME"
    )

    # Registering all required parameters for our script:
    #               - photo, position, text, x, y
    #               - the 1. parameter is the name the user types in the terminal
    #               - the 2. parameters makes argparse stop and print an error in case it is forgotten
    #               - the 3. parameter is the explanation shown if --help is run

    parser.add_argument("--photo", required=True, help="Path to the input photo")
    parser.add_argument("--position", required=True, choices=["bottom-left", "bottom-right", "top-left", "top-right"], help="Corner for the motive")
    parser.add_argument("--text", required=True, help="Text inside of the motive")

    # type=int to convert "20" as a string to the integer 20 ; default value is set to 0 (could change later on based on algorithm for motive)
    parser.add_argument("--x", type=int, default=0, help="Horizontal position of the text in the motive")
    parser.add_argument("--y", type=int, default=0, help="Vertical position of the text in the motive")

    parser.add_argument("--output_path", required=False, help="Path to the output file")
    parser.add_argument("--output_name", required=False, default="output.png", help="Name of the output file")

    # reads what the user types in the terminal and fills all required and not required values given
    args = parser.parse_args()

    # replacing the attributes/parameters with the actual values set by the user at runtime
    print(f"Photo: {args.photo}")
    print(f"Position: {args.position}")
    print(f"Text: {args.text}")
    print(f"X: {args.x}")
    print(f"Y: {args.y}")
    print(f"Output path: {args.output_path}")
    print(f"Output name: {args.output_name}")


if __name__ == "__main__":
    main()