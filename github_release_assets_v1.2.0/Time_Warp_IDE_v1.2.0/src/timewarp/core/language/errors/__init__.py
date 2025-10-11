"""
Time_Warp IDE Errors Module
"""

from .error_manager import (
    ErrorSeverity,
    ErrorCode,
    SourceLocation,
    TimeWarpError,
    ErrorManager,
    TimeWarpBaseException,
    TimeWarpLexicalError,
    TimeWarpSyntaxError,
    TimeWarpRuntimeError,
    TimeWarpTypeError,
    TimeWarpNameError,
    create_syntax_error,
    create_runtime_error,
    create_type_error,
)

__all__ = [
    "ErrorSeverity",
    "ErrorCode",
    "SourceLocation",
    "TimeWarpError",
    "ErrorManager",
    "TimeWarpBaseException",
    "TimeWarpLexicalError",
    "TimeWarpSyntaxError",
    "TimeWarpRuntimeError",
    "TimeWarpTypeError",
    "TimeWarpNameError",
    "create_syntax_error",
    "create_runtime_error",
    "create_type_error",
]
