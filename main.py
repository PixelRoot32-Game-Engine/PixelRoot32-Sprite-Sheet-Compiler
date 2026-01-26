import sys
import os
import argparse
from pathlib import Path
from PIL import Image

# Add src to path if needed
sys.path.append(str(Path(__file__).parent))

from src.gui.main_window import MainWindow
from src.services.exporter import Exporter
from src.core.models import SpriteDefinition, CompilationOptions

def run_cli(args):
    """Executes the compilation from command line arguments."""
    try:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"ERROR: Input file not found: {input_path}")
            return 1

        img = Image.open(input_path).convert("RGBA")
        
        # Parse grid
        try:
            gw, gh = map(int, args.grid.lower().split('x'))
        except:
            print(f"ERROR: Invalid grid format '{args.grid}'. Use WxH (e.g. 16x16)")
            return 1

        # Parse offset
        ox, oy = 0, 0
        if args.offset:
            try:
                ox, oy = map(int, args.offset.split(','))
            except:
                print(f"ERROR: Invalid offset format '{args.offset}'. Use X,Y (e.g. 0,10)")
                return 1

        # Parse sprites
        sprites = []
        if not args.sprite:
            print("ERROR: No sprites defined. Use --sprite gx,gy,gw,gh at least once.")
            return 1

        for i, s_str in enumerate(args.sprite):
            try:
                gx, gy, sw, sh = map(int, s_str.split(','))
                sprites.append(SpriteDefinition(gx, gy, sw, sh, i))
            except:
                print(f"ERROR: Invalid sprite format '{s_str}'. Use gx,gy,gw,gh")
                return 1

        options = CompilationOptions(
            output_path=args.out,
            grid_w=gw,
            grid_h=gh,
            offset_x=ox,
            offset_y=oy,
            mode=args.mode
        )

        print(f"Compiling {len(sprites)} sprites...")
        if Exporter.export(img, sprites, options):
            print(f"OK: Generated {args.out}")
            return 0
        else:
            print("ERROR: Export failed.")
            return 1

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        return 1

def main():
    if len(sys.argv) > 1:
        # CLI Mode
        parser = argparse.ArgumentParser(description="PixelRoot32 Sprite Compiler CLI")
        parser.add_argument("input", help="Input PNG file")
        parser.add_argument("--grid", required=True, help="Grid size (WxH, e.g. 16x16)")
        parser.add_argument("--offset", help="Initial offset (X,Y, e.g. 0,0)")
        parser.add_argument("--sprite", action="append", help="Sprite definition (gx,gy,gw,gh). Can be used multiple times.")
        parser.add_argument("--out", default="sprites.h", help="Output header file (.h)")
        parser.add_argument("--mode", choices=["layered", "2bpp", "4bpp"], default="layered", help="Export mode")
        
        args = parser.parse_args()
        sys.exit(run_cli(args))
    else:
        # GUI Mode
        try:
            app = MainWindow()
            app.mainloop()
        except Exception as e:
            print(f"Critical error: {e}")
            input("Press Enter to exit...")

if __name__ == "__main__":
    main()
