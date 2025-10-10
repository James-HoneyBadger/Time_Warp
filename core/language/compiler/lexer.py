"""
Time_Warp IDE Enhanced Lexer
Improved tokenization with better error handling and performance
"""

from typing import List, Optional, Dict, Iterator, NamedTuple
from enum import Enum, auto
from dataclasses import dataclass
import re
import string

from ..errors.error_manager import (
    ErrorManager,
    TimeWarpError,
    TimeWarpLexicalError,
    ErrorCode,
    ErrorSeverity,
    SourceLocation,
)


class TokenType(Enum):
    """Enhanced token types for Time_Warp IDE"""

    # Literals
    NUMBER = auto()
    STRING = auto()
    BOOLEAN = auto()

    # Identifiers and keywords
    IDENTIFIER = auto()
    KEYWORD = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MODULO = auto()
    POWER = auto()

    # Comparison
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS_THAN = auto()
    GREATER_THAN = auto()
    LESS_EQUAL = auto()
    GREATER_EQUAL = auto()

    # Logical
    AND = auto()
    OR = auto()
    NOT = auto()

    # Assignment
    ASSIGN = auto()
    PLUS_ASSIGN = auto()
    MINUS_ASSIGN = auto()

    # Delimiters
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACKET = auto()
    RIGHT_BRACKET = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    COMMA = auto()
    SEMICOLON = auto()
    COLON = auto()
    DOT = auto()

    # Control flow
    IF = auto()
    THEN = auto()
    ELSE = auto()
    ELIF = auto()
    ENDIF = auto()
    FOR = auto()
    WHILE = auto()
    DO = auto()
    LOOP = auto()
    BREAK = auto()
    CONTINUE = auto()
    FUNCTION = auto()
    RETURN = auto()

    # Mode keywords
    MODE = auto()
    BASIC = auto()
    PILOT = auto()
    LOGO = auto()
    PYTHON = auto()

    # Special
    NEWLINE = auto()
    EOF = auto()
    COMMENT = auto()
    WHITESPACE = auto()

    # Error token
    ERROR = auto()


@dataclass
class Token:
    """Enhanced token representation"""

    type: TokenType
    value: str
    location: SourceLocation
    length: int = 0

    def __post_init__(self):
        if self.length == 0:
            self.length = len(self.value)

    def __str__(self) -> str:
        return f"{self.type.name}({self.value!r}) at {self.location}"


class LexerState:
    """Lexer state for better error recovery"""

    def __init__(self, text: str, filename: Optional[str] = None):
        self.text = text
        self.filename = filename
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self.error_manager = ErrorManager()

    def current_char(self) -> Optional[str]:
        """Get current character"""
        return self.text[self.position] if self.position < len(self.text) else None

    def peek_char(self, offset: int = 1) -> Optional[str]:
        """Peek at character with offset"""
        pos = self.position + offset
        return self.text[pos] if pos < len(self.text) else None

    def advance(self) -> Optional[str]:
        """Advance position and return current character"""
        if self.position >= len(self.text):
            return None

        char = self.text[self.position]
        self.position += 1

        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return char

    def current_location(self) -> SourceLocation:
        """Get current source location"""
        return SourceLocation(self.line, self.column, self.filename)

    def add_token(
        self,
        token_type: TokenType,
        value: str,
        start_location: Optional[SourceLocation] = None,
    ):
        """Add token to list"""
        location = start_location or self.current_location()
        token = Token(token_type, value, location)
        self.tokens.append(token)
        return token


class EnhancedLexer:
    """Enhanced lexer with better error handling and performance"""

    # Keywords mapping
    KEYWORDS = {
        # Control flow
        "IF": TokenType.IF,
        "THEN": TokenType.THEN,
        "ELSE": TokenType.ELSE,
        "ELIF": TokenType.ELIF,
        "ENDIF": TokenType.ENDIF,
        "FOR": TokenType.FOR,
        "WHILE": TokenType.WHILE,
        "DO": TokenType.DO,
        "LOOP": TokenType.LOOP,
        "BREAK": TokenType.BREAK,
        "CONTINUE": TokenType.CONTINUE,
        "FUNCTION": TokenType.FUNCTION,
        "RETURN": TokenType.RETURN,
        # Modes
        "MODE": TokenType.MODE,
        "BASIC": TokenType.BASIC,
        "PILOT": TokenType.PILOT,
        "LOGO": TokenType.LOGO,
        "PYTHON": TokenType.PYTHON,
        # Logical operators
        "AND": TokenType.AND,
        "OR": TokenType.OR,
        "NOT": TokenType.NOT,
        "TRUE": TokenType.BOOLEAN,
        "FALSE": TokenType.BOOLEAN,
    }

    # Single character tokens
    SINGLE_CHAR_TOKENS = {
        "+": TokenType.PLUS,
        "-": TokenType.MINUS,
        "*": TokenType.MULTIPLY,
        "/": TokenType.DIVIDE,
        "%": TokenType.MODULO,
        "^": TokenType.POWER,
        "=": TokenType.ASSIGN,
        "(": TokenType.LEFT_PAREN,
        ")": TokenType.RIGHT_PAREN,
        "[": TokenType.LEFT_BRACKET,
        "]": TokenType.RIGHT_BRACKET,
        "{": TokenType.LEFT_BRACE,
        "}": TokenType.RIGHT_BRACE,
        ",": TokenType.COMMA,
        ";": TokenType.SEMICOLON,
        ":": TokenType.COLON,
        ".": TokenType.DOT,
    }

    # Multi-character tokens
    MULTI_CHAR_TOKENS = {
        "==": TokenType.EQUAL,
        "!=": TokenType.NOT_EQUAL,
        "<>": TokenType.NOT_EQUAL,  # BASIC-style
        "<": TokenType.LESS_THAN,
        ">": TokenType.GREATER_THAN,
        "<=": TokenType.LESS_EQUAL,
        ">=": TokenType.GREATER_EQUAL,
        "+=": TokenType.PLUS_ASSIGN,
        "-=": TokenType.MINUS_ASSIGN,
    }

    def __init__(self):
        self.state: Optional[LexerState] = None

    def _ensure_state(self) -> LexerState:
        """Ensure state is not None and return it"""
        if self.state is None:
            raise RuntimeError("Lexer state not initialized")
        return self.state

    def tokenize(self, text: str, filename: Optional[str] = None) -> List[Token]:
        """Tokenize input text"""
        self.state = LexerState(text, filename)

        while self.state.position < len(self.state.text):
            try:
                self._scan_token()
            except Exception as e:
                # Error recovery - skip character and continue
                self.state.error_manager.add_error(
                    ErrorCode.INVALID_CHARACTER,
                    f"Unexpected error during tokenization: {e}",
                    self.state.current_location(),
                )
                self.state.advance()

        # Add EOF token
        self.state.add_token(TokenType.EOF, "", self.state.current_location())

        return self.state.tokens

    def _scan_token(self):
        """Scan next token"""
        if self.state is None:
            return

        char = self.state.current_char()
        if char is None:
            return

        start_location = self.state.current_location()

        # Skip whitespace (except newlines)
        if char in " \t\r":
            self._scan_whitespace()
            return

        # Newlines
        if char == "\n":
            self.state.advance()
            self.state.add_token(TokenType.NEWLINE, "\n", start_location)
            return

        # Comments
        if char == "#" or (
            char == "R"
            and self.state.peek_char() == "E"
            and self.state.peek_char(2) == "M"
        ):
            self._scan_comment()
            return

        # Numbers
        if char.isdigit() or (
            char == "." and self.state.peek_char() and self.state.peek_char().isdigit()
        ):
            self._scan_number()
            return

        # Strings
        if char in "\"'":
            self._scan_string(char)
            return

        # Multi-character operators
        two_char = char + (self.state.peek_char() or "")
        if two_char in self.MULTI_CHAR_TOKENS:
            self.state.advance()
            self.state.advance()
            self.state.add_token(
                self.MULTI_CHAR_TOKENS[two_char], two_char, start_location
            )
            return

        # Single character tokens
        if char in self.SINGLE_CHAR_TOKENS:
            self.state.advance()
            self.state.add_token(self.SINGLE_CHAR_TOKENS[char], char, start_location)
            return

        # Identifiers and keywords
        if char.isalpha() or char == "_":
            self._scan_identifier()
            return

        # Unknown character
        self.state.error_manager.add_error(
            ErrorCode.INVALID_CHARACTER,
            f"Unexpected character '{char}'",
            start_location,
            suggestions=[
                "Remove the invalid character",
                "Check for proper string delimiters",
            ],
        )
        self.state.advance()
        self.state.add_token(TokenType.ERROR, char, start_location)

    def _scan_whitespace(self):
        """Scan whitespace characters"""
        if self.state is None:
            return

        start_pos = self.state.position
        start_location = self.state.current_location()

        while self.state.current_char() and self.state.current_char() in " \t\r":
            self.state.advance()

        # Don't emit whitespace tokens by default
        # self.state.add_token(TokenType.WHITESPACE,
        #                     self.state.text[start_pos:self.state.position],
        #                     start_location)

    def _scan_comment(self):
        """Scan comment"""
        start_pos = self.state.position
        start_location = self.state.current_location()

        # Handle both # style and REM style comments
        if self.state.current_char() == "#":
            self.state.advance()
        else:  # REM style
            self.state.advance()  # R
            self.state.advance()  # E
            self.state.advance()  # M
            if self.state.current_char() == " ":
                self.state.advance()

        # Read until end of line
        while self.state.current_char() and self.state.current_char() != "\n":
            self.state.advance()

        comment_text = self.state.text[start_pos : self.state.position]
        # Don't emit comment tokens by default
        # self.state.add_token(TokenType.COMMENT, comment_text, start_location)

    def _scan_number(self):
        """Scan numeric literal"""
        start_pos = self.state.position
        start_location = self.state.current_location()
        has_dot = False
        has_e = False

        while self.state.current_char():
            char = self.state.current_char()

            if char.isdigit():
                self.state.advance()
            elif char == "." and not has_dot and not has_e:
                has_dot = True
                self.state.advance()
            elif char.lower() == "e" and not has_e:
                has_e = True
                self.state.advance()
                # Handle optional + or - after e
                if self.state.current_char() in "+-":
                    self.state.advance()
            else:
                break

        number_text = self.state.text[start_pos : self.state.position]

        # Validate the number
        try:
            if has_dot or has_e:
                float(number_text)
            else:
                int(number_text)
        except ValueError:
            self.state.error_manager.add_error(
                ErrorCode.INVALID_NUMBER,
                f"Invalid number format: '{number_text}'",
                start_location,
            )
            self.state.add_token(TokenType.ERROR, number_text, start_location)
            return

        self.state.add_token(TokenType.NUMBER, number_text, start_location)

    def _scan_string(self, quote_char: str):
        """Scan string literal"""
        start_pos = self.state.position
        start_location = self.state.current_location()

        self.state.advance()  # Skip opening quote

        value = ""
        while self.state.current_char() and self.state.current_char() != quote_char:
            char = self.state.current_char()

            if char == "\\":
                # Handle escape sequences
                self.state.advance()
                next_char = self.state.current_char()
                if next_char is None:
                    break

                escape_map = {
                    "n": "\n",
                    "t": "\t",
                    "r": "\r",
                    "\\": "\\",
                    "'": "'",
                    '"': '"',
                    "0": "\0",
                }

                if next_char in escape_map:
                    value += escape_map[next_char]
                else:
                    value += next_char

                self.state.advance()
            else:
                value += char
                self.state.advance()

        if self.state.current_char() == quote_char:
            self.state.advance()  # Skip closing quote
        else:
            self.state.error_manager.add_error(
                ErrorCode.UNTERMINATED_STRING,
                "Unterminated string literal",
                start_location,
                suggestions=["Add closing quote", "Check for embedded quotes"],
            )
            self.state.add_token(TokenType.ERROR, value, start_location)
            return

        self.state.add_token(TokenType.STRING, value, start_location)

    def _scan_identifier(self):
        """Scan identifier or keyword"""
        start_pos = self.state.position
        start_location = self.state.current_location()

        while self.state.current_char() and (
            self.state.current_char().isalnum() or self.state.current_char() in "_$"
        ):
            self.state.advance()

        text = self.state.text[start_pos : self.state.position]
        text_upper = text.upper()

        # Check if it's a keyword
        if text_upper in self.KEYWORDS:
            token_type = self.KEYWORDS[text_upper]
            # Special handling for boolean literals
            if token_type == TokenType.BOOLEAN:
                value = text_upper == "TRUE"
                self.state.add_token(TokenType.BOOLEAN, str(value), start_location)
            else:
                self.state.add_token(token_type, text, start_location)
        else:
            self.state.add_token(TokenType.IDENTIFIER, text, start_location)

    def get_errors(self) -> List[TimeWarpError]:
        """Get lexical errors"""
        return self.state.error_manager.get_all_issues() if self.state else []

    def has_errors(self) -> bool:
        """Check if there are lexical errors"""
        return self.state.error_manager.has_errors() if self.state else False
