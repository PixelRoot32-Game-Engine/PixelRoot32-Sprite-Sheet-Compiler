from PIL import Image
import os

src = r"c:\Users\gperez88\Documents\Proyects\Games\pixelroot32 workspace\PixelRoot32 Sprite Compiler\assets\pr32_logo.png"
dst = r"c:\Users\gperez88\Documents\Proyects\Games\pixelroot32 workspace\PixelRoot32 Sprite Compiler\assets\pr32_logo.ico"

try:
    img = Image.open(src)
    # Icon sizes for Windows
    icon_sizes = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]
    img.save(dst, sizes=icon_sizes)
    print(f"OK: Created {dst}")
except Exception as e:
    print(f"Error: {e}")
