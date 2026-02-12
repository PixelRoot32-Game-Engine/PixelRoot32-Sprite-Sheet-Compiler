"""PixelRoot32 Sprite Compiler.

A sprite sheet compiler for the PixelRoot32 engine.

Example:
    >>> from pr32_sprite_compiler import compile_sprite_sheet, SpriteDefinition, CompilationOptions
    >>> from PIL import Image
    >>> 
    >>> img = Image.open("player.png")
    >>> sprites = [SpriteDefinition(0, 0, 1, 1, 0)]
    >>> options = CompilationOptions(
    ...     grid_w=16, grid_h=16,
    ...     mode="4bpp",
    ...     output_path="sprites.h"
    ... )
    >>> compile_sprite_sheet(img, sprites, options)
    True

For GUI mode, run:
    $ pr32-sprite-compiler

For CLI mode:
    $ pr32-sprite-compiler input.png --grid 16x16 --sprite 0,0,1,1 --out sprites.h
"""

from pr32_sprite_compiler.core.api import (
    compile_sprite_sheet,
    get_supported_palettes,
    get_palette_colors,
    SpriteDefinition,
    CompilationOptions,
    SpriteCompiler,
    Exporter,
)

__version__ = "0.3.0"

__all__ = [
    "compile_sprite_sheet",
    "get_supported_palettes",
    "get_palette_colors",
    "SpriteDefinition",
    "CompilationOptions",
    "SpriteCompiler",
    "Exporter",
]
