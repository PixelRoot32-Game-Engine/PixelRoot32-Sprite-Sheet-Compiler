from PIL import Image
import os

png_path = r'assets/pr32_logo.png'
ico_path = r'assets/pr32_logo.ico'

if os.path.exists(png_path):
    img = Image.open(png_path)
    # Generate multiple sizes for high quality ICO
    icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(ico_path, sizes=icon_sizes)
    print(f"Successfully generated {ico_path}")
else:
    print(f"Error: {png_path} not found")
