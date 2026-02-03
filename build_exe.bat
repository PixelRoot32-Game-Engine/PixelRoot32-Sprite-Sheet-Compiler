@echo off
echo Building PixelRoot32 Sprite Compiler...
pyinstaller --noconsole --onefile --clean --name "PixelRoot32SpriteCompiler" --icon "assets\pr32_logo.ico" --add-data "assets;assets" main.py
echo.
echo Build complete! Executable should be in the "dist" folder.
pause
