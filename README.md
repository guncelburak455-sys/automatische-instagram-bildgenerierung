# Automatic Instagram Post Generator (ig-bild)

## Overview

**IG_Bild_Gen** is a Python-based command-line tool that automatically generates Instagram-ready images (1080×1350 px, 4:5 aspect ratio) for THWS. 

The tool takes an input photo, crops it appropriately, overlays a THWS-branded orange motive shape, adds custom text with precise positioning, and exports a ready-to-upload image. Recently refactored into a clean, modular architecture, this project aims to reduce manual effort and ensure a consistent visual design for social media posts.

### Demo

![How it works](demo.gif)
*(Please place your demonstration GIF as `demo.gif` in the root folder to display it here.)*

---

## Features

* **Automatic Image Cropping**: Resizes and crops the image to the standard Instagram portrait format (4:5).
* **THWS-branded Overlay**: Automatically applies a smoothly generated mask and orange motive.
* **Flexible Positioning**: Choose from 4 corners (`top-left`, `top-right`, `bottom-left`, `bottom-right`) or the wide side overlays (`left`, `right`) for the overlay.
* **Custom Text Rendering**: Add your own text inside the motive.
* **Adjustable Text Coordinates**: Fine-tune the text placement with custom X and Y offsets.
* **Modular Architecture**: Clean, maintainable codebase utilizing `dataclasses` and separated service layers.
* **CLI Integration**: Easy-to-use command-line interface.

---

## Tech Stack

* **Python 3.x**
* **Pillow (PIL)** – Core image processing library.
* **argparse** – Command-line parameter handling.

---

## Project Structure

The project has been structured into a modern Python package:

```text
.
├── main.py                    # Entry point for direct execution
├── pyproject.toml             # Package configuration & dependencies
├── requirements.txt           # Standard dependency list
└── src/
    └── post_generator/        # Main package
        ├── app.py             # Core application logic
        ├── cli.py             # CLI argument parsing
        ├── config.py          # Dataclass for configuration
        ├── runner.py          # Package runner script
        └── services/          # Image processing services
            ├── composition.py # Image composition
            ├── mask.py        # Mask generation
            ├── post_generator.py # Utilities (cropping, grid logic)
            ├── textrenderer.py # Text drawing logic
            └── transform.py   # Position and transformation logic
```

---

## Installation

### 1. Clone the repository

```bash
git clone <repo-url>
cd automatische-instagram-bildgenerierung-2
```

### 2. Install dependencies

You can install the requirements via `requirements.txt`:

```bash
pip install -r requirements.txt
```

Alternatively, since this project supports standard packaging (via `pyproject.toml`), you can install it as a local package:

```bash
pip install -e .
```

---

## Usage

### Using `main.py` directly

```bash
python main.py --photo campus.jpg --position bottom-left --text "Waseda University" --x 20 --y 40
```

### Using the installed command (if installed via `pip install -e .`)

```bash
ig_bild --photo campus.jpg --position top-right --text "THWS Partner" --x 30 --y 50 --output_name custom_output.png
```

---

## Parameters

| Parameter       | Description                                                          | Default Value | Required |
| --------------- | -------------------------------------------------------------------- | ------------- | -------- |
| `--photo`       | Path to the input image file                                         | None          | Yes      |
| `--position`    | Motive position (`top-left`, `top-right`, `bottom-left`, `bottom-right`, `left`, `right`) | None          | Yes      |
| `--text`        | Text to be displayed inside the motive                               | None          | Yes      |
| `--x`           | Horizontal (X) offset for the text                                   | `0`           | No       |
| `--y`           | Vertical (Y) offset for the text                                     | `0`           | No       |
| `--output_path` | Directory path where the generated image will be saved               | `.` (Current) | No       |
| `--output_name` | Filename of the generated image                                      | `output.png`  | No       |

---

## Output

* **Format**: PNG
* **Aspect Ratio**: 4:5 (Standard Instagram Portrait)
* **Design**: Cropped image with the THWS overlay and customized text.

---

## Error Handling

* **Invalid Image Path**: Throws an error if the specified input photo cannot be found.
* **Missing Required Parameters**: The CLI will automatically prompt with usage instructions.
* **Unsupported Position**: Handled via `argparse` choices to prevent invalid inputs.

---

## Authors

* Mhd Zaher Shaiban
* Burak Ince
* Orik Mazreku
* Abdullah Aydin Lüleci
