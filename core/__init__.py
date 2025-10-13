"""
Time_Warp Core Module
=====================

Core functionality for the Time_Warp IDE, providing the main interpreter engine
and language execution capabilities.

This module serves as the central hub for:
- Time_WarpInterpreter: Main execution engine for all supported languages
- Language executors: Individual language implementations (PILOT, BASIC, Logo, etc.)
- Utility functions: Helper classes and shared functionality

The core module is designed to be lightweight and focused on program execution,
with all GUI components handled by the main Time_Warp.py application.

Supported Languages:
- TW PILOT: Educational language with turtle graphics
- TW BASIC: Classic line-numbered programming
- TW Logo: Turtle graphics programming
- TW Pascal: Structured programming
- TW Prolog: Logic programming
- TW Forth: Stack-based programming
- Perl: Modern scripting
- Python: Full Python execution
- JavaScript: JavaScript execution

Usage:
    from core.interpreter import Time_WarpInterpreter
    interpreter = Time_WarpInterpreter()
    interpreter.run_program("T:Hello World!")
"""

__version__ = "1.3.0"
__author__ = "Time_Warp Development Team"

from .interpreter import Time_WarpInterpreter
from . import languages
from . import utilities

__all__ = ["Time_WarpInterpreter", "languages", "utilities"]
