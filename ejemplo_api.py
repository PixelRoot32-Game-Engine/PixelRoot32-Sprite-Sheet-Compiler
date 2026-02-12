"""Ejemplo de uso de la API pública del PixelRoot32 Sprite Compiler.

Este script demuestra como usar el compiler desde código Python sin GUI,
como lo haría el PixelRoot32 Suite.
"""
import sys
from pathlib import Path

# En el Suite, esto sería simplemente:
# from pr32_sprite_compiler import compile_sprite_sheet, SpriteDefinition, CompilationOptions
# Pero por ahora usamos el path local
sys.path.insert(0, str(Path(__file__).parent))

from pr32_sprite_compiler.core import (
    compile_sprite_sheet,
    get_supported_palettes,
    get_palette_colors,
    SpriteDefinition,
    CompilationOptions,
)
from PIL import Image


def ejemplo_basico():
    """Ejemplo básico: Compilar un sprite simple."""
    print("=" * 60)
    print("Ejemplo 1: Compilacion Basica")
    print("=" * 60)
    
    # Crear una imagen de prueba (32x16 con 2 sprites de 16x16)
    img = Image.new("RGBA", (32, 16), (0, 0, 0, 0))
    # Sprite 0: Cuadrado rojo
    img.paste((255, 0, 0, 255), (0, 0, 16, 16))
    # Sprite 1: Cuadrado azul
    img.paste((0, 0, 255, 255), (16, 0, 32, 16))
    
    # Definir los sprites a extraer
    sprites = [
        SpriteDefinition(gx=0, gy=0, gw=1, gh=1, index=0),  # Sprite rojo
        SpriteDefinition(gx=1, gy=0, gw=1, gh=1, index=1),  # Sprite azul
    ]
    
    # Configurar opciones de compilación
    options = CompilationOptions(
        grid_w=16,           # Ancho de cada celda del grid
        grid_h=16,           # Alto de cada celda del grid
        offset_x=0,          # Offset X inicial
        offset_y=0,          # Offset Y inicial
        mode="layered",      # Modo: layered, 2bpp, o 4bpp
        output_path="ejemplo_basico.h",
        name_prefix="PLAYER"
    )
    
    # Compilar
    print(f"Compilando {len(sprites)} sprites...")
    success = compile_sprite_sheet(img, sprites, options)
    
    if success:
        print(f"[OK] Exito! Archivo generado: {options.output_path}")
        # Mostrar contenido
        with open(options.output_path, 'r') as f:
            content = f.read()
            print(f"\nContenido generado ({len(content)} caracteres):")
            print("-" * 40)
            print(content[:500] + "..." if len(content) > 500 else content)
    else:
        print("[ERROR] Error en la compilacion")
    
    return success


def ejemplo_animacion():
    """Ejemplo: Compilar una animación de 4 frames."""
    print("\n" + "=" * 60)
    print("Ejemplo 2: Animacion con 4 Frames")
    print("=" * 60)
    
    # Crear imagen de animación (64x16 = 4 frames de 16x16)
    img = Image.new("RGBA", (64, 16), (0, 0, 0, 0))
    
    # 4 frames con diferentes colores
    colors = [
        (255, 0, 0, 255),    # Rojo
        (255, 128, 0, 255),  # Naranja
        (255, 255, 0, 255),  # Amarillo
        (128, 255, 0, 255),  # Verde-amarillo
    ]
    
    for i, color in enumerate(colors):
        x = i * 16
        img.paste(color, (x, 0, x + 16, 16))
    
    # Definir frames de animación
    sprites = [
        SpriteDefinition(gx=i, gy=0, gw=1, gh=1, index=i)
        for i in range(4)
    ]
    
    options = CompilationOptions(
        grid_w=16,
        grid_h=16,
        offset_x=0,
        offset_y=0,
        mode="4bpp",  # Usar modo 4bpp para optimizar espacio
        output_path="ejemplo_animacion.h",
        name_prefix="ANIM"
    )
    
    print(f"Compilando animación de {len(sprites)} frames...")
    success = compile_sprite_sheet(img, sprites, options)
    
    if success:
        print(f"[OK] Animacion compilada: {options.output_path}")
    else:
        print("[ERROR] Error compilando animacion")
    
    return success


def ejemplo_paletas():
    """Ejemplo: Trabajar con paletas predefinidas."""
    print("\n" + "=" * 60)
    print("Ejemplo 3: Informacion de Paletas")
    print("=" * 60)
    
    # Obtener lista de paletas soportadas
    palettes = get_supported_palettes()
    print(f"Paletas soportadas ({len(palettes)}):")
    for palette_name in palettes:
        colors = get_palette_colors(palette_name)
        print(f"  - {palette_name}: {len(colors)} colores")
    
    # Mostrar colores de una paleta específica
    print(f"\nColores de PALETTE_NES:")
    nes_colors = get_palette_colors("PALETTE_NES")
    for i, (r, g, b) in enumerate(nes_colors[:8]):  # Primeros 8 colores
        print(f"  Index {i}: RGB({r:3}, {g:3}, {b:3})")
    
    return True


def cleanup():
    """Limpia archivos generados."""
    import os
    files = ["ejemplo_basico.h", "ejemplo_animacion.h"]
    for f in files:
        if os.path.exists(f):
            os.remove(f)
            print(f"[DELETE] Eliminado: {f}")


def main():
    """Ejecuta todos los ejemplos."""
    print("\n")
    print("=" * 60)
    print("  PixelRoot32 Sprite Compiler - API Demo")
    print("=" * 60)
    print("\nEste demo muestra como usar la API pública desde código Python.\n")
    
    try:
        # Ejecutar ejemplos
        results = []
        results.append(("Básico", ejemplo_basico()))
        results.append(("Animación", ejemplo_animacion()))
        results.append(("Paletas", ejemplo_paletas()))
        
        # Resumen
        print("\n" + "=" * 60)
        print("RESUMEN")
        print("=" * 60)
        
        for name, success in results:
            status = "[OK]" if success else "[FAIL]"
            print(f"{status}: {name}")
        
        print("\n" + "=" * 60)
        print("Archivos generados:")
        print("  - ejemplo_basico.h")
        print("  - ejemplo_animacion.h")
        print("=" * 60)
        
        # Preguntar si limpiar
        print("\nLos archivos se mantienen para inspección.")
        print("Ejecuta 'python ejemplo_api.py --cleanup' para eliminarlos.")
        
        if "--cleanup" in sys.argv:
            cleanup()
        
    except KeyboardInterrupt:
        print("\n\nInterrumpido por el usuario.")
        cleanup()
    except Exception as e:
        print(f"\n\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        cleanup()


if __name__ == "__main__":
    main()
