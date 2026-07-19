"""Legacy launcher kept for local runs and PyInstaller specs.

Prefer the installed console script ``pr32-sprite-compiler`` or
``python -m pr32_sprite_compiler``.
"""

from pr32_sprite_compiler.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
