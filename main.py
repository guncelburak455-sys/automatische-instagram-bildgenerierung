from src.post_generator.cli import parse_args
from src.post_generator.app import generate_post

def main():
    config = parse_args()
    generate_post(config)

if __name__ == "__main__":
    main()