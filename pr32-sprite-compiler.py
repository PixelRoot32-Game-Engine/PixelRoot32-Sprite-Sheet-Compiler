#!/usr/bin/env python3
from PIL import Image
import argparse
from pathlib import Path
import sys

def parse_grid(value):
    w, h = value.lower().split("x")
    return int(w), int(h)

def parse_sprite(value):
    gx, gy, gw, gh = value.split(",")
    return int(gx), int(gy), int(gw), int(gh)

def extract_colors(img):
    pixels = img.load()
    colors = set()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = pixels[x, y]
            if a > 0:
                colors.add((r, g, b))
    return sorted(colors)

def sprite_to_bits(sprite, color):
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

def pack_2bpp(sprite, palette_map):
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

def pack_4bpp(sprite, palette_map):
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

def main():
    parser = argparse.ArgumentParser(
        description="PixelRoot32 sprite sheet compiler"
    )
    parser.add_argument("input", help="Input PNG sprite sheet")
    parser.add_argument("--grid", required=False, help="Grid size WxH (e.g. 16x16)")
    parser.add_argument(
        "--offset",
        default="0,0",
        help="Grid offset X,Y (default: 0,0)",
    )
    parser.add_argument(
        "--sprite",
        action="append",
        required=False,
        help="Sprite definition gx,gy,gw,gh (grid units)",
    )
    parser.add_argument(
        "--out",
        default="sprites.h",
        help="Output header file (default: sprites.h)",
    )
    parser.add_argument(
        "--mode",
        choices=["layered", "2bpp", "4bpp"],
        default="layered",
        help="Export mode: layered (default), 2bpp, or 4bpp"
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: input file not found: {input_path}")
        sys.exit(1)

    img = Image.open(input_path).convert("RGBA")
    
    if args.grid:
        grid_w, grid_h = parse_grid(args.grid)
    else:
        # Auto-detect grid logic (ported from GUI)
        width, height = img.size
        
        def divisors(n: int):
            result = set()
            limit = int(n**0.5) + 1
            for d in range(1, limit):
                if n % d == 0:
                    result.add(d)
                    result.add(n // d)
            return sorted(result)

        candidates = [d for d in divisors(width) if 8 <= d <= width]
        preferred = [16, 32, 8, 24, 48, 64]
        
        grid_w = None
        for p in preferred:
            if p in candidates:
                grid_w = p
                break
        
        if grid_w is None:
            if candidates:
                grid_w = max(candidates)
            else:
                grid_w = width
        
        grid_h = grid_w # Assume square grid cells for auto-detect
        print(f"INFO: Auto-detected grid size: {grid_w}x{grid_h}")

    offset_x, offset_y = 0, 0
    if args.offset:
        ox, oy = args.offset.split(",")
        offset_x, offset_y = int(ox), int(oy)

    if args.sprite:
        sprites = [parse_sprite(s) for s in args.sprite]
    else:
        # Auto-generate sprites filling the grid (ported from GUI)
        cols = max(1, img.width // grid_w)
        rows = max(1, img.height // grid_h)
        sprites = []
        for gy in range(rows):
            for gx in range(cols):
                sprites.append((gx, gy, 1, 1))
        print(f"INFO: Auto-generated {len(sprites)} sprites ({cols} cols x {rows} rows).")

    colors = extract_colors(img)

    if args.mode == "layered":
        if len(colors) > 4:
            print(f"WARNING: Detected {len(colors)} colors (layers).")
            print("         Performance may degrade on ESP32 if using > 4 layers for main characters.")
            print("         Consider using 4bpp packed sprites for higher color counts.")

    # Palette mapping for packed modes
    palette_map = {}
    if args.mode in ["2bpp", "4bpp"]:
        # Index 0 is reserved for transparency
        max_colors = 3 if args.mode == "2bpp" else 15
        if len(colors) > max_colors:
            print(f"WARNING: Detected {len(colors)} colors, but {args.mode} supports max {max_colors} (+transparency).")
            print("         Some colors will be mapped to the last index or ignored.")
        
        for i, color in enumerate(colors):
            if i < max_colors:
                palette_map[color] = i + 1
            else:
                # Map extra colors to the last valid index
                palette_map[color] = max_colors

    out_path = Path(args.out)

    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("// Generated by pr32-sprite-compiler\n")
        f.write("// Engine: PixelRoot32\n")
        f.write(f"// Mode: {args.mode}\n\n")

        # Write palette info if packed
        if args.mode in ["2bpp", "4bpp"]:
             f.write(f"// Palette ({len(palette_map)} colors + transparent):\n")
             f.write("// Index 0: Transparent\n")
             # Sort map by index to list
             inv_map = {v: k for k, v in palette_map.items() if v in palette_map.values()}
             # Note: multiple colors might map to same index if overflow, just showing unique indices
             processed_indices = set()
             for i in range(1, max(palette_map.values()) + 1 if palette_map else 1):
                 # Find a color that maps to i
                 for c, idx in palette_map.items():
                     if idx == i and i not in processed_indices:
                         r, g, b = c
                         f.write(f"// Index {i}: RGB({r}, {g}, {b})\n")
                         processed_indices.add(i)
                         break
             f.write("\n")

        for idx, (gx, gy, gw, gh) in enumerate(sprites):

            x = offset_x + gx * grid_w
            y = offset_y + gy * grid_h
            w = gw * grid_w
            h = gh * grid_h

            # Crop and pad if necessary
            cropped = img.crop((x, y, x + w, y + h))
            sprite = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            sprite.paste(cropped, (0, 0))

            if args.mode == "layered":
                for layer, color in enumerate(colors):
                    bits = sprite_to_bits(sprite, color)
                    name = f"SPRITE_{idx}_LAYER_{layer}"

                    f.write(f"static const uint16_t {name}[] = {{\n")
                    for row in bits:
                        for word in row:
                            f.write(f"    0x{word:04X},\n")
                    f.write("};\n\n")
            
            elif args.mode == "2bpp":
                bits = pack_2bpp(sprite, palette_map)
                name = f"SPRITE_{idx}_2BPP"
                f.write(f"static const uint16_t {name}[] = {{\n")
                for row in bits:
                    for word in row:
                        f.write(f"    0x{word:04X},\n")
                f.write("};\n\n")

            elif args.mode == "4bpp":
                bits = pack_4bpp(sprite, palette_map)
                name = f"SPRITE_{idx}_4BPP"
                f.write(f"static const uint16_t {name}[] = {{\n")
                for row in bits:
                    for word in row:
                        f.write(f"    0x{word:04X},\n")
                f.write("};\n\n")

    print(f"OK: generated {out_path}")

if __name__ == "__main__":
    main()
