"""API pública del PixelRoot32 Sprite Compiler.

Esta es la única interfaz que debería usarse desde el Suite u otros proyectos.
Proporciona una API estable y limpia sin dependencias de GUI.

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
    """Valida que la imagen sea válida para compilación.
    
    Args:
        image: Imagen PIL a validar
        
    Raises:
        ImageError: Si la imagen no es válida
    """
    if image is None:
        raise ImageError("La imagen no puede ser None")
    
    if not isinstance(image, Image.Image):
        raise ImageError(
            f"Se esperaba PIL.Image.Image, se recibió {type(image).__name__}"
        )
    
    # Verificar modo
    if image.mode != "RGBA":
        raise ImageError(
            f"La imagen debe estar en modo RGBA, actualmente es {image.mode}",
            context={"current_mode": image.mode, "required_mode": "RGBA"}
        )
    
    # Verificar dimensiones
    if image.width <= 0 or image.height <= 0:
        raise ImageError(
            f"Dimensiones de imagen inválidas: {image.width}x{image.height}",
            context={"width": image.width, "height": image.height}
        )
    
    log.debug(f"Imagen validada: {image.width}x{image.height} RGBA")


def _validate_sprites(sprites: List[SpriteDefinition]) -> None:
    """Valida la lista de sprites.
    
    Args:
        sprites: Lista de sprites a validar
        
    Raises:
        ValidationError: Si los sprites no son válidos
    """
    if not sprites:
        raise ValidationError(
            "Se requiere al menos un sprite",
            field="sprites"
        )
    
    if not isinstance(sprites, list):
        raise ValidationError(
            f"sprites debe ser una lista, no {type(sprites).__name__}",
            field="sprites",
            value=sprites
        )
    
    for i, sprite in enumerate(sprites):
        if not isinstance(sprite, SpriteDefinition):
            raise ValidationError(
                f"El sprite {i} no es un SpriteDefinition válido",
                field=f"sprites[{i}]",
                value=sprite
            )
        
        # Validar dimensiones del sprite
        if sprite.gw <= 0 or sprite.gh <= 0:
            raise ValidationError(
                f"Dimensiones de sprite inválidas en sprite {i}",
                field=f"sprites[{i}].grid_size",
                value=(sprite.gw, sprite.gh)
            )
    
    log.debug(f"Sprites validados: {len(sprites)} sprites")


def _validate_options(options: CompilationOptions) -> None:
    """Valida las opciones de compilación.
    
    Args:
        options: Opciones a validar
        
    Raises:
        ValidationError: Si las opciones no son válidas
    """
    if options is None:
        raise ValidationError(
            "options no puede ser None",
            field="options"
        )
    
    if not isinstance(options, CompilationOptions):
        raise ValidationError(
            f"options debe ser CompilationOptions, no {type(options).__name__}",
            field="options",
            value=options
        )
    
    # Validar grid
    if options.grid_w <= 0:
        raise ValidationError(
            f"grid_w debe ser positivo, se recibió {options.grid_w}",
            field="grid_w",
            value=options.grid_w
        )
    
    if options.grid_h <= 0:
        raise ValidationError(
            f"grid_h debe ser positivo, se recibió {options.grid_h}",
            field="grid_h",
            value=options.grid_h
        )
    
    # Validar modo
    valid_modes = ["layered", "2bpp", "4bpp"]
    if options.mode not in valid_modes:
        raise ValidationError(
            f"Modo '{options.mode}' no soportado. Use: {', '.join(valid_modes)}",
            field="mode",
            value=options.mode
        )
    
    # Validar output_path
    if not options.output_path:
        raise ValidationError(
            "output_path no puede estar vacío",
            field="output_path"
        )
    
    log.debug(f"Opciones validadas: modo={options.mode}, grid={options.grid_w}x{options.grid_h}")


def compile_sprite_sheet(
    image: Image.Image,
    sprites: List[SpriteDefinition],
    options: CompilationOptions,
    raise_on_error: bool = False
) -> bool:
    """Compila un sprite sheet a código C.
    
    Esta es la función principal de la API pública. Toma una imagen PIL
    cargada en modo RGBA, una lista de definiciones de sprites y opciones
    de compilación, y genera un archivo header de C (.h) con los sprites
    compilados.
    
    Args:
        image: Imagen PIL cargada en modo RGBA. Debe contener todos los
               sprites organizados según la grid especificada.
        sprites: Lista de SpriteDefinition que indica qué sprites extraer
                 y en qué posición de la grid se encuentran.
        options: Opciones de compilación incluyendo grid size, modo de
                exportación (layered, 2bpp, 4bpp), path de salida, etc.
        raise_on_error: Si True, lanza excepciones en lugar de retornar False
    
    Returns:
        True si la compilación fue exitosa, False en caso contrario.
    
    Raises:
        ValidationError: Si los parámetros no son válidos (solo si raise_on_error=True)
        ImageError: Si hay problemas con la imagen (solo si raise_on_error=True)
        CompilationError: Si falla la compilación (solo si raise_on_error=True)
    
    Example:
        >>> from pr32_sprite_compiler.core import compile_sprite_sheet, SpriteDefinition, CompilationOptions
        >>> from PIL import Image
        >>> 
        >>> # Cargar imagen
        >>> img = Image.open("assets/player.png").convert("RGBA")
        >>> 
        >>> # Definir sprites (4 frames de animación)
        >>> sprites = [
        ...     SpriteDefinition(0, 0, 1, 1, 0),  # frame 0
        ...     SpriteDefinition(1, 0, 1, 1, 1),  # frame 1
        ...     SpriteDefinition(2, 0, 1, 1, 2),  # frame 2
        ...     SpriteDefinition(3, 0, 1, 1, 3),  # frame 3
        ... ]
        >>> 
        >>> # Configurar opciones
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
        >>> # Compilar
        >>> success = compile_sprite_sheet(img, sprites, options)
        >>> if success:
        ...     print(f"Generado: {options.output_path}")
        ... else:
        ...     print("Error en la compilación")
    """
    try:
        # Validar entradas
        log.log_compilation_start(options)
        _validate_image(image)
        _validate_sprites(sprites)
        _validate_options(options)
        
        # Ejecutar compilación
        result = Exporter.export(image, sprites, options)
        
        if result:
            log.log_compilation_success(len(sprites), options.output_path)
        else:
            log.log_compilation_error("Exportación falló")
        
        return result
        
    except (ValidationError, ImageError, CompilationError) as e:
        log.log_compilation_error(str(e))
        if raise_on_error:
            raise
        return False
    except Exception as e:
        log.log_compilation_error(f"Error inesperado: {str(e)}")
        if raise_on_error:
            raise CompilationError(f"Error inesperado: {str(e)}")
        return False


def get_supported_palettes() -> List[str]:
    """Retorna la lista de paletas predefinidas soportadas.
    
    Returns:
        Lista de nombres de paletas disponibles (e.g., ['PALETTE_NES', ...])
    
    Example:
        >>> from pr32_sprite_compiler.core import get_supported_palettes
        >>> palettes = get_supported_palettes()
        >>> print(f"Palettes soportadas: {', '.join(palettes)}")
    """
    return list(Exporter.PREDEFINED_PALETTES.keys())


def get_palette_colors(palette_name: str) -> List[tuple]:
    """Retorna los colores de una paleta predefinida.
    
    Args:
        palette_name: Nombre de la paleta (e.g., 'PALETTE_NES')
    
    Returns:
        Lista de tuplas RGB o lista vacía si la paleta no existe.
    
    Example:
        >>> from pr32_sprite_compiler.core import get_palette_colors
        >>> colors = get_palette_colors("PALETTE_NES")
        >>> print(f"La paleta NES tiene {len(colors)} colores")
    """
    return Exporter.PREDEFINED_PALETTES.get(palette_name, [])
