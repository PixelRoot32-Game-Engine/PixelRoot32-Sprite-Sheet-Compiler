from PIL import Image
from typing import List, Tuple, Dict, Set
from pr32_sprite_compiler.core.models import SpriteDefinition, CompilationOptions

class SpriteCompiler:
    @staticmethod
    def extract_colors(img: Image.Image) -> List[Tuple[int, int, int]]:
        pixels = img.load()
        colors = set()
        for y in range(img.height):
            for x in range(img.width):
                r, g, b, a = pixels[x, y]
                if a > 0:
                    colors.add((r, g, b))
        return sorted(colors)

    @staticmethod
    def sprite_to_bits(sprite: Image.Image, color: Tuple[int, int, int]) -> List[List[int]]:
        pixels = sprite.load()
        rows = []
        words_per_row = (sprite.width + 15) // 16

        for y in range(sprite.height):
            row_words = [0] * words_per_row
            for x in range(sprite.width):
                r, g, b, a = pixels[x, y]
                if a > 0 and (r, g, b) == color:
                    word = x // 16
                    bit = 15 - (x % 16)
                    row_words[word] |= (1 << bit)
            rows.append(row_words)
        return rows

    @staticmethod
    def pack_2bpp(sprite: Image.Image, palette_map: Dict[Tuple[int, int, int], int]) -> List[List[int]]:
        pixels = sprite.load()
        rows = []
        bits_per_pixel = 2
        row_stride_bits = sprite.width * bits_per_pixel
        row_stride_bytes = (row_stride_bits + 7) // 8

        for y in range(sprite.height):
            row_bytes = [0] * row_stride_bytes
            for x in range(sprite.width):
                r, g, b, a = pixels[x, y]
                idx = 0
                if a > 0:
                    idx = palette_map.get((r, g, b), 0)

                bit_index = x * bits_per_pixel
                byte_index = bit_index >> 3
                shift = bit_index & 7
                row_bytes[byte_index] |= (idx & 0x3) << shift

            words_per_row = (row_stride_bytes + 1) // 2
            row_words = []
            for i in range(words_per_row):
                lo = row_bytes[2 * i] if 2 * i < row_stride_bytes else 0
                hi = row_bytes[2 * i + 1] if 2 * i + 1 < row_stride_bytes else 0
                word = (hi << 8) | lo
                row_words.append(word)
            rows.append(row_words)
        return rows

    @staticmethod
    def pack_4bpp(sprite: Image.Image, palette_map: Dict[Tuple[int, int, int], int]) -> List[List[int]]:
        pixels = sprite.load()
        rows = []
        bits_per_pixel = 4
        row_stride_bits = sprite.width * bits_per_pixel
        row_stride_bytes = (row_stride_bits + 7) // 8

        for y in range(sprite.height):
            row_bytes = [0] * row_stride_bytes
            for x in range(sprite.width):
                r, g, b, a = pixels[x, y]
                idx = 0
                if a > 0:
                    idx = palette_map.get((r, g, b), 0)

                bit_index = x * bits_per_pixel
                byte_index = bit_index >> 3
                shift = bit_index & 7
                row_bytes[byte_index] |= (idx & 0xF) << shift

            words_per_row = (row_stride_bytes + 1) // 2
            row_words = []
            for i in range(words_per_row):
                lo = row_bytes[2 * i] if 2 * i < row_stride_bytes else 0
                hi = row_bytes[2 * i + 1] if 2 * i + 1 < row_stride_bytes else 0
                word = (hi << 8) | lo
                row_words.append(word)
            rows.append(row_words)
        return rows
