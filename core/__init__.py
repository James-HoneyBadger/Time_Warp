"""
TimeWarp Core Module
===================

Core functionality for the TimeWarp IDE including:
- Main interpreter engine
- Language processing modules
- Core utilities and constants
"""

__version__ = "2.0.0"
__author__ = "TimeWarp Development Team"

from .interpreter import TimeWarpInterpreter
from . import languages
from . import utilities

__all__ = ['TimeWarpInterpreter', 'languages', 'utilities']