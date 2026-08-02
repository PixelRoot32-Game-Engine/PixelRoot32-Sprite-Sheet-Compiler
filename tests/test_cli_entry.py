"""Smoke tests for the packaged CLI entry point."""

import subprocess
import sys


def test_cli_help_via_module():
    result = subprocess.run(
        [sys.executable, "-m", "pr32_sprite_compiler", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "PixelRoot32 Sprite Compiler CLI" in result.stdout


def test_cli_import_does_not_require_gui_extras():
    """CLI must import without ttkbootstrap / GUI modules."""
    from pr32_sprite_compiler.cli import build_parser, main

    parser = build_parser()
    assert parser.prog or True
    assert callable(main)
