"""
Time_Warp IDE Language Lexer
Tokenizes Time_Warp IDE source code for parsing
"""

import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Union


class TokenType(Enum):
    # Literals
    NUMBER = "NUMBER"
    STRING = "STRING"
    IDENTIFIER = "IDENTIFIER"

    # BASIC Keywords
    LET = "LET"
    PRINT = "PRINT"
    INPUT = "INPUT"
    IF = "IF"
    THEN = "THEN"
    ELSE = "ELSE"
    ELIF = "ELIF"
    ENDIF = "ENDIF"
    FOR = "FOR"
    TO = "TO"
    STEP = "STEP"
    NEXT = "NEXT"
    WHILE = "WHILE"
    WEND = "WEND"
    GOSUB = "GOSUB"
    RETURN = "RETURN"
    END = "END"
    DIM = "DIM"
    DEF = "DEF"
    END_DEF = "END_DEF"
    DATA = "DATA"
    READ = "READ"
    RESTORE = "RESTORE"

    # PILOT Keywords
    PILOT = "PILOT"
    T_COLON = "T:"
    A_COLON = "A:"
    M_COLON = "M:"
    J_COLON = "J:"
    C_COLON = "C:"
    U_COLON = "U:"
    R_COLON = "R:"
    E_COLON = "E:"

    # Logo Keywords
    LOGO = "LOGO"
    FORWARD = "FORWARD"
    FD = "FD"
    BACK = "BACK"
    BK = "BK"
    LEFT = "LEFT"
    LT = "LT"
    RIGHT = "RIGHT"
    RT = "RT"
    PENUP = "PENUP"
    PU = "PU"
    PENDOWN = "PENDOWN"
    PD = "PD"
    SETCOLOR = "SETCOLOR"
    REPEAT = "REPEAT"
    HOME = "HOME"
    CLEARSCREEN = "CLEARSCREEN"
    CS = "CS"

    # Python Integration
    PYTHON = "PYTHON"
    END_PYTHON = "END_PYTHON"

    # Mode Control
    MODE = "MODE"
    BASIC = "BASIC"

    # Error Handling
    TRY = "TRY"
    CATCH = "CATCH"
    FINALLY = "FINALLY"
    END_TRY = "END_TRY"

    # Operators
    PLUS = "+"
    MINUS = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    POWER = "^"
    EQUALS = "="
    NOT_EQUALS = "<>"
    LESS_THAN = "<"
    GREATER_THAN = ">"
    LESS_EQUAL = "<="
    GREATER_EQUAL = ">="
    AND = "AND"
    OR = "OR"
    NOT = "NOT"

    # Delimiters
    LPAREN = "("
    RPAREN = ")"
    COMMA = ","
    SEMICOLON = ";"
    COLON = ":"
    HASH = "#"
    DOLLAR = "$"

    # Special
    NEWLINE = "NEWLINE"
    EOF = "EOF"
    COMMENT = "COMMENT"
    LINE_NUMBER = "LINE_NUMBER"


@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int


class TimeWarpLexer:
    """Lexical analyzer for Time_Warp IDE language"""

    def __init__(self):
        self.keywords = {
            # BASIC keywords
            "LET": TokenType.LET,
            "PRINT": TokenType.PRINT,
            "INPUT": TokenType.INPUT,
            "IF": TokenType.IF,
            "THEN": TokenType.THEN,
            "ELSE": TokenType.ELSE,
            "ELIF": TokenType.ELIF,
            "ENDIF": TokenType.ENDIF,
            "FOR": TokenType.FOR,
            "TO": TokenType.TO,
            "STEP": TokenType.STEP,
            "NEXT": TokenType.NEXT,
            "WHILE": TokenType.WHILE,
            "WEND": TokenType.WEND,
            "GOSUB": TokenType.GOSUB,
            "RETURN": TokenType.RETURN,
            "END": TokenType.END,
            "DIM": TokenType.DIM,
            "DEF": TokenType.DEF,
            "END_DEF": TokenType.END_DEF,
            "DATA": TokenType.DATA,
            "READ": TokenType.READ,
            "RESTORE": TokenType.RESTORE,
            # Mode keywords
            "PILOT": TokenType.PILOT,
            "LOGO": TokenType.LOGO,
            "PYTHON": TokenType.PYTHON,
            "END_PYTHON": TokenType.END_PYTHON,
            "MODE": TokenType.MODE,
            "BASIC": TokenType.BASIC,
            # Logo keywords
            "FORWARD": TokenType.FORWARD,
            "FD": TokenType.FD,
            "BACK": TokenType.BACK,
            "BK": TokenType.BK,
            "LEFT": TokenType.LEFT,
            "LT": TokenType.LT,
            "RIGHT": TokenType.RIGHT,
            "RT": TokenType.RT,
            "PENUP": TokenType.PENUP,
            "PU": TokenType.PU,
            "PENDOWN": TokenType.PENDOWN,
            "PD": TokenType.PD,
            "SETCOLOR": TokenType.SETCOLOR,
            "REPEAT": TokenType.REPEAT,
            "HOME": TokenType.HOME,
            "CLEARSCREEN": TokenType.CLEARSCREEN,
            "CS": TokenType.CS,
            # Error handling
            "TRY": TokenType.TRY,
            "CATCH": TokenType.CATCH,
            "FINALLY": TokenType.FINALLY,
            "END_TRY": TokenType.END_TRY,
            # Logical operators
            "AND": TokenType.AND,
            "OR": TokenType.OR,
            "NOT": TokenType.NOT,
        }

        self.pilot_commands = {
            "T:": TokenType.T_COLON,
            "A:": TokenType.A_COLON,
            "M:": TokenType.M_COLON,
            "J:": TokenType.J_COLON,
            "C:": TokenType.C_COLON,
            "U:": TokenType.U_COLON,
            "R:": TokenType.R_COLON,
            "E:": TokenType.E_COLON,
        }

    def tokenize(self, source_code: str) -> List[Token]:
        """Tokenize Time_Warp IDE source code"""
        tokens = []
        lines = source_code.split("\n")

        for line_num, line in enumerate(lines, 1):
            tokens.extend(self._tokenize_line(line, line_num))
            tokens.append(Token(TokenType.NEWLINE, "\\n", line_num, len(line)))

        tokens.append(Token(TokenType.EOF, "", len(lines), 0))
        return tokens

    def _tokenize_line(self, line: str, line_num: int) -> List[Token]:
        """Tokenize a single line"""
        tokens = []
        i = 0

        while i < len(line):
            # Skip whitespace
            if line[i].isspace():
                i += 1
                continue

            # Comments
            if line[i : i + 3] == "REM" or line[i] == "'" or line[i : i + 2] == "//":
                comment_start = i
                if line[i : i + 3] == "REM":
                    i += 3
                elif line[i : i + 2] == "//":
                    i += 2
                else:
                    i += 1
                tokens.append(
                    Token(
                        TokenType.COMMENT, line[comment_start:], line_num, comment_start
                    )
                )
                break

            # Multi-line comments
            if line[i : i + 2] == "/*":
                # Handle multi-line comment start (simplified for now)
                tokens.append(Token(TokenType.COMMENT, line[i:], line_num, i))
                break

            # Line numbers
            if i == 0 and line[i].isdigit():
                num_start = i
                while i < len(line) and line[i].isdigit():
                    i += 1
                tokens.append(
                    Token(TokenType.LINE_NUMBER, line[num_start:i], line_num, num_start)
                )
                continue

            # Numbers
            if line[i].isdigit() or (
                line[i] == "." and i + 1 < len(line) and line[i + 1].isdigit()
            ):
                num_start = i
                has_dot = False
                while i < len(line) and (
                    line[i].isdigit() or (line[i] == "." and not has_dot)
                ):
                    if line[i] == ".":
                        has_dot = True
                    i += 1
                tokens.append(
                    Token(TokenType.NUMBER, line[num_start:i], line_num, num_start)
                )
                continue

            # Strings
            if line[i] == '"':
                str_start = i
                i += 1
                while i < len(line) and line[i] != '"':
                    if line[i] == "\\" and i + 1 < len(line):
                        i += 2  # Skip escaped character
                    else:
                        i += 1
                if i < len(line):
                    i += 1  # Skip closing quote
                tokens.append(
                    Token(TokenType.STRING, line[str_start:i], line_num, str_start)
                )
                continue

            # Two-character operators
            if i + 1 < len(line):
                two_char = line[i : i + 2]
                if two_char == "<>":
                    tokens.append(Token(TokenType.NOT_EQUALS, two_char, line_num, i))
                    i += 2
                    continue
                elif two_char == "<=":
                    tokens.append(Token(TokenType.LESS_EQUAL, two_char, line_num, i))
                    i += 2
                    continue
                elif two_char == ">=":
                    tokens.append(Token(TokenType.GREATER_EQUAL, two_char, line_num, i))
                    i += 2
                    continue

            # Single-character operators and delimiters
            single_chars = {
                "+": TokenType.PLUS,
                "-": TokenType.MINUS,
                "*": TokenType.MULTIPLY,
                "/": TokenType.DIVIDE,
                "^": TokenType.POWER,
                "=": TokenType.EQUALS,
                "<": TokenType.LESS_THAN,
                ">": TokenType.GREATER_THAN,
                "(": TokenType.LPAREN,
                ")": TokenType.RPAREN,
                ",": TokenType.COMMA,
                ";": TokenType.SEMICOLON,
                ":": TokenType.COLON,
                "#": TokenType.HASH,
                "$": TokenType.DOLLAR,
            }

            if line[i] in single_chars:
                tokens.append(Token(single_chars[line[i]], line[i], line_num, i))
                i += 1
                continue

            # Identifiers and keywords
            if line[i].isalpha() or line[i] == "_":
                id_start = i
                while i < len(line) and (
                    line[i].isalnum() or line[i] == "_" or line[i] == "$"
                ):
                    i += 1

                identifier = line[id_start:i].upper()

                # Check for PILOT commands
                if (
                    i < len(line)
                    and line[i] == ":"
                    and identifier in ["T", "A", "M", "J", "C", "U", "R", "E"]
                ):
                    pilot_cmd = identifier + ":"
                    if pilot_cmd in self.pilot_commands:
                        tokens.append(
                            Token(
                                self.pilot_commands[pilot_cmd],
                                pilot_cmd,
                                line_num,
                                id_start,
                            )
                        )
                        i += 1
                        continue

                # Check for keywords
                if identifier in self.keywords:
                    tokens.append(
                        Token(self.keywords[identifier], identifier, line_num, id_start)
                    )
                else:
                    tokens.append(
                        Token(
                            TokenType.IDENTIFIER, line[id_start:i], line_num, id_start
                        )
                    )
                continue

            # Unknown character
            tokens.append(Token(TokenType.IDENTIFIER, line[i], line_num, i))
            i += 1

        return tokens
