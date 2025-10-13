"""
Time_Warp Language Support Modules
==================================

This package contains executor classes for all supported programming languages
in the Time_Warp IDE. Each language has its own executor that handles parsing,
execution, and integration with the main interpreter.

Language Executors:
- TwPilotExecutor: Handles TW PILOT commands (T:, A:, J:, Y:, N:, etc.)
- TwBasicExecutor: Handles TW BASIC statements (PRINT, LET, GOTO, etc.)
- TwLogoExecutor: Handles TW Logo commands (FORWARD, RIGHT, REPEAT, etc.)
- TwPascalExecutor: Handles TW Pascal structured programming
- TwPrologExecutor: Handles TW Prolog logic programming
- TwForthExecutor: Handles TW Forth stack-based operations
- PerlExecutor: Handles Perl script execution
- PythonExecutor: Handles Python script execution
- JavaScriptExecutor: Handles JavaScript execution

Each executor follows a consistent interface:
- __init__(interpreter): Initialize with reference to main interpreter
- execute_command(command): Execute a single command and return result

The executors integrate with the Time_WarpInterpreter for shared functionality
like variable management, turtle graphics, and output handling.
"""

from .pilot import TwPilotExecutor
from .basic import TwBasicExecutor
from .logo import TwLogoExecutor
from .pascal import TwPascalExecutor
from .prolog import TwPrologExecutor
from .forth import TwForthExecutor
from .perl import PerlExecutor
from .python_executor import PythonExecutor
from .javascript_executor import JavaScriptExecutor

__all__ = [
    "TwPilotExecutor",
    "TwBasicExecutor",
    "TwLogoExecutor",
    "TwPascalExecutor",
    "TwPrologExecutor",
    "TwForthExecutor",
    "PerlExecutor",
    "PythonExecutor",
    "JavaScriptExecutor",
]
