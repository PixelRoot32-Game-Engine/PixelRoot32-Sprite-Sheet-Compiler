"""Public API for the PixelRoot32 Sprite Compiler.

This is the only interface that should be used from the Suite or other projects.
It provides a stable and clean API without GUI dependencies.

Example:
    >>> from pr32_sprite_compiler.core import compile_sprite_sheet, SpriteDefinition, CompilationOptions
    >>> from PIL import Image
    >>> 
    >>> img = Image.open("player.png")
    >>> sprites = [SpriteDefinition(0, 0, 1, 1, 0)]
    >>> options = CompilationOptions(
    ...     grid_w=16, grid_h=16,
    ...     offset_x=0, offset_y=0,
    ...     mode="4bpp",
    ...     output_path="sprites.h"
    ... )
    >>> compile_sprite_sheet(img, sprites, options)
    True
"""
from typing import List, Optional
from pathlib import Path
from PIL import Image

from .models import SpriteDefinition, CompilationOptions
from .compiler import SpriteCompiler
from .exporter import Exporter
from .exceptions import (
    CompilationError,
    ValidationError,
    ImageError,
)
from . import logging as log

__all__ = [
    'compile_sprite_sheet',
    'SpriteDefinition',
    'CompilationOptions',
    'SpriteCompiler',
    'Exporter',
    'CompilationError',
    'ValidationError',
    'ImageError',
]


def _validate_image(image: Image.Image) -> None:
    """Validates that the image is valid for compilation.
    
    Args:
        image: PIL image to validate
        
    Raises:
        ImageError: If the image is not valid
    """
    if image is None:
        raise ImageError("Image cannot be None")
    
    if not isinstance(image, Image.Image):
        raise ImageError(
            f"Expected PIL.Image.Image, received {type(image).__name__}"
        )
    
    # Check mode
    if image.mode != "RGBA":
        raise ImageError(
            f"Image must be in RGBA mode, currently it is {image.mode}",
            context={"current_mode": image.mode, "required_mode": "RGBA"}
        )
    
    # Check dimensions
    if image.width <= 0 or image.height <= 0:
        raise ImageError(
            f"Invalid image dimensions: {image.width}x{image.height}",
            context={"width": image.width, "height": image.height}
        )
    
    log.debug(f"Validated image: {image.width}x{image.height} RGBA")


def _validate_sprites(sprites: List[SpriteDefinition]) -> None:
    """Validates the sprite list.
    
    Args:
        sprites: List of sprites to validate
        
    Raises:
        ValidationError: If the sprites are not valid
    """
    if not sprites:
        raise ValidationError(
            "At least one sprite is required",
            field="sprites"
        )
    
    if not isinstance(sprites, list):
        raise ValidationError(
            f"sprites must be a list, not {type(sprites).__name__}",
            field="sprites",
            value=sprites
        )
    
    for i, sprite in enumerate(sprites):
        if not isinstance(sprite, SpriteDefinition):
            raise ValidationError(
                f"Sprite {i} is not a valid SpriteDefinition",
                field=f"sprites[{i}]",
                value=sprite
            )
        
        # Validate sprite dimensions
        if sprite.gw <= 0 or sprite.gh <= 0:
            raise ValidationError(
                f"Invalid sprite dimensions in sprite {i}",
                field=f"sprites[{i}].grid_size",
                value=(sprite.gw, sprite.gh)
            )
    
    log.debug(f"Validated sprites: {len(sprites)} sprites")


def _validate_options(options: CompilationOptions) -> None:
    """Validates compilation options.
    
    Args:
        options: Options to validate
        
    Raises:
        ValidationError: If options are not valid
    """
    if options is None:
        raise ValidationError(
            "options cannot be None",
            field="options"
        )
    
    if not isinstance(options, CompilationOptions):
        raise ValidationError(
            f"options must be CompilationOptions, not {type(options).__name__}",
            field="options",
            value=options
        )
    
    # Validate grid
    if options.grid_w <= 0:
        raise ValidationError(
            f"grid_w must be positive, received {options.grid_w}",
            field="grid_w",
            value=options.grid_w
        )
    
    if options.grid_h <= 0:
        raise ValidationError(
            f"grid_h must be positive, received {options.grid_h}",
            field="grid_h",
            value=options.grid_h
        )
    
    # Validate mode
    valid_modes = ["layered", "2bpp", "4bpp"]
    if options.mode not in valid_modes:
        raise ValidationError(
            f"Mode '{options.mode}' not supported. Use: {', '.join(valid_modes)}",
            field="mode",
            value=options.mode
        )
    
    # Validate output_path
    if not options.output_path:
        raise ValidationError(
            "output_path cannot be empty",
            field="output_path"
        )
    
    log.debug(f"Validated options: mode={options.mode}, grid={options.grid_w}x{options.grid_h}")


def compile_sprite_sheet(
    image: Image.Image,
    sprites: List[SpriteDefinition],
    options: CompilationOptions,
    raise_on_error: bool = False
) -> bool:
    """Compiles a sprite sheet to C code.
    
    This is the main function of the public API. It takes a PIL image
    loaded in RGBA mode, a list of sprite definitions and compilation
    options, and generates a C header file (.h) with the compiled sprites.
    
    Args:
        image: PIL image loaded in RGBA mode. Must contain all sprites
               organized according to the specified grid.
        sprites: List of SpriteDefinition indicating which sprites to extract
                 and their position on the grid.
        options: Compilation options including grid size, export mode
                (layered, 2bpp, 4bpp), output path, etc.
        raise_on_error: If True, raises exceptions instead of returning False
    
    Returns:
        True if compilation was successful, False otherwise.
    
    Raises:
        ValidationError: If parameters are not valid (only if raise_on_error=True)
        ImageError: If there are problems with the image (only if raise_on_error=True)
        CompilationError: If compilation fails (only if raise_on_error=True)
    
    Example:
        >>> from pr32_sprite_compiler.core import compile_sprite_sheet, SpriteDefinition, CompilationOptions
        >>> from PIL import Image
        >>> 
        >>> # Load image
        >>> img = Image.open("assets/player.png").convert("RGBA")
        >>> 
        >>> # Define sprites (4 animation frames)
        >>> sprites = [
        ...     SpriteDefinition(0, 0, 1, 1, 0),  # frame 0
        ...     SpriteDefinition(1, 0, 1, 1, 1),  # frame 1
        ...     SpriteDefinition(2, 0, 1, 1, 2),  # frame 2
        ...     SpriteDefinition(3, 0, 1, 1, 3),  # frame 3
        ... ]
        >>> 
        >>> # Configure options
        >>> options = CompilationOptions(
        ...     grid_w=16,
        ...     grid_h=16,
        ...     offset_x=0,
        ...     offset_y=0,
        ...     mode="4bpp",
        ...     output_path="src/player_sprites.h",
        ...     name_prefix="PLAYER"
        ... )
        >>> 
        >>> # Compile
        >>> success = compile_sprite_sheet(img, sprites, options)
        >>> if success:
        ...     print(f"Generated: {options.output_path}")
        ... else:
        ...     print("Compilation error")
    """
    try:
        # Validate inputs
        log.log_compilation_start(options)
        _validate_image(image)
        _validate_sprites(sprites)
        _validate_options(options)
        
        # Execute compilation
        result = Exporter.export(image, sprites, options)
        
        if result:
            log.log_compilation_success(len(sprites), options.output_path)
        else:
            log.log_compilation_error("Export failed")
        
        return result
        
    except (ValidationError, ImageError, CompilationError) as e:
        log.log_compilation_error(str(e))
        if raise_on_error:
            raise
        return False
    except Exception as e:
        log.log_compilation_error(f"Unexpected error: {str(e)}")
        if raise_on_error:
            raise CompilationError(f"Unexpected error: {str(e)}")
        return False


def get_supported_palettes() -> List[str]:
    """Returns the list of supported predefined palettes.
    
    Returns:
        List of available palette names (e.g., ['PALETTE_NES', ...])
    
    Example:
        >>> from pr32_sprite_compiler.core import get_supported_palettes
        >>> palettes = get_supported_palettes()
        >>> print(f"Supported palettes: {', '.join(palettes)}")
    """
    return list(Exporter.PREDEFINED_PALETTES.keys())


def get_palette_colors(palette_name: str) -> List[tuple]:
    """Returns the colors of a predefined palette.
    
    Args:
        palette_name: Palette name (e.g., 'PALETTE_NES')
    
    Returns:
        List of RGB tuples or empty list if the palette does not exist.
    
    Example:
        >>> from pr32_sprite_compiler.core import get_palette_colors
        >>> colors = get_palette_colors("PALETTE_NES")
        >>> print(f"NES palette has {len(colors)} colors")
    """
    return Exporter.PREDEFINED_PALETTES.get(palette_name, [])
