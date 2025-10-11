"""
Time_Warp IDE Error Handling System
Centralized error management for better debugging and user experience
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    FATAL = "fatal"


class ErrorCode(Enum):
    """Standardized error codes"""

    # Lexical errors
    INVALID_CHARACTER = "E0001"
    UNTERMINATED_STRING = "E0002"
    INVALID_NUMBER = "E0003"

    # Syntax errors
    UNEXPECTED_TOKEN = "E1001"
    MISSING_TOKEN = "E1002"
    INVALID_SYNTAX = "E1003"
    UNMATCHED_PARENTHESES = "E1004"

    # Runtime errors
    UNDEFINED_VARIABLE = "E2001"
    TYPE_MISMATCH = "E2002"
    DIVISION_BY_ZERO = "E2003"
    INDEX_OUT_OF_BOUNDS = "E2004"
    FUNCTION_NOT_FOUND = "E2005"
    INVALID_ARGUMENT_COUNT = "E2006"

    # Mode-specific errors
    PILOT_PATTERN_ERROR = "E3001"
    LOGO_GRAPHICS_ERROR = "E3002"
    PYTHON_EXECUTION_ERROR = "E3003"

    # System errors
    FILE_NOT_FOUND = "E4001"
    PERMISSION_DENIED = "E4002"
    OUT_OF_MEMORY = "E4003"


@dataclass
class SourceLocation:
    """Represents a location in source code"""

    line: int
    column: int
    filename: Optional[str] = None

    def __str__(self) -> str:
        location = f"line {self.line}, column {self.column}"
        if self.filename:
            location = f"{self.filename}:{location}"
        return location


@dataclass
class TimeWarpError:
    """Structured error information"""

    code: ErrorCode
    severity: ErrorSeverity
    message: str
    location: Optional[SourceLocation] = None
    context: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None

    def __str__(self) -> str:
        parts = [f"[{self.code.value}] {self.severity.value.upper()}: {self.message}"]

        if self.location:
            parts.append(f"  at {self.location}")

        if self.suggestions:
            parts.append("  Suggestions:")
            for suggestion in self.suggestions:
                parts.append(f"    - {suggestion}")

        return "\n".join(parts)


class ErrorManager:
    """Centralized error management"""

    def __init__(self):
        self.errors: List[TimeWarpError] = []
        self.warnings: List[TimeWarpError] = []

    def add_error(
        self,
        code: ErrorCode,
        message: str,
        location: Optional[SourceLocation] = None,
        context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
    ) -> TimeWarpError:
        """Add an error"""
        error = TimeWarpError(
            code=code,
            severity=ErrorSeverity.ERROR,
            message=message,
            location=location,
            context=context,
            suggestions=suggestions,
        )
        self.errors.append(error)
        return error

    def add_warning(
        self,
        code: ErrorCode,
        message: str,
        location: Optional[SourceLocation] = None,
        context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
    ) -> TimeWarpError:
        """Add a warning"""
        warning = TimeWarpError(
            code=code,
            severity=ErrorSeverity.WARNING,
            message=message,
            location=location,
            context=context,
            suggestions=suggestions,
        )
        self.warnings.append(warning)
        return warning

    def has_errors(self) -> bool:
        """Check if there are any errors"""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Check if there are any warnings"""
        return len(self.warnings) > 0

    def get_all_issues(self) -> List[TimeWarpError]:
        """Get all errors and warnings"""
        return self.errors + self.warnings

    def clear(self):
        """Clear all errors and warnings"""
        self.errors.clear()
        self.warnings.clear()

    def format_errors(self) -> str:
        """Format all errors for display"""
        if not self.errors:
            return ""

        lines = ["Errors:"]
        for error in self.errors:
            lines.append(str(error))

        return "\n".join(lines)

    def format_warnings(self) -> str:
        """Format all warnings for display"""
        if not self.warnings:
            return ""

        lines = ["Warnings:"]
        for warning in self.warnings:
            lines.append(str(warning))

        return "\n".join(lines)


# Exception classes for different error types
class TimeWarpBaseException(Exception):
    """Base exception for all Time_Warp errors"""

    def __init__(self, error: TimeWarpError):
        self.error = error
        super().__init__(str(error))


class TimeWarpLexicalError(TimeWarpBaseException):
    """Lexical analysis error"""

    pass


class TimeWarpSyntaxError(TimeWarpBaseException):
    """Syntax parsing error"""

    pass


class TimeWarpRuntimeError(TimeWarpBaseException):
    """Runtime execution error"""

    pass


class TimeWarpTypeError(TimeWarpRuntimeError):
    """Type-related runtime error"""

    pass


class TimeWarpNameError(TimeWarpRuntimeError):
    """Name/variable-related runtime error"""

    pass


# Utility functions for common error scenarios
def create_syntax_error(
    message: str, location: SourceLocation, suggestions: Optional[List[str]] = None
) -> TimeWarpSyntaxError:
    """Create a syntax error with location"""
    error = TimeWarpError(
        code=ErrorCode.INVALID_SYNTAX,
        severity=ErrorSeverity.ERROR,
        message=message,
        location=location,
        suggestions=suggestions,
    )
    return TimeWarpSyntaxError(error)


def create_runtime_error(
    message: str,
    location: Optional[SourceLocation] = None,
    suggestions: Optional[List[str]] = None,
) -> TimeWarpError:
    """Create a runtime error"""
    return TimeWarpError(
        code=ErrorCode.UNDEFINED_VARIABLE,  # Default, should be overridden
        severity=ErrorSeverity.ERROR,
        message=message,
        location=location,
        suggestions=suggestions,
    )


def create_type_error(
    expected: str, actual: str, location: Optional[SourceLocation] = None
) -> TimeWarpTypeError:
    """Create a type mismatch error"""
    error = TimeWarpError(
        code=ErrorCode.TYPE_MISMATCH,
        severity=ErrorSeverity.ERROR,
        message=f"Expected {expected}, got {actual}",
        location=location,
        suggestions=[
            f"Convert the value to {expected}",
            "Check your variable assignments",
        ],
    )
    return TimeWarpTypeError(error)
