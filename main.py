from src.post_generator.cli import parse_args           # imports the command-line argumts
from src.post_generator.app import generate_post        # imports the core function that builds and saves the Instagram post image

# main function
def main():
    config = parse_args()       # reads the arguments the user hash types in the terminal ; object is stored in config.py file
    generate_post(config)       # calls generate_post, passing config to it.

if __name__ == "__main__":
    main()