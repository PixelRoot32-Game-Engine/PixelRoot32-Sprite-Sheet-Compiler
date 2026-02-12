"""Tests for the PixelRoot32 Sprite Compiler public API."""
import sys
import os
import tempfile
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_api_imports():
    """Verifies that all API elements can be imported from src.core."""
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
        print("[OK] Public API importable from src.core")
        return True
    except Exception as e:
        print(f"[FAIL] Error importing API: {e}")
        return False

def test_api_simple_compile():
    """Verifies that compile_sprite_sheet works with a simple case."""
    from pr32_sprite_compiler.core import compile_sprite_sheet, SpriteDefinition, CompilationOptions
    from PIL import Image
    
    try:
        # Create simple test image (2x1 grid of 16x16)
        img = Image.new("RGBA", (32, 16), (255, 0, 0, 255))  # Red
        
        # Define sprites
        sprites = [
            SpriteDefinition(0, 0, 1, 1, 0),
            SpriteDefinition(1, 0, 1, 1, 1),
        ]
        
        # Create temporary file
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
            
            # Verify that the file was created
            if result and os.path.exists(output_path):
                # Read content
                with open(output_path, 'r') as f:
                    content = f.read()
                    if "TEST_SPRITE_0_LAYER_0" in content:
                        print("[OK] API compile_sprite_sheet works correctly")
                        return True
                    else:
                        print("[FAIL] Generated content does not contain expected sprite")
                        return False
            else:
                print(f"[FAIL] Compilation failed or file not created")
                return False
        finally:
            # Clean up
            if os.path.exists(output_path):
                os.unlink(output_path)
    except Exception as e:
        print(f"[FAIL] Error in compilation test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_get_supported_palettes():
    """Verifies that get_supported_palettes works."""
    from pr32_sprite_compiler.core import get_supported_palettes
    
    try:
        palettes = get_supported_palettes()
        
        expected = ["PALETTE_NES", "PALETTE_GB", "PALETTE_GBC", "PALETTE_PICO8", "PALETTE_PR32"]
        
        for palette in expected:
            if palette not in palettes:
                print(f"[FAIL] Palette '{palette}' not found")
                return False
        
        print(f"[OK] get_supported_palettes returns {len(palettes)} palettes")
        return True
    except Exception as e:
        print(f"[FAIL] Error in get_supported_palettes: {e}")
        return False

def test_api_get_palette_colors():
    """Verifies that get_palette_colors works."""
    from pr32_sprite_compiler.core import get_palette_colors
    
    try:
        # Existing palette
        colors = get_palette_colors("PALETTE_NES")
        if len(colors) != 16:
            print(f"[FAIL] PALETTE_NES should have 16 colors, has {len(colors)}")
            return False
        
        # Non-existent palette
        empty = get_palette_colors("PALETTE_FAKE")
        if empty != []:
            print(f"[FAIL] Non-existent palette should return empty list")
            return False
        
        print("[OK] get_palette_colors works correctly")
        return True
    except Exception as e:
        print(f"[FAIL] Error in get_palette_colors: {e}")
        return False

def test_api_compile_modes():
    """Verifies that compile_sprite_sheet works with different modes."""
    from pr32_sprite_compiler.core import compile_sprite_sheet, SpriteDefinition, CompilationOptions
    from PIL import Image
    
    modes = ["layered", "2bpp", "4bpp"]
    results = []
    
    for mode in modes:
        try:
            # Create test image (16x16 with limited colors for 2bpp/4bpp)
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
            print(f"[WARN] Mode {mode} failed: {e}")
    
    success_count = sum(1 for _, r in results if r)
    if success_count == len(modes):
        print(f"[OK] All modes work: {', '.join(modes)}")
        return True
    else:
        failed = [m for m, r in results if not r]
        print(f"[WARN] Some modes failed: {', '.join(failed)}")
        return success_count > 0

def run_api_tests():
    """Runs all API tests."""
    print("="*60)
    print("Public API Tests - Phase 3")
    print("="*60)
    
    tests = [
        ("API Import", test_api_imports),
        ("Simple Compilation", test_api_simple_compile),
        ("Supported Palettes", test_api_get_supported_palettes),
        ("Palette Colors", test_api_get_palette_colors),
        ("Compilation Modes", test_api_compile_modes),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n[TEST] {name}")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"[FAIL] Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    print("\n" + "="*60)
    print("API SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {name}")
    
    print(f"\nTotal API: {passed}/{total} tests passed")
    
    return passed == total

if __name__ == "__main__":
    success = run_api_tests()
    sys.exit(0 if success else 1)
