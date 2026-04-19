import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Generate an Instagram image"
    )

    parser.parse_args()

    print("CLI initialized successfully.")


if __name__ == "__main__":
    main()