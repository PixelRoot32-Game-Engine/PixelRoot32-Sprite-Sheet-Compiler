"""Custom exceptions for PixelRoot32 Sprite Compiler.

This module defines specific exceptions for compilation errors,
validation errors, and compiler operations. Provides clear error
messages and allows granular error handling.
"""
from typing import Optional


class CompilerError(Exception):
    """Base exception for compiler errors.
    
    Attributes:
        message: Descriptive error message
        context: Additional context (optional)
    """
    
    def __init__(self, message: str, context: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.context = context or {}
    
    def __str__(self):
        if self.context:
            ctx_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} ({ctx_str})"
        return self.message


class CompilationError(CompilerError):
    """Error during the compilation process.
    
    Raised when there are problems generating C code,
    such as file writing errors, permission issues, etc.
    
    Example:
        >>> try:
        ...     compile_sprite_sheet(img, sprites, options)
        ... except CompilationError as e:
        ...     print(f"Compilation error: {e}")
    """
    pass


class ValidationError(CompilerError):
    """Parameter validation error.
    
    Raised when input parameters are not valid,
    such as incorrect dimensions, unsupported modes, etc.
    
    Attributes:
        field: Name of the field that failed validation
        value: Invalid value provided
        
    Example:
        >>> try:
        ...     options = CompilationOptions(grid_w=-1, ...)
        ... except ValidationError as e:
        ...     print(f"Error in {e.field}: {e.message}")
    """
    
    def __init__(self, message: str, field: Optional[str] = None, value=None, context: Optional[dict] = None):
        super().__init__(message, context)
        self.field = field
        self.value = value
    
    def __str__(self):
        base_msg = super().__str__()
        if self.field:
            return f"[{self.field}] {base_msg}"
        return base_msg


class ImageError(CompilerError):
    """Image-related error.
    
    Raised when there are problems loading or processing images,
    such as unsupported formats, corrupted images, etc.
    """
    pass


class PaletteError(CompilerError):
    """Color palette error.
    
    Raised when there are problems with palettes, such as
    colors not found, invalid palettes, etc.
    """
    pass


class ExportError(CompilerError):
    """Export error.
    
    Raised when there are problems exporting to different formats.
    """
    pass
