
"""
TW BASIC Unified Language Support Module
=======================================

This package contains the unified executor class for TW BASIC, which combines
the features of BASIC, PILOT, and Logo into a single educational language.

Language Executor:
- TwBasicExecutor: Handles all TW BASIC commands, including classic BASIC, PILOT-style, and Logo-style turtle graphics.

Each executor follows a consistent interface:
- __init__(interpreter): Initialize with reference to main interpreter
- execute_command(command): Execute a single command and return result

The executor integrates with the Time_WarpInterpreter for shared functionality
like variable management, turtle graphics, and output handling.
"""

from .basic import TwBasicInterpreter
from .pascal import TwPascalInterpreter
from .prolog import TwPrologInterpreter

__all__ = [
    "TwBasicInterpreter",
    "TwPascalInterpreter",
    "TwPrologInterpreter",
]
