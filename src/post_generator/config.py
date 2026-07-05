from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """acts as a container that holds all the settings needed to generate the instagram post"""
    photo: str
    position: str
    text: str
    x: int          # pixel offsets from the auto-calculated text center
    y: int
    output_path: Optional[str] = None
    output_name: str = "output.png"
    preview: bool = False
    
    # --- Epic B - Issue 1: Text Styling Config ---
    # Change: Added 'font', 'text_color', and 'stroke_color' fields to the Config dataclass.
    # Reason: Previously, font and color settings were entirely hardcoded.
    # This change allows users to specify custom fonts and colors via the CLI.
    font: Optional[str] = None
    text_color: str = "white"
    stroke_color: Optional[str] = None

    # Letter spacing (tracking) in percent of the font size. Negative values
    # tighten the text (THWS posts use tight tracking), positive values widen it.
    letter_spacing: float = -8.0
    
