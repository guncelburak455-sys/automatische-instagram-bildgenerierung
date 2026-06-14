# 📸 IG-Bild-Gen — Automatic Instagram Post Generator

> A Python CLI tool that turns campus photos into THWS-branded, Instagram-ready posts in seconds.

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/Pillow-Image%20Processing-orange.svg)](https://python-pillow.org/)

---

## 📖 Overview

**IG-Bild-Gen** is a Python-based command-line tool that automatically generates Instagram-ready images (**1080×1350 px, 4:5 aspect ratio**) for THWS social media.

The tool takes an input photo, crops it to the correct format, overlays a smooth THWS-branded orange "motive" shape, adds custom text with precise positioning, and exports a ready-to-upload PNG — all in a single command.

Recently refactored into a clean, modular architecture, this project removes manual design work from the social media workflow and ensures a **consistent visual identity** across all THWS Instagram posts.

---

## 🎬 Demo

> Place your demonstration GIF as `demo.gif` in the root folder to display it here.

![Demo](demo.gif)

**Example use case:** Generating a series of "International THWS" posts — e.g. campus photos combined with text like *"Study in Germany"*, *"Applications now open"*, or student spotlight quotes — all with a consistent orange overlay and THWS branding.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🖼️ **Automatic Cropping** | Resizes and crops any input image to the standard Instagram portrait format (4:5) |
| 🟧 **THWS-branded Overlay** | Automatically applies a smoothly generated mask with the orange THWS motive shape |
| 📍 **Flexible Positioning** | Choose from 4 corners — `top-left`, `top-right`, `bottom-left`, `bottom-right` |
| ✏️ **Custom Text Rendering** | Add your own text directly inside the motive |
| 🎯 **Adjustable Text Coordinates** | Fine-tune text placement with custom X/Y offsets |
| 🧩 **Modular Architecture** | Clean, maintainable codebase using dataclasses and separated service layers |
| ⚡ **CLI Integration** | Simple, scriptable command-line interface |

---

## 🛠️ Tech Stack

- **Python 3.x**
- **[Pillow (PIL)](https://python-pillow.org/)** — core image processing library
- **argparse** — command-line argument handling

---

## 📁 Project Structure

```
.
├── main.py                       # Entry point for direct execution
├── pyproject.toml                # Package configuration & dependencies
├── requirements.txt              # Standard dependency list
└── src/
    └── post_generator/           # Main package
        ├── app.py                # Core application logic
        ├── cli.py                # CLI argument parsing
        ├── config.py             # Dataclass for configuration
        ├── runner.py             # Package runner script
        └── services/             # Image processing services
            ├── composition.py    # Image composition
            ├── mask.py           # Mask generation
            ├── post_generator.py # Utilities (cropping, grid logic)
            ├── textrenderer.py   # Text drawing logic
            └── transform.py      # Position and transformation logic
```

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone <repo-url>
cd automatische-instagram-bildgenerierung-2
```

### 2. Install dependencies

Using `requirements.txt`:

```bash
pip install -r requirements.txt
```

Or, since the project supports standard packaging via `pyproject.toml`, install it as a local package:

```bash
pip install -e .
```

---

## 💻 Usage

### Run directly with `main.py`

```bash
python main.py --photo campus.jpg --position bottom-left --text "Waseda University" --x 20 --y 40
```

### Run via the installed command (after `pip install -e .`)

```bash
ig_bild --photo campus.jpg --position top-right --text "THWS Partner" --x 30 --y 50 --output_name custom_output.png
```

---

## ⚙️ Parameters

| Parameter | Description | Default | Required |
|---|---|---|---|
| `--photo` | Path to the input image file | `None` | ✅ Yes |
| `--position` | Motive corner: `top-left`, `top-right`, `bottom-left`, `bottom-right` | `None` | ✅ Yes |
| `--text` | Text to be displayed inside the motive | `None` | ✅ Yes |
| `--x` | Horizontal (X) offset for the text | `0` | ❌ No |
| `--y` | Vertical (Y) offset for the text | `0` | ❌ No |
| `--output_path` | Directory path where the generated image will be saved | `.` (current dir) | ❌ No |
| `--output_name` | Filename of the generated image | `output.png` | ❌ No |

---

## 📤 Output

- **Format:** PNG
- **Aspect Ratio:** 4:5 (standard Instagram portrait)
- **Design:** Cropped input image with the THWS overlay and custom text applied

---

## ⚠️ Error Handling

- **Invalid Image Path** — Raises an error if the specified input photo cannot be found
- **Missing Required Parameters** — The CLI automatically displays usage instructions
- **Unsupported Position** — Prevented via `argparse` choices, restricting input to valid corner values

---

## 👥 Authors

- Mhd Zaher Shaiban
- Burak Ince
- Orik Mazreku
- Abdullah Aydin Lüleci

---

## 📌 Project

Developed as part of **Programmierprojekte Braun 2026SS** — *Automatische Instagram-Bildgenerierung 2* — THWS.
---

## Authors

* Mhd Zaher Shaiban
* Burak Ince
* Orik Mazreku
* Abdullah Aydin Lüleci
