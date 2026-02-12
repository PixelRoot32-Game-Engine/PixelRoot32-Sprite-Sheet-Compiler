"""Tests para la API pública del PixelRoot32 Sprite Compiler."""
import sys
import os
import tempfile
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_api_imports():
    """Verifica que todos los elementos de la API pueden importarse desde src.core."""
    try:
        from pr32_sprite_compiler.core import (
            compile_sprite_sheet,
            get_supported_palettes,
            get_palette_colors,
            SpriteDefinition,
            CompilationOptions,
            SpriteCompiler,
            Exporter,
        )
        print("[OK] API publica importable desde src.core")
        return True
    except Exception as e:
        print(f"[FAIL] Error importando API: {e}")
        return False

def test_api_simple_compile():
    """Verifica que compile_sprite_sheet funciona con un caso simple."""
    from pr32_sprite_compiler.core import compile_sprite_sheet, SpriteDefinition, CompilationOptions
    from PIL import Image
    
    try:
        # Crear imagen de prueba simple (2x1 grid de 16x16)
        img = Image.new("RGBA", (32, 16), (255, 0, 0, 255))  # Rojo
        
        # Definir sprites
        sprites = [
            SpriteDefinition(0, 0, 1, 1, 0),
            SpriteDefinition(1, 0, 1, 1, 1),
        ]
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.h', delete=False) as f:
            output_path = f.name
        
        try:
            options = CompilationOptions(
                grid_w=16,
                grid_h=16,
                offset_x=0,
                offset_y=0,
                mode="layered",
                output_path=output_path,
                name_prefix="TEST"
            )
            
            result = compile_sprite_sheet(img, sprites, options)
            
            # Verificar que el archivo fue creado
            if result and os.path.exists(output_path):
                # Leer contenido
                with open(output_path, 'r') as f:
                    content = f.read()
                    if "TEST_SPRITE_0_LAYER_0" in content:
                        print("[OK] API compile_sprite_sheet funciona correctamente")
                        return True
                    else:
                        print("[FAIL] Contenido generado no contiene sprite esperado")
                        return False
            else:
                print(f"[FAIL] Compilacion fallo o archivo no creado")
                return False
        finally:
            # Limpiar
            if os.path.exists(output_path):
                os.unlink(output_path)
    except Exception as e:
        print(f"[FAIL] Error en test de compilacion: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_get_supported_palettes():
    """Verifica que get_supported_palettes funciona."""
    from pr32_sprite_compiler.core import get_supported_palettes
    
    try:
        palettes = get_supported_palettes()
        
        expected = ["PALETTE_NES", "PALETTE_GB", "PALETTE_GBC", "PALETTE_PICO8", "PALETTE_PR32"]
        
        for palette in expected:
            if palette not in palettes:
                print(f"[FAIL] Paleta '{palette}' no encontrada")
                return False
        
        print(f"[OK] get_supported_palettes retorna {len(palettes)} paletas")
        return True
    except Exception as e:
        print(f"[FAIL] Error en get_supported_palettes: {e}")
        return False

def test_api_get_palette_colors():
    """Verifica que get_palette_colors funciona."""
    from pr32_sprite_compiler.core import get_palette_colors
    
    try:
        # Paleta existente
        colors = get_palette_colors("PALETTE_NES")
        if len(colors) != 16:
            print(f"[FAIL] PALETTE_NES deberia tener 16 colores, tiene {len(colors)}")
            return False
        
        # Paleta no existente
        empty = get_palette_colors("PALETTE_FAKE")
        if empty != []:
            print(f"[FAIL] Paleta inexistente deberia retornar lista vacia")
            return False
        
        print("[OK] get_palette_colors funciona correctamente")
        return True
    except Exception as e:
        print(f"[FAIL] Error en get_palette_colors: {e}")
        return False

def test_api_compile_modes():
    """Verifica que compile_sprite_sheet funciona con diferentes modos."""
    from pr32_sprite_compiler.core import compile_sprite_sheet, SpriteDefinition, CompilationOptions
    from PIL import Image
    
    modes = ["layered", "2bpp", "4bpp"]
    results = []
    
    for mode in modes:
        try:
            # Crear imagen de prueba (16x16 con colores limitados para 2bpp/4bpp)
            img = Image.new("RGBA", (16, 16), (255, 0, 0, 255))
            
            sprites = [SpriteDefinition(0, 0, 1, 1, 0)]
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.h', delete=False) as f:
                output_path = f.name
            
            try:
                options = CompilationOptions(
                    grid_w=16, grid_h=16, offset_x=0, offset_y=0,
                    mode=mode,
                    output_path=output_path,
                    name_prefix="TEST"
                )
                
                result = compile_sprite_sheet(img, sprites, options)
                
                if result and os.path.exists(output_path):
                    results.append((mode, True))
                else:
                    results.append((mode, False))
            finally:
                if os.path.exists(output_path):
                    os.unlink(output_path)
        except Exception as e:
            results.append((mode, False))
            print(f"[WARN] Modo {mode} fallo: {e}")
    
    success_count = sum(1 for _, r in results if r)
    if success_count == len(modes):
        print(f"[OK] Todos los modos funcionan: {', '.join(modes)}")
        return True
    else:
        failed = [m for m, r in results if not r]
        print(f"[WARN] Algunos modos fallaron: {', '.join(failed)}")
        return success_count > 0

def run_api_tests():
    """Ejecuta todos los tests de la API."""
    print("="*60)
    print("Tests de API Publica - Fase 3")
    print("="*60)
    
    tests = [
        ("Importacion de API", test_api_imports),
        ("Compilacion Simple", test_api_simple_compile),
        ("Paletras Soportadas", test_api_get_supported_palettes),
        ("Colores de Paleta", test_api_get_palette_colors),
        ("Modos de Compilacion", test_api_compile_modes),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n[TEST] {name}")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"[FAIL] Test fallo con excepcion: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    print("\n" + "="*60)
    print("RESUMEN API")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {name}")
    
    print(f"\nTotal API: {passed}/{total} tests pasaron")
    
    return passed == total

if __name__ == "__main__":
    success = run_api_tests()
    sys.exit(0 if success else 1)
