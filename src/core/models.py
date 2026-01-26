from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
from PIL import Image

@dataclass
class SpriteDefinition:
    gx: int
    gy: int
    gw: int
    gh: int
    index: int

@dataclass
class CompilationOptions:
    grid_w: int
    grid_h: int
    offset_x: int
    offset_y: int
    mode: str  # "layered", "2bpp", "4bpp"
    output_path: str
