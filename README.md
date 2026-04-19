# Automatic Instagram Post Generator

## - Overview

IG_Bild_Gen is a Python-based command-line tool that automatically generates Instagram-ready images (1080×1080 px PNG) for THWS.

The tool takes an input photo, overlays a THWS-branded orange motive shape, adds custom text, and exports a ready-to-upload image.

This project aims to reduce manual effort and ensure a consistent visual design for social media posts.

---

## - Features

* Automatic image resizing to Instagram format (1080×1080 px)
* THWS-branded overlay (orange motive)
* Custom text rendering
* Flexible positioning (4 corners)
* Adjustable text coordinates
* Reproducible results using seed
* PNG export ready for upload

---

## - Tech Stack

* **Python**
* **Pillow** – image processing
* **argparse** – CLI parameter handling
* **random** – procedural shape generation
* **numpy** (optional)

---

## - Project Structure

```
IG_Bild_Gen/
│
├── IG_Bild_Gen.py       # Main script
├── requirements.txt     # Dependencies
├── README.md            # Documentation
└── examples/            # Example input/output images
```

---

## - Installation

### 1. Clone the repository

```bash
git clone <repo-url>
cd IG_Bild_Gen
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

## - Usage

Run the tool from the command line:

```bash
python IG_Bild_Gen.py --photo campus.jpg --position bottom-left --text "Waseda University" --x 20 --y 40
```

---

## - Parameters

| Parameter    | Description                                                     |
| ------------ | --------------------------------------------------------------- |
| `--photo`    | Path to input image (required)                                  |
| `--position` | Motive position: top-left, top-right, bottom-left, bottom-right |
| `--text`     | Text displayed inside the motive                                |
| `--x`        | X coordinate of the text                                        |
| `--y`        | Y coordinate of the text                                        |
| `--seed`     | Optional seed for reproducible shape                            |
| `--output`   | Output file path (default: output.png)                          |

---

## - Output

* Format: PNG
* Size: 1080×1080 px
* Ready for Instagram upload

---

## - Error Handling

* Invalid or missing image path → clear error message
* Unsupported position → validation error
* Missing required parameters → CLI help

---

## - Example

### Input

```bash
python IG_Bild_Gen.py --photo campus.jpg --position top-right --text "THWS Partner" --x 30 --y 50
```

### Output

* File: `output.png`
* Image with THWS overlay and text

---

## - Future Improvements

* Advanced motive shape generation
* Automatic text scaling
* Batch processing (multiple posts)
* Web interface
* Template system for different layouts

---

## - Authors

* Mhd Zaher Shaiban
* Burak Ince
* Orik Mazreku
* Abdullah Aydin Lüleci

---


