<p align="center">
  <img src="assets/pr32_logo.png" alt="PixelRoot32 Logo" width="320">
</p>

# PixelRoot32 Sprite Compiler (`pr32-sprite-compiler`)

`pr32-sprite-compiler.py` is a Python command-line tool that converts a **PNG sprite sheet** into a C header file (`.h`) compatible with the **PixelRoot32** engine. A small GUI wrapper (`pr32-sprite-compiler-gui.py`) is included so you can use the tool without typing commands in a terminal.

For every defined sprite it generates one or more arrays:

```c
static const uint16_t SPRITE_0_LAYER_0[] = { /* bit data */ };
static const uint16_t SPRITE_0_LAYER_1[] = { /* bit data */ };
/* ... */
```

Each array represents a **color layer** of the same sprite. PixelRoot32 can combine these layers at render time.

For the engine that consumes these headers, see the PixelRoot32 Game Engine repository: [PixelRoot32-Game-Engine](https://github.com/Gperez88/PixelRoot32-Game-Engine)

---

## 1. Requirements

- **Python**
  - Recommended minimum: **Python 3.8+**
  - Developed and tested with Python 3.x on **Windows 10/11**.

- **Dependencies**
  - [Pillow](https://python-pillow.org/) (PIL fork)

- **Supported operating systems**
  - Any OS with Python 3.x and Pillow installed.
  - The tool should also run on Linux/macOS, but this path is currently considered **experimental** and may require additional setup or tweaks.
  - Examples and notes focus on **Windows / PowerShell**.

---

## 2. Installation

### 2.1 Install Python

1. Download Python from:
   - [python.org](https://www.python.org/downloads/)
2. During installation on Windows:
   - Check **"Add Python to PATH"**.

To verify that Python is installed:

```powershell
python --version
```

or, depending on the installation:

```powershell
py --version
```

### 2.2 Install Pillow

Install Pillow with `pip`:

```powershell
python -m pip install pillow
```

On Linux/macOS:

```bash
python3 -m pip install pillow
```

### 2.3 Verification

Check that Pillow imports correctly:

```powershell
python -c "from PIL import Image; print('Pillow OK')"
```

You should see:

```text
Pillow OK
```

---

## 3. Usage

### 3.1 GUI (recommended)

For most users (artists, technical designers), the GUI is the easiest way to use the compiler. It is a thin wrapper around `pr32-sprite-compiler.py` and internally calls the same script with the same parameters.

#### 3.1.1 Launching the GUI

- From a terminal in this folder:

  ```bash
  python pr32-sprite-compiler-gui.py
  ```

  On Windows you can also double‑click the file if `.py` files are associated with Python, but running from a terminal lets you see any startup errors.

#### 3.1.2 Fields and workflow

The window contains:

- **Input PNG**  
  - Click **Browse...** and select your sprite sheet (`.png`).

- **Grid (WxH)**  
  - Same meaning as `--grid` in the CLI.  
  - Enter the sprite cell size in pixels, e.g. `16x32`.

- **Sprite count (per row)**  
  - Optional helper for auto‑detection.  
  - If you know how many sprites there are in the first row, enter it here (e.g. `9`).

- **Offset (X,Y)**  
  - Same as `--offset` in the CLI.  
  - Use this if the first row of sprites is not at the very top of the image (e.g. `0,10`).

- **Output .h**  
  - Target header file name (e.g. `sprites_player.h`).  
  - Use **Browse...** to pick a location.

- **Auto-detect**  
  - After filling **Input PNG**, optionally **Sprite count (per row)**, and **Output .h**, click **Auto-detect**.  
  - The GUI analyzes the image and tries to:
    - Infer a suitable grid size.
    - Detect the vertical offset.
    - Populate the sprite list with one sprite per cell in the first row.
  - You can then correct any values manually.

- **Sprites (gx, gy, gw, gh)**  
  - List of sprite definitions in grid units (same meaning as the CLI `--sprite` options).  
  - Use the small form on the right to:
    - **Add / Update** a sprite.
    - **Remove** the selected sprite.
    - **Clear** the list.

- **Compile**  
  - Runs `pr32-sprite-compiler.py` with the parameters defined in the GUI.  
  - The button is disabled while compilation is in progress and re‑enabled when it finishes.

- **Log**  
  - Shows:
    - The exact command used to call `pr32-sprite-compiler.py`.
    - Progress and output produced by the script (streamed while it runs).
    - Messages from **Auto-detect**.  
  - The log is **not cleared** between operations, so you can see the history of actions.

If something goes wrong (missing file, invalid grid, etc.), the GUI shows an error dialog and logs the details in the log area.

### 3.2 Command-line usage (optional)

The command-line interface is useful for automation, scripting, or integration into build pipelines. It is optional; the GUI is the recommended entry point for manual usage.

#### 3.2.1 General syntax

```bash
python pr32-sprite-compiler.py INPUT.png \
  --grid WxH \
  [--offset X,Y] \
  --sprite gx,gy,gw,gh \
  [--sprite gx,gy,gw,gh ...] \
  [--out output_file.h]
```

On Windows / PowerShell (multi-line) using the backtick:

```powershell
python .\pr32-sprite-compiler.py `
  assets\player_sprites.png `
  --grid 16x32 `
  --offset 0,10 `
  --sprite 0,0,1,1 `
  --sprite 1,0,1,1 `
  --sprite 2,0,1,1 `
  --out sprites_player.h
```

#### 3.2.2 Parameters

- **`INPUT.png` (positional)**  
  Path to the PNG sprite sheet.

- **`--grid WxH` (required)**  
  Grid cell size in pixels.  
  `W` = width of each grid cell.  
  `H` = height of each grid cell.  
  Example: `--grid 16x32`.

- **`--offset X,Y` (optional)**  
  Initial offset in pixels from the top-left corner of the image.  
  `X` = horizontal offset.  
  `Y` = vertical offset.  
  Useful when the first sprite row does not start exactly at `y = 0`.  
  Default: `0,0`.

- **`--sprite gx,gy,gw,gh` (required, repeatable)**  
  Defines a sprite in **grid units** (not pixels):

  - `gx` = starting column (0 = first column)
  - `gy` = starting row (0 = first row)
  - `gw` = width in grid cells (number of columns)
  - `gh` = height in grid cells (number of rows)

  Can be passed **multiple times** to export several sprites in a single run.

- **`--out output_file.h` (optional)**  
  Name of the output `.h` file.  
  Default: `sprites.h`.  
  The script writes the file directly → **do not use shell redirection `>`**.

#### 3.2.3 Full example

Sprite sheet with 9 frames (144×32), sprites of 16×32, first row shifted 10 pixels down:


```powershell
python .\pr32-sprite-compiler.py `
  assets\player_sprites.png `
  --grid 16x32 `
  --offset 0,10 `
  --sprite 0,0,1,1 `
  --sprite 1,0,1,1 `
  --sprite 2,0,1,1 `
  --sprite 3,0,1,1 `
  --sprite 4,0,1,1 `
  --sprite 5,0,1,1 `
  --sprite 6,0,1,1 `
  --sprite 7,0,1,1 `
  --sprite 8,0,1,1 `
  --out sprites_player_all.h
```

---

## 4. Sprite definition and Constraints

### 4.1 Grid and Coordinates
The sprite sheet is conceptually divided into a grid of cells of size `WxH` pixels (`--grid`).

- The position `(gx, gy)` is expressed in **grid cells**.
- The size `(gw, gh)` is the number of cells the sprite occupies.

Example with `--grid 16x16` (4×2 cells):

```text
   gx →
    0      1      2      3
gy  ┌──────┬──────┬──────┬──────┐
↓ 0 │ 0,0  │ 1,0  │ 2,0  │ 3,0  │
   ├──────┼──────┼──────┼──────┤
 1 │ 0,1  │ 1,1  │ 2,1  │ 3,1  │
   └──────┴──────┴──────┴──────┘
```

- Single-cell sprite: `--sprite 1,0,1,1` → cell (1,0), 1×1 cells.  
- Three-cell wide sprite: `--sprite 0,0,3,1` → from (0,0), 3 columns, 1 row.

The offset (`--offset X,Y`) is applied in **pixels** before converting to grid coordinates:

```text
real_x = offset_x + gx * grid_w
real_y = offset_y + gy * grid_h
```

### 4.2 Constraints and Recommendations

- **Max Layers (Performance Warning)**:
  - **Main Characters**: Do not exceed **4 layers**.
  - **Common Enemies/Objects**: Keep it under **2 layers**.
  - **Why?**: Although the engine technically supports up to 255 layers, rendering each layer involves a separate pass. Exceeding these limits can significantly drop the frame rate on standard ESP32 hardware.
  - **Alternative**: If you need more than 4 colors, consider using **4bpp packed sprites** (if supported by your engine version) instead of stacking many 1bpp layers, as it draws the final pixel in a single pass.

- **Palette**: It is strongly recommended to use the **official PixelRoot32 palette** to ensure visual consistency and optimal rendering.
  - Palette file: `assets/pixelroot32_palette.png`
  - Colors outside this palette will still be compiled, but they might not blend correctly with other engine assets.

---

## 5. Output format

The generated `.h` file has this structure:

```c
// Generated by pr32-sprite-compiler
// Engine: PixelRoot32

static const uint16_t SPRITE_0_LAYER_0[] = {
    0x0000,
    0x0C30,
    /* ... */
};

static const uint16_t SPRITE_0_LAYER_1[] = {
    /* ... */
};

/* SPRITE_1_LAYER_0, SPRITE_1_LAYER_1, etc. */
```

### 5.1 Naming convention

- `SPRITE_<N>_LAYER_<L>`
  - `<N>` = sprite index (in the order of the `--sprite` arguments).
  - `<L>` = layer index (in the order of detected colors).

### 5.2 Color layers

- The tool scans the PNG and extracts all distinct **RGB colors** with alpha > 0.
- For each detected color:
  - It generates an independent layer.
  - Within that layer, a bit set to `1` means “this pixel has this color”.
- Combining all layers reproduces the original sprite.

### 5.3 Data layout (words per row)

- Each `uint16_t` represents **up to 16 horizontal pixels**.
  - Bit 15 → leftmost pixel in the word.  
  - Bit 0  → rightmost pixel in the word.
- The number of words per row is:

```text
words_per_row = ceil(sprite_width / 16)
```

- Rows are written from top to bottom.
- If the sprite width is not a multiple of 16, the extra bits on the right are 0.

---

## 6. Common errors and fixes

### 6.1 PNG file not found

Typical message:

```text
ERROR: input file not found: assets/foo.png
```

Fix:

- Check the relative path from the directory where you run the command.
- On Windows, escape paths with spaces or use quotes:

```powershell
python .\pr32-sprite-compiler.py "assets\player sprites.png" --grid 16x32 ...
```

### 6.2 Pillow not installed

Typical message:

```text
ModuleNotFoundError: No module named 'PIL'
```

Fix:

```powershell
python -m pip install pillow
```

If you have multiple Python installations, make sure you use the same `python` to install and to run the script.

### 6.3 Incorrect use of `>` redirection in PowerShell

Do **not** do this:

```powershell
python .\pr32-sprite-compiler.py ... > sprites.h
```

- The tool **already writes** the `.h` file.
- Redirection `>` can truncate the file or capture only console output (which is minimal).

Always use the `--out` parameter:

```powershell
python .\pr32-sprite-compiler.py ... --out sprites_player.h
```

### 6.4 Encoding or newline warnings when compiling with GCC

The tool writes:

- File encoded as **UTF‑8**.  
- Unix newlines (`\n`).

If GCC warns about encoding:

- Make sure the compiler expects UTF‑8:

```bash
gcc -Wall -Wextra -finput-charset=UTF-8 ...
```

- Alternatively, remove or edit the initial comments if your toolchain has strict encoding requirements.

### 6.5 Narrowing conversion errors

The generated data is `uint16_t`. Typical issue:

```c++
uint8_t data[] = {
    0xFFFF, // narrowing conversion from 'int' to 'uint8_t'
};
```

Fixes:

- Always use `uint16_t` for arrays that store this data:

```c
static const uint16_t* sprite_layer = SPRITE_0_LAYER_0;
```

- If you need to copy into another type, cast explicitly and be aware of data loss:

```c++
uint8_t dst = (uint8_t)(SPRITE_0_LAYER_0[i] & 0xFF);
```

---

## 7. Notes for PixelRoot32

### 7.1 Consuming the data

Typical assumptions when integrating into the engine:

- You know in advance:
  - Sprite width and height in pixels (from `--grid` and `gw`, `gh`).
  - Number of layers per sprite (length of the `colors` list).
- Each sprite is represented as a set of pointers to arrays:

```c
extern const uint16_t SPRITE_0_LAYER_0[];
extern const uint16_t SPRITE_0_LAYER_1[];
/* ... */
```

In the engine you can pack this information into your own structure:

```c
typedef struct {
    const uint16_t* layers;
    int layer_count;
    int width;
    int height;
} PR32_Sprite;
```

(The concrete design depends on your rendering API.)

### 7.2 Tool assumptions

- It does not rescale the image.
- It does not reorder or filter colors:
  - Layer order is given by the order in which unique colors are discovered.
- It considers only pixels with `alpha > 0` as “active”.
- It assumes sprites fit fully inside the image based on the offset and grid.
  - If they do not, it crops what exists and pads the rest with transparency.

### 7.3 What the tool does **not** do

- It does **not**:
  - Rescale sprites.
  - Change the color palette.
  - Generate high-level code (structs, animation tables, etc.).
  - Optimize layers (e.g. merge colors or remove empty layers).
  - Validate that sprite parameters make sense for your game design.

The goal is to be a **purely mechanical** stage: convert pixels into bitfields stored in `uint16_t` arrays, ready to be consumed by PixelRoot32 and your own engine tooling.

---

## 8. Building standalone executables

You can bundle the GUI into a standalone binary (no Python installation required) using [PyInstaller](https://pyinstaller.org/).

### 8.1 Prerequisites

- Python 3.8+ installed.
- PyInstaller:

  ```bash
  pip install pyinstaller
  ```

### 8.2 Windows `.exe`

From the project root (where [pr32-sprite-compiler-gui.py](pr32-sprite-compiler-gui.py) and [pr32-sprite-compiler.py](pr32-sprite-compiler.py) live), run:

```powershell
pyinstaller --noconsole --onefile --add-data "pr32-sprite-compiler.py;." pr32-sprite-compiler-gui.py
```

Notes:

- `--onefile` produces a single `pr32-sprite-compiler-gui.exe`.
- `--noconsole` hides the console window (GUI only).
- `--add-data "pr32-sprite-compiler.py;."` embeds the CLI script inside the binary.

The resulting executable will be located at:

- `dist\pr32-sprite-compiler-gui.exe`

You can distribute this file as a binary release or commit it under a `bin/` directory if you wish.

### 8.3 Linux / macOS binary

The same approach works on Linux/macOS, but the `--add-data` separator changes from `;` to `:`:

```bash
pyinstaller --noconsole --onefile --add-data "pr32-sprite-compiler.py:." pr32-sprite-compiler-gui.py
```

The resulting binary will be placed in the `dist/` folder (e.g. `dist/pr32-sprite-compiler-gui`).

> The GUI has been written to work both as a plain Python script and as a PyInstaller-frozen executable. At runtime it automatically locates and executes `pr32-sprite-compiler.py` from the bundled files.
