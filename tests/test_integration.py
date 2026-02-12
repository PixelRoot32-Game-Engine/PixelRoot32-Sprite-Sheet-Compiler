"""Tests de integración básicos para el core del PixelRoot32 Sprite Compiler."""
import sys
import os
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_core_imports():
    """Verifica que el paquete core puede ser importado sin errores."""
    try:
        from pr32_sprite_compiler.core import models
        from pr32_sprite_compiler.core import compiler
        print("[OK] Core imports exitoso")
        return True
    except Exception as e:
        print(f"[FAIL] Error importando core: {e}")
        return False

def test_core_exporter_import():
    """Verifica que el exporter puede importarse desde core."""
    try:
        from pr32_sprite_compiler.core.exporter import Exporter
        print("[OK] Exporter import desde core exitoso")
        return True
    except Exception as e:
        print(f"[FAIL] Error importando exporter desde core: {e}")
        return False

def test_services_backwards_compatibility():
    """Verifica que services sigue funcionando (compatibilidad hacia atras)."""
    import warnings
    try:
        # Capturar warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            from pr32_sprite_compiler.services import Exporter
            
            # Verificar que se emitio warning de deprecacion
            deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
            if deprecation_warnings:
                print("[OK] Backwards compatibility funciona (con warning de deprecacion)")
                return True
            else:
                print("[WARN] Backwards compatibility funciona pero sin warning")
                return True
    except Exception as e:
        print(f"[FAIL] Error en backwards compatibility: {e}")
        return False

def test_core_no_gui_dependency():
    """Verifica que core no depende de gui ni tkinter."""
    import importlib
    
    # Limpiar módulos previamente importados
    modules_to_check = ['src.core', 'src.core.models', 'src.core.compiler']
    
    # Verificar que tkinter no está en los módulos importados por core
    import pr32_sprite_compiler.core.models
    import pr32_sprite_compiler.core.compiler
    
    imported_modules = list(sys.modules.keys())
    
    gui_related = [m for m in imported_modules if any(x in m for x in ['tkinter', 'ttkbootstrap', 'gui'])]
    
    if gui_related:
        print(f"[WARN] Módulos GUI detectados: {gui_related}")
        return False
    else:
        print("[OK] Core no tiene dependencias de GUI")
        return True

def test_models_dataclasses():
    """Verifica que los modelos funcionan correctamente."""
    from pr32_sprite_compiler.core.models import SpriteDefinition, CompilationOptions
    
    try:
        # Crear instancias de prueba
        sprite = SpriteDefinition(gx=0, gy=0, gw=1, gh=1, index=0)
        options = CompilationOptions(
            grid_w=16,
            grid_h=16,
            offset_x=0,
            offset_y=0,
            mode="layered",
            output_path="test.h",
            name_prefix="TEST"
        )
        
        print(f"[OK] Models funcionan: Sprite({sprite.gx},{sprite.gy}), Options(mode={options.mode})")
        return True
    except Exception as e:
        print(f"[FAIL] Error creando modelos: {e}")
        return False

def test_compiler_static_methods():
    """Verifica que los métodos estáticos del compiler existen."""
    from pr32_sprite_compiler.core.compiler import SpriteCompiler
    
    methods = ['extract_colors', 'sprite_to_bits', 'pack_2bpp', 'pack_4bpp']
    
    for method in methods:
        if hasattr(SpriteCompiler, method):
            print(f"[OK] Metodo '{method}' disponible")
        else:
            print(f"[FAIL] Metodo '{method}' no encontrado")
            return False
    
    return True

def test_exporter_predefined_palettes():
    """Verifica que las paletas predefinidas existen."""
    from pr32_sprite_compiler.core.exporter import Exporter
    
    expected_palettes = [
        "PALETTE_NES",
        "PALETTE_GB", 
        "PALETTE_GBC",
        "PALETTE_PICO8",
        "PALETTE_PR32"
    ]
    
    for palette_name in expected_palettes:
        if palette_name in Exporter.PREDEFINED_PALETTES:
            palette = Exporter.PREDEFINED_PALETTES[palette_name]
            print(f"[OK] Paleta '{palette_name}' disponible ({len(palette)} colores)")
        else:
            print(f"[FAIL] Paleta '{palette_name}' no encontrada")
            return False
    
    return True

def run_all_tests():
    """Ejecuta todos los tests básicos."""
    print("="*60)
    print("Tests de Integracion - Fase 2")
    print("="*60)
    
    tests = [
        ("Importacion de Core", test_core_imports),
        ("Importacion de Exporter desde Core", test_core_exporter_import),
        ("Backwards Compatibility (services)", test_services_backwards_compatibility),
        ("Sin dependencias GUI", test_core_no_gui_dependency),
        ("Models Dataclasses", test_models_dataclasses),
        ("Metodos del Compiler", test_compiler_static_methods),
        ("Paletras Predefinidas", test_exporter_predefined_palettes),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n[TEST] {name}")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"[FAIL] Test fallo con excepcion: {e}")
            results.append((name, False))
    
    print("\n" + "="*60)
    print("RESUMEN")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests pasaron")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
