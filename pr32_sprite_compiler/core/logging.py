"""Structured logging for PixelRoot32 Sprite Compiler.

Provides configurable logging without GUI dependencies.
Allows setting log level and format for use from
scripts, Suite, or CLI.
"""
import logging
import sys
from typing import Optional
from pathlib import Path

# Main compiler logger
_logger: Optional[logging.Logger] = None

# Default level
_DEFAULT_LEVEL = logging.INFO

# Default format
_DEFAULT_FORMAT = "[%(levelname)s] %(message)s"

# Detailed format for debug
_DETAILED_FORMAT = "[%(levelname)s] %(name)s - %(message)s"


def get_logger() -> logging.Logger:
    """Get the configured compiler logger.
    
    Returns:
        Configured logger ready to use.
    """
    global _logger
    if _logger is None:
        _logger = _setup_logger()
    return _logger


def _setup_logger(
    level: int = _DEFAULT_LEVEL,
    format_str: str = _DEFAULT_FORMAT,
    output: Optional[Path] = None
) -> logging.Logger:
    """Setup the compiler logger.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        format_str: Message format
        output: Optional path for log file
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger("pr32_sprite_compiler")
    logger.setLevel(level)
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Formatter
    formatter = logging.Formatter(format_str)
    
    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if output:
        file_handler = logging.FileHandler(output)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def configure_logging(
    level: str = "INFO",
    detailed: bool = False,
    output: Optional[Path] = None
) -> None:
    """Configure compiler logging.
    
    This function allows configuring logging according to user needs.
    Can be called at program start to set the desired log level.
    
    Args:
        level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR')
        detailed: If True, includes logger name in format
        output: Optional path to save logs to file
        
    Example:
        >>> from pr32_sprite_compiler.core.logging import configure_logging
        >>> configure_logging(level="DEBUG", detailed=True)
        >>> # Now logs will be more detailed
    """
    global _logger
    
    # Map string to logging level
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    
    log_level = level_map.get(level.upper(), logging.INFO)
    format_str = _DETAILED_FORMAT if detailed else _DEFAULT_FORMAT
    
    _logger = _setup_logger(log_level, format_str, output)


def debug(msg: str, *args, **kwargs) -> None:
    """Log DEBUG level message."""
    get_logger().debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs) -> None:
    """Log INFO level message."""
    get_logger().info(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs) -> None:
    """Log WARNING level message."""
    get_logger().warning(msg, *args, **kwargs)


def error(msg: str, *args, **kwargs) -> None:
    """Log ERROR level message."""
    get_logger().error(msg, *args, **kwargs)


def critical(msg: str, *args, **kwargs) -> None:
    """Log CRITICAL level message."""
    get_logger().critical(msg, *args, **kwargs)


def log_compilation_start(options) -> None:
    """Log compilation start with relevant information.
    
    Args:
        options: CompilationOptions with configuration
    """
    logger = get_logger()
    logger.info(f"Starting compilation - Mode: {options.mode}")
    logger.debug(f"Grid: {options.grid_w}x{options.grid_h}")
    logger.debug(f"Offset: ({options.offset_x}, {options.offset_y})")
    logger.debug(f"Output: {options.output_path}")
    if options.name_prefix:
        logger.debug(f"Prefix: {options.name_prefix}")


def log_compilation_success(sprite_count: int, output_path: str) -> None:
    """Log successful compilation completion.
    
    Args:
        sprite_count: Number of compiled sprites
        output_path: Path of generated file
    """
    logger = get_logger()
    logger.info(f"Compilation successful: {sprite_count} sprites -> {output_path}")


def log_compilation_error(error_msg: str) -> None:
    """Log error during compilation.
    
    Args:
        error_msg: Descriptive error message
    """
    logger = get_logger()
    logger.error(f"Compilation error: {error_msg}")
