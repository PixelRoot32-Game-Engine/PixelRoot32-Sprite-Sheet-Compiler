"""Validation of user-provided C identifiers.

Sprite names become C symbols, so they must be valid C identifiers. These
helpers are pure (no argparse, no I/O) so the CLI, the GUI and the Suite can
apply exactly the same rules.
"""
import re
from typing import Optional

_C_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def is_valid_c_identifier(name: str) -> bool:
    """True when ``name`` is a non-empty C identifier."""
    return bool(name) and _C_IDENTIFIER.match(name) is not None


def symbol_error(name: str) -> Optional[str]:
    """Return a short reason why ``name`` cannot be a symbol, or None if it can."""
    if not name:
        return "name must not be empty"
    if not is_valid_c_identifier(name):
        return "not a valid C identifier (use [A-Za-z_][A-Za-z0-9_]*)"
    return None
