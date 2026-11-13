"""Tests for per-sprite names (`--sprite-name` and `SpriteDefinition.name`).

- A sprite name replaces the index stem: `HERO_LAYER_0`, `HERO_2BPP`,
  `HERO_4BPP`; `--prefix` still applies, so a prefixed named sprite is
  `PLAYER_HERO_4BPP`.
- Without a name the symbols keep the v0.4.0 form `SPRITE_<index>_...` and the
  header text is byte-identical to an export of an unnamed sprite (the pinned
  v0.3.1/v0.4.0 literals in `test_export_storage.py` guard that too).
- The CLI requires exactly one `--sprite-name` per `--sprite`, rejects names
  that are not C identifiers, and rejects duplicates.
"""
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from PIL import Image

from pr32_sprite_compiler.core import CompilationOptions, SpriteDefinition, compile_sprite_sheet
from pr32_sprite_compiler.core.naming import is_valid_c_identifier, symbol_error

REPO_ROOT = Path(__file__).parent.parent
# Subset of PALETTE_NES, so 2bpp/4bpp take the predefined-palette branch and emit
# no PALETTE_MAPPING array (same fixture idea as test_export_storage).
COLORS = [(0, 0, 0), (255, 241, 232), None]
ARRAY_LINE = re.compile(r"^(static const|inline constexpr) \w+\s+(\w+)\[", re.MULTILINE)


def make_image(cells=2):
    """Two-cell test sheet; column/row pattern reused from test_export_storage."""
    img = Image.new("RGBA", (8 * cells, 2), (0, 0, 0, 0))
    for x in range(img.width):
        color = COLORS[x % len(COLORS)]
        if color is not None:
            img.putpixel((x, 0), color + (255,))
            img.putpixel((img.width - 1 - x, 1), color + (255,))
    return img


def export_header(sprites, mode, prefix, out_dir):
    out_path = Path(out_dir) / f"{mode}_{prefix.strip() or 'none'}.h"
    options = CompilationOptions(8, 2, 0, 0, mode, str(out_path), prefix)
    assert compile_sprite_sheet(make_image(), sprites, options)
    return out_path.read_bytes().decode("utf-8")


def symbol_names(text):
    return [name for _, name in ARRAY_LINE.findall(text)]


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "pr32_sprite_compiler", *args],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )


class NamingTests(unittest.TestCase):
    def test_accepts_c_identifiers(self):
        for name in ("HERO", "hero", "_private", "Fighter2", "a", "SPRITE_0_LAYER_0"):
            with self.subTest(name=name):
                self.assertTrue(is_valid_c_identifier(name))
                self.assertIsNone(symbol_error(name))

    def test_rejects_empty_name(self):
        self.assertFalse(is_valid_c_identifier(""))
        self.assertEqual(symbol_error(""), "name must not be empty")

    def test_rejects_invalid_identifiers(self):
        for name in ("1hero", "hero-two", "hero two", "hero.name", "HERO!", "héroe"):
            with self.subTest(name=name):
                self.assertFalse(is_valid_c_identifier(name))
                self.assertEqual(
                    symbol_error(name),
                    "not a valid C identifier (use [A-Za-z_][A-Za-z0-9_]*)",
                )


class NamedExportTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.out_dir = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def test_named_sprite_uses_name_in_layered_mode(self):
        text = export_header([SpriteDefinition(0, 0, 1, 1, 0, "HERO")], "layered", "", self.out_dir)
        self.assertEqual(symbol_names(text), ["HERO_LAYER_0", "HERO_LAYER_1"])
        self.assertNotIn("SPRITE_0_LAYER", text)

    def test_named_sprite_uses_name_in_packed_modes(self):
        for mode in ("2bpp", "4bpp"):
            with self.subTest(mode=mode):
                text = export_header([SpriteDefinition(0, 0, 1, 1, 0, "HERO")], mode, "", self.out_dir)
                self.assertEqual(symbol_names(text), [f"HERO_{mode.upper()}"])

    def test_prefix_and_name_combine(self):
        for mode in ("layered", "2bpp", "4bpp"):
            with self.subTest(mode=mode):
                text = export_header([SpriteDefinition(0, 0, 1, 1, 0, "HERO")], mode, "PLAYER", self.out_dir)
                self.assertTrue(all(name.startswith("PLAYER_HERO_") for name in symbol_names(text)))
                self.assertIn("inline constexpr", text)
        layered = export_header([SpriteDefinition(0, 0, 1, 1, 0, "HERO")], "layered", "PLAYER", self.out_dir)
        self.assertEqual(symbol_names(layered), ["PLAYER_HERO_LAYER_0", "PLAYER_HERO_LAYER_1"])

    def test_unnamed_sprite_keeps_index_symbols_and_identical_output(self):
        unnamed = export_header([SpriteDefinition(0, 0, 1, 1, 0)], "4bpp", "PLAYER", self.out_dir)
        empty_name = export_header(
            [SpriteDefinition(0, 0, 1, 1, 0, name="")], "4bpp", "PLAYER", self.out_dir
        )
        self.assertEqual(symbol_names(unnamed), ["PLAYER_SPRITE_0_4BPP"])
        self.assertEqual(unnamed, empty_name)

    def test_mixed_named_and_unnamed_sprites(self):
        sprites = [SpriteDefinition(0, 0, 1, 1, 0, "HERO"), SpriteDefinition(1, 0, 1, 1, 1)]
        text = export_header(sprites, "4bpp", "PLAYER", self.out_dir)
        self.assertEqual(symbol_names(text), ["PLAYER_HERO_4BPP", "PLAYER_SPRITE_1_4BPP"])
        self.assertIn("// Sprite 0 Dimensions: 8x2\n", text)
        self.assertIn("// Sprite 1 Dimensions: 8x2\n", text)


class SpriteNameCliTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.image = self.tmp / "sheet.png"
        make_image().save(self.image)
        self.out = self.tmp / "sprites.h"

    def tearDown(self):
        self._tmp.cleanup()

    def _cli(self, *extra):
        return run_cli(str(self.image), "--grid", "8x2", "--out", str(self.out), *extra)

    def test_named_sprites_use_their_names(self):
        result = self._cli(
            "--mode", "4bpp",
            "--prefix", "GAME",
            "--sprite", "0,0,1,1",
            "--sprite", "1,0,1,1",
            "--sprite-name", "HERO",
            "--sprite-name", "FOE",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(f"OK: Generated {self.out}", result.stdout)
        text = self.out.read_bytes().decode("utf-8")
        self.assertEqual(symbol_names(text), ["GAME_HERO_4BPP", "GAME_FOE_4BPP"])

    def test_without_names_uses_index_symbols_and_matches_library_output(self):
        result = self._cli("--mode", "4bpp", "--prefix", "GAME",
                           "--sprite", "0,0,1,1", "--sprite", "1,0,1,1")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        text = self.out.read_bytes().decode("utf-8")
        self.assertEqual(symbol_names(text), ["GAME_SPRITE_0_4BPP", "GAME_SPRITE_1_4BPP"])
        # Previous behaviour: the header is exactly what the library writes for
        # the same input when no sprite carries a name.
        library = export_header(
            [SpriteDefinition(0, 0, 1, 1, 0), SpriteDefinition(1, 0, 1, 1, 1)],
            "4bpp", "GAME", self.tmp,
        )
        self.assertEqual(text, library)

    def test_name_count_must_match_sprite_count(self):
        cases = {
            "too few": ["--sprite-name", "HERO"],
            "too many": ["--sprite-name", "HERO", "--sprite-name", "FOE", "--sprite-name", "EXTRA"],
        }
        for label, names in cases.items():
            with self.subTest(case=label):
                if self.out.exists():
                    self.out.unlink()
                result = self._cli("--mode", "4bpp", "--sprite", "0,0,1,1", "--sprite", "1,0,1,1", *names)
                self.assertEqual(result.returncode, 1)
                self.assertIn(
                    "--sprite-name must be given once per --sprite",
                    result.stdout,
                )
                self.assertFalse(self.out.exists())

    def test_invalid_identifier_is_rejected_with_its_reason(self):
        cases = {
            "1hero": "not a valid C identifier (use [A-Za-z_][A-Za-z0-9_]*)",
            "hero-two": "not a valid C identifier (use [A-Za-z_][A-Za-z0-9_]*)",
            "": "name must not be empty",
        }
        for name, reason in cases.items():
            with self.subTest(name=name):
                if self.out.exists():
                    self.out.unlink()
                result = self._cli("--mode", "4bpp", "--sprite", "0,0,1,1", "--sprite-name", name)
                self.assertEqual(result.returncode, 1)
                self.assertIn(f"ERROR: Invalid sprite name '{name}': {reason}", result.stdout)
                self.assertFalse(self.out.exists())

    def test_duplicate_names_are_rejected(self):
        result = self._cli(
            "--mode", "4bpp",
            "--sprite", "0,0,1,1",
            "--sprite", "1,0,1,1",
            "--sprite-name", "HERO",
            "--sprite-name", "HERO",
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("ERROR: Duplicate sprite name 'HERO'", result.stdout)
        self.assertFalse(self.out.exists())

    def test_help_documents_sprite_name(self):
        result = subprocess.run(
            [sys.executable, "-m", "pr32_sprite_compiler", "--help"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--sprite-name", result.stdout)


if __name__ == "__main__":
    unittest.main()
