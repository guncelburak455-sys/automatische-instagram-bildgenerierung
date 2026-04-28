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
