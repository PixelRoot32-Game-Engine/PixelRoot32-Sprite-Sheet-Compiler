"""PixelRoot32 Sprite Compiler - Services package.

DEPRECATED: Este módulo se mantiene solo para compatibilidad hacia atrás.
La funcionalidad ha sido movida a src.core.exporter.

En lugar de usar:
    from pr32_sprite_compiler.services.exporter import Exporter

Usa:
    from pr32_sprite_compiler.core.exporter import Exporter
"""
import warnings

# Re-export desde core para mantener compatibilidad
from pr32_sprite_compiler.core.exporter import Exporter

__all__ = ['Exporter']

# Emitir warning de deprecación
warnings.warn(
    "src.services.exporter está deprecado. "
    "Usa src.core.exporter en su lugar.",
    DeprecationWarning,
    stacklevel=2
)
