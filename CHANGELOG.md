# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.3.0-dev] - 2026-02-02

### Added

- **Sprite Sheet Preview**: Integrated a dynamic preview panel with zoom and grid visualization.
- **Pixel-Art Zoom**: Added support for 0.1x to 10x zoom using `Image.NEAREST` interpolation to maintain pixel clarity.
- **Interactive Navigation**: Added Panning (Space + Left Click) and Mouse Wheel Zoom for easier inspection of large sprite sheets.
- **Two-Column Layout**: Redesigned the GUI with a scrollable sidebar for controls and a dedicated main area for the preview.
- **Individual Tile Fields**: Replaced combined input fields with specific Spinboxes for Tile Width, Height, and Offsets (X, Y).
- **Auto-Preview Synchronization**: The preview now updates automatically when input paths or tile settings change.
- **High Quality Asset**: Generated a multi-size high-quality `.ico` icon for the application.

## [v0.2.0-dev] - 2024-01-20

### Added

- **Dimension Comments**: Added width/height comments in the generated header files for easier debugging.
- **Experimental Label**: Added experimental status notes for non-Windows platforms in documentation.

### Changed

- **Modular Project Structure**: Restructured the project into a modular `src/` layout (core, gui, services).
- **Unified Interface**: Unified the CLI and GUI logic for better maintainability and consistency.
- **Packing Functions**: Implemented new packing functions for 2BPP and 4BPP sprite formats.
- **Mode Selection**: Added mode selection to both CLI and GUI interfaces.
- **Header Metadata**: Included palette information in output header for packed modes.

## [v0.1.0-dev] - 2023-11-15

### Added

- **Initial Release**: Pre-release of the PixelRoot32 Sprite Compiler GUI.
- **Windows Executable**: Standalone Windows executable `pr32-sprite-compiler-gui.exe`.
- **Tkinter GUI**: Tkinter-based GUI wrapper for the core compiler logic.
- **Auto-Detection**: Image-based auto-detection of grid, offset, and sprite list (Experimental).
- **Log Console**: Integrated log console with live compiler output.
- **Export Modes**: Support for layered (1BPP), 2BPP, and 4BPP for packed sprite output.

### Fixed

- **Platform Notes**: Documented that developed and tested on Windows 10/11 only; Linux/macOS support is experimental.
