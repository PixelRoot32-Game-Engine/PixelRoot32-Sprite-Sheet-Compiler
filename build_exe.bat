@echo off
echo Building PixelRoot32 Sprite Compiler...
pyinstaller --noconsole --onefile --clean --name "PixelRoot32SpriteCompiler" --icon "assets\pr32_logo.ico" --add-data "pr32-sprite-compiler.py;." --add-data "assets\pr32_logo.png;assets" pr32-sprite-compiler-gui.py
echo.
echo Build complete! Executable should be in the "dist" folder.
pause
