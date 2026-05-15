from .cli import parse_args
from .app import generate_post


def main():
    try:
        config = parse_args()
        generate_post(config)

    except FileNotFoundError as error:
        print("Image not found. Please check the file path.")
        print(f"Details: {error}")
        return 1

    except ValueError as error:
        print("Invalid input. Please check your values.")
        print(f"Details: {error}")
        return 1

    except KeyboardInterrupt:
        print("\nProgram cancelled by user.")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())