"""
JAMES IDE Errors Module
"""

from .error_manager import (
    ErrorSeverity, ErrorCode, SourceLocation, JAMESError, ErrorManager,
    JAMESBaseException, JAMESLexicalError, JAMESSyntaxError, 
    JAMESRuntimeError, JAMESTypeError, JAMESNameError,
    create_syntax_error, create_runtime_error, create_type_error
)

__all__ = [
    'ErrorSeverity', 'ErrorCode', 'SourceLocation', 'JAMESError', 'ErrorManager',
    'JAMESBaseException', 'JAMESLexicalError', 'JAMESSyntaxError', 
    'JAMESRuntimeError', 'JAMESTypeError', 'JAMESNameError',
    'create_syntax_error', 'create_runtime_error', 'create_type_error'
]