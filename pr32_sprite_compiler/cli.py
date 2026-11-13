"""CLI and GUI launcher for pr32-sprite-compiler."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

from PIL import Image

from pr32_sprite_compiler.core.exporter import Exporter
from pr32_sprite_compiler.core.models import CompilationOptions, SpriteDefinition
from pr32_sprite_compiler.core.naming import symbol_error


def run_cli(args: argparse.Namespace) -> int:
    """Execute compilation from parsed CLI arguments."""
    try:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"ERROR: Input file not found: {input_path}")
            return 1

        img = Image.open(input_path).convert("RGBA")

        try:
            gw, gh = map(int, args.grid.lower().split("x"))
        except Exception:
            print(f"ERROR: Invalid grid format '{args.grid}'. Use WxH (e.g. 16x16)")
            return 1

        ox, oy = 0, 0
        if args.offset:
            try:
                ox, oy = map(int, args.offset.split(","))
            except Exception:
                print(f"ERROR: Invalid offset format '{args.offset}'. Use X,Y (e.g. 0,10)")
                return 1

        if not args.sprite:
            print("ERROR: No sprites defined. Use --sprite gx,gy,gw,gh at least once.")
            return 1

        sprites = []
        for i, s_str in enumerate(args.sprite):
            try:
                gx, gy, sw, sh = map(int, s_str.split(","))
                sprites.append(SpriteDefinition(gx, gy, sw, sh, i))
            except Exception:
                print(f"ERROR: Invalid sprite format '{s_str}'. Use gx,gy,gw,gh")
                return 1

        names = args.sprite_name or []
        if names:
            if len(names) != len(sprites):
                print(
                    "ERROR: --sprite-name must be given once per --sprite "
                    f"(got {len(names)} name(s) for {len(sprites)} sprite(s))."
                )
                return 1

            seen = set()
            for name in names:
                reason = symbol_error(name)
                if reason:
                    print(f"ERROR: Invalid sprite name '{name}': {reason}")
                    return 1
                if name in seen:
                    print(
                        f"ERROR: Duplicate sprite name '{name}'. Sprite names become "
                        "distinct symbols in the header, so they must be unique."
                    )
                    return 1
                seen.add(name)

            for s_def, name in zip(sprites, names):
                s_def.name = name

        options = CompilationOptions(
            output_path=args.out,
            grid_w=gw,
            grid_h=gh,
            offset_x=ox,
            offset_y=oy,
            mode=args.mode,
            name_prefix=args.prefix or "",
        )

        print(f"Compiling {len(sprites)} sprites...")
        if Exporter.export(img, sprites, options):
            print(f"OK: Generated {args.out}")
            return 0

        print("ERROR: Export failed.")
        return 1

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PixelRoot32 Sprite Compiler CLI")
    parser.add_argument("input", help="Input PNG file")
    parser.add_argument("--grid", required=True, help="Grid size (WxH, e.g. 16x16)")
    parser.add_argument("--offset", help="Initial offset (X,Y, e.g. 0,0)")
    parser.add_argument(
        "--sprite",
        action="append",
        help="Sprite definition (gx,gy,gw,gh). Can be used multiple times.",
    )
    parser.add_argument(
        "--sprite-name",
        action="append",
        metavar="NAME",
        help=(
            "C identifier used for this sprite's arrays instead of the index "
            "(SPRITE_<n>). Give one name per --sprite, in the same order. "
            "Can be used multiple times."
        ),
    )
    parser.add_argument("--out", default="sprites.h", help="Output header file (.h)")
    parser.add_argument(
        "--mode",
        choices=["layered", "2bpp", "4bpp"],
        default="layered",
        help="Export mode",
    )
    parser.add_argument(
        "--prefix",
        help=(
            "Prefix for the generated sprite names. A prefix also makes the generated "
            "arrays inline constexpr (single copy in flash across .cpp files), so use "
            "a unique prefix per sprite sheet within a game"
        ),
    )
    return parser


def run_gui() -> int:
    """Launch the optional GUI (requires [gui] extras)."""
    try:
        from pr32_sprite_compiler.gui.main_window import MainWindow
    except ImportError as e:
        print(f"ERROR: GUI dependencies are not installed ({e}).")
        print("Install with: pip install 'pr32-sprite-compiler[gui]'")
        return 1

    try:
        app = MainWindow()
        app.mainloop()
        return 0
    except Exception as e:
        print(f"Critical error: {e}")
        try:
            input("Press Enter to exit...")
        except EOFError:
            pass
        return 1


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Entry point for console script and ``python -m pr32_sprite_compiler``."""
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) > 0:
        args = build_parser().parse_args(list(argv))
        return run_cli(args)

    return run_gui()


if __name__ == "__main__":
    raise SystemExit(main())
