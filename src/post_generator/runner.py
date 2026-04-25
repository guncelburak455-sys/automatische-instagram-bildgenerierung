from .cli import parse_args
from .app import generate_post


def main():
    config = parse_args()
    generate_post(config)


if __name__ == "__main__":
    main()