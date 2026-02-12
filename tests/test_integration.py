"""Basic integration tests for the PixelRoot32 Sprite Compiler core."""
import sys
import os
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_core_imports():
    """Verifies that the core package can be imported without errors."""
    try:
        from pr32_sprite_compiler.core import models
        from pr32_sprite_compiler.core import compiler
        print("[OK] Core imports successful")
        return True
    except Exception as e:
        print(f"[FAIL] Error importing core: {e}")
        return False

def test_core_exporter_import():
    """Verifies that the exporter can be imported from core."""
    try:
        from pr32_sprite_compiler.core.exporter import Exporter
        print("[OK] Exporter import from core successful")
        return True
    except Exception as e:
        print(f"[FAIL] Error importing exporter from core: {e}")
        return False

def test_services_backwards_compatibility():
    """Verifies that services still works (backwards compatibility)."""
    import warnings
    try:
        # Capture warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            from pr32_sprite_compiler.services import Exporter
            
            # Verify that deprecation warning was emitted
            deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
            if deprecation_warnings:
                print("[OK] Backwards compatibility works (with deprecation warning)")
                return True
            else:
                print("[WARN] Backwards compatibility works but without warning")
                return True
    except Exception as e:
        print(f"[FAIL] Error in backwards compatibility: {e}")
        return False

def test_core_no_gui_dependency():
    """Verifies that core does not depend on gui or tkinter."""
    import importlib
    
    # Clean up previously imported modules
    modules_to_check = ['src.core', 'src.core.models', 'src.core.compiler']
    
    # Verify that tkinter is not in the modules imported by core
    import pr32_sprite_compiler.core.models
    import pr32_sprite_compiler.core.compiler
    
    imported_modules = list(sys.modules.keys())
    
    gui_related = [m for m in imported_modules if any(x in m for x in ['tkinter', 'ttkbootstrap', 'gui'])]
    
    if gui_related:
        print(f"[WARN] GUI modules detected: {gui_related}")
        return False
    else:
        print("[OK] Core has no GUI dependencies")
        return True

def test_models_dataclasses():
    """Verifies that the models work correctly."""
    from pr32_sprite_compiler.core.models import SpriteDefinition, CompilationOptions
    
    try:
        # Create test instances
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
        
        print(f"[OK] Models work: Sprite({sprite.gx},{sprite.gy}), Options(mode={options.mode})")
        return True
    except Exception as e:
        print(f"[FAIL] Error creating models: {e}")
        return False

def test_compiler_static_methods():
    """Verifies that the compiler static methods exist."""
    from pr32_sprite_compiler.core.compiler import SpriteCompiler
    
    methods = ['extract_colors', 'sprite_to_bits', 'pack_2bpp', 'pack_4bpp']
    
    for method in methods:
        if hasattr(SpriteCompiler, method):
            print(f"[OK] Method '{method}' available")
        else:
            print(f"[FAIL] Method '{method}' not found")
            return False
    
    return True

def test_exporter_predefined_palettes():
    """Verifies that the predefined palettes exist."""
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
            print(f"[OK] Palette '{palette_name}' available ({len(palette)} colors)")
        else:
            print(f"[FAIL] Palette '{palette_name}' not found")
            return False
    
    return True

def run_all_tests():
    """Runs all basic tests."""
    print("="*60)
    print("Integration Tests - Phase 2")
    print("="*60)
    
    tests = [
        ("Core Import", test_core_imports),
        ("Exporter Import from Core", test_core_exporter_import),
        ("Backwards Compatibility (services)", test_services_backwards_compatibility),
        ("No GUI Dependencies", test_core_no_gui_dependency),
        ("Models Dataclasses", test_models_dataclasses),
        ("Compiler Methods", test_compiler_static_methods),
        ("Predefined Palettes", test_exporter_predefined_palettes),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n[TEST] {name}")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"[FAIL] Test failed with exception: {e}")
            results.append((name, False))
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
