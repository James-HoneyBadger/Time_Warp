"""
JAMES Core Module
================

Core functionality for the JAMES IDE including:
- Main interpreter engine
- Language processing modules
- Core utilities and constants
"""

__version__ = "2.0.0"
__author__ = "JAMES Development Team"

from .interpreter import JAMESInterpreter
from . import languages
from . import utilities

__all__ = ['JAMESInterpreter', 'languages', 'utilities']