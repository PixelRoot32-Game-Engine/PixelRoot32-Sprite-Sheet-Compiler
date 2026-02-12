"""PixelRoot32 Sprite Compiler - Core package.

Este paquete contiene la lógica principal de compilación de sprites
para el motor PixelRoot32. Proporciona una API pública estable que
puede ser usada tanto por la GUI como por otros proyectos (e.g., Suite).

API Pública:
    >>> from pr32_sprite_compiler.core import compile_sprite_sheet, SpriteDefinition, CompilationOptions
    >>> from PIL import Image
    >>> 
    >>> # Cargar imagen
    >>> img = Image.open("player.png")
    >>> 
    >>> # Definir sprites
    >>> sprites = [SpriteDefinition(0, 0, 1, 1, 0)]
    >>> 
    >>> # Configurar opciones
    >>> options = CompilationOptions(
    ...     grid_w=16, grid_h=16,
    ...     offset_x=0, offset_y=0,
    ...     mode="4bpp",
    ...     output_path="sprites.h"
    ... )
    >>> 
    >>> # Compilar
    >>> compile_sprite_sheet(img, sprites, options)
    True

Módulos Internos (uso avanzado):
    - models: Definiciones de datos (SpriteDefinition, CompilationOptions)
    - compiler: Lógica de compilación (SpriteCompiler)
    - exporter: Generación de código C (Exporter)
    - api: API pública (compile_sprite_sheet, helpers)

Nota:
    Para uso normal, solo necesitas importar desde este módulo (src.core).
    Los submódulos internos están disponibles para casos de uso avanzados.
"""

# API Pública - Estas son las únicas importaciones necesarias para el uso normal
from .api import (
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
    # API Principal
    'compile_sprite_sheet',
    'get_supported_palettes',
    'get_palette_colors',
    
    # Modelos
    'SpriteDefinition',
    'CompilationOptions',
    
    # Clases internas (para uso avanzado)
    'SpriteCompiler',
    'Exporter',
]
