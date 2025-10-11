"""
Time_Warp Core Module
===================

Core functionality for the Time_Warp IDE including:
- Main interpreter engine
- Language processing modules
- Core utilities and constants
"""

__version__ = "2.0.0"
__author__ = "Time_Warp Development Team"

from .interpreter import Time_WarpInterpreter
from . import languages
from . import utilities

__all__ = ["Time_WarpInterpreter", "languages", "utilities"]
