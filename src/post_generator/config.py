from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """Configuration for the post generator."""
    photo: str
    position: str
    text: str
    x: int          # pixel offsets from the auto-calculated text center
    y: int
    output_path: Optional[str] = None
    output_name: str = "output.png"
