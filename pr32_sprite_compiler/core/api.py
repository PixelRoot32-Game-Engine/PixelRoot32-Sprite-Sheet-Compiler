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
from typing import List
from PIL import Image

from .models import SpriteDefinition, CompilationOptions
from .compiler import SpriteCompiler
from .exporter import Exporter

__all__ = [
    'compile_sprite_sheet',
    'SpriteDefinition',
    'CompilationOptions',
    'SpriteCompiler',
    'Exporter',
]


def compile_sprite_sheet(
    image: Image.Image,
    sprites: List[SpriteDefinition],
    options: CompilationOptions
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
    
    Returns:
        True si la compilación fue exitosa, False en caso contrario.
    
    Raises:
        No lanza excepciones. Todos los errores se manejan internamente
        y retornan False.
    
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
        return Exporter.export(image, sprites, options)
    except Exception:
        # La API pública no propaga excepciones
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
