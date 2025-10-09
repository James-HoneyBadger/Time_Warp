"""
JAMES IDE Language Module
Unified programming language combining PILOT, BASIC, Logo, and Python
"""

from .lexer import JAMESLexer, Token, TokenType
from .parser import JAMESParser, ProgramNode
from .interpreter import JAMESInterpreter
from .james_compiler import JAMESCompiler

__all__ = [
    'JAMESLexer', 'Token', 'TokenType',
    'JAMESParser', 'ProgramNode', 
    'JAMESInterpreter',
    'JAMESCompiler'
]

__version__ = "1.0.0"