"""
Language Engine System
Provides language-specific editing features for Time_Warp IDE
"""

import re
import tkinter as tk
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass


@dataclass
class LanguageConfig:
    """Configuration for a specific language"""

    name: str
    extensions: List[str]
    keywords: List[str]
    operators: List[str]
    delimiters: List[str]
    comment_markers: List[str]
    block_comment: Tuple[str, str] = None
    string_quotes: List[str] = None
    escape_char: str = "\\"
    case_sensitive: bool = True
    line_comment: str = None
    supports_compilation: bool = False
    compiler_extensions: List[str] = None
    executable_extensions: List[str] = None


class BaseLanguageEngine(ABC):
    """Base class for language-specific engines"""

    def __init__(self, config: LanguageConfig):
        self.config = config
        self.keywords_pattern = None
        self.setup_patterns()

    def setup_patterns(self):
        """Setup regex patterns for syntax highlighting"""
        if self.config.keywords:
            keywords = "|".join(re.escape(kw) for kw in self.config.keywords)
            flags = 0 if self.config.case_sensitive else re.IGNORECASE
            self.keywords_pattern = re.compile(rf"\b({keywords})\b", flags)

    @abstractmethod
    def get_completions(self, text: str, cursor_pos: int) -> List[str]:
        """Get code completions for current context"""
        pass

    @abstractmethod
    def check_syntax(self, text: str) -> List[Dict[str, Any]]:
        """Check syntax and return errors/warnings"""
        pass

    @abstractmethod
    def format_code(self, text: str) -> str:
        """Format code according to language conventions"""
        pass

    @abstractmethod
    def get_indentation(self, text: str, line_num: int) -> str:
        """Get appropriate indentation for line"""
        pass

    def get_syntax_highlights(self, text: str) -> List[Tuple[str, int, int]]:
        """Get syntax highlighting tags and positions"""
        highlights = []

        # Keywords
        if self.keywords_pattern:
            for match in self.keywords_pattern.finditer(text):
                highlights.append(("keyword", match.start(), match.end()))

        # Comments
        for comment_marker in self.config.comment_markers:
            pattern = re.escape(comment_marker) + r".*$"
            for match in re.finditer(pattern, text, re.MULTILINE):
                highlights.append(("comment", match.start(), match.end()))

        # Strings
        if self.config.string_quotes:
            for quote in self.config.string_quotes:
                pattern = (
                    re.escape(quote)
                    + r"[^"
                    + re.escape(quote)
                    + r"]*"
                    + re.escape(quote)
                )
                for match in re.finditer(pattern, text):
                    highlights.append(("string", match.start(), match.end()))

        return highlights


class PILOTEngine(BaseLanguageEngine):
    """PILOT language engine"""

    def __init__(self):
        config = LanguageConfig(
            name="PILOT",
            extensions=[".pilot"],
            keywords=["T:", "A:", "J:", "Y:", "N:", "U:", "C:", "R:", "M:", "E:"],
            operators=["+", "-", "*", "/", "=", "<", ">", "<=", ">=", "<>"],
            delimiters=["(", ")", "#"],
            comment_markers=["R:"],
            line_comment="R:",
            supports_compilation=True,
            compiler_extensions=["_compiled"],
            executable_extensions=[".exe", ".bin"],
        )
        super().__init__(config)

        # PILOT-specific patterns
        self.label_pattern = re.compile(r"\*[A-Za-z][A-Za-z0-9]*")
        self.variable_pattern = re.compile(r"#[A-Za-z][A-Za-z0-9]*")
        self.command_pattern = re.compile(r"^[TAJYNCURME]:")

    def get_completions(self, text: str, cursor_pos: int) -> List[str]:
        """Get PILOT-specific completions"""
        lines = text[:cursor_pos].split("\n")
        current_line = lines[-1] if lines else ""

        completions = []

        # Command completions
        if not current_line.strip() or current_line.strip()[-1] not in ":":
            completions.extend(
                ["T: ", "A: ", "J: ", "Y: ", "N: ", "U: ", "C: ", "R: ", "M: ", "E: "]
            )

        # Variable completions
        if "#" in current_line:
            # Find all variables in the text
            variables = set(re.findall(r"#[A-Za-z][A-Za-z0-9]*", text))
            completions.extend(list(variables))

        # Label completions for jumps
        if current_line.strip().startswith("J:"):
            labels = set(re.findall(r"\*[A-Za-z][A-Za-z0-9]*", text))
            completions.extend(list(labels))

        return completions

    def check_syntax(self, text: str) -> List[Dict[str, Any]]:
        """Check PILOT syntax"""
        errors = []
        lines = text.split("\n")

        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith("R:"):
                continue

            # Check command format
            if not re.match(r"^[TAJYNCURME]:", line):
                if line.startswith("*"):
                    # Label definition - valid
                    continue
                else:
                    errors.append(
                        {
                            "type": "error",
                            "line": i + 1,
                            "message": f"Invalid PILOT command: {line}",
                        }
                    )

        return errors

    def format_code(self, text: str) -> str:
        """Format PILOT code"""
        lines = text.split("\n")
        formatted = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted.append("")
                continue

            if stripped.startswith("*"):
                # Label - no indentation
                formatted.append(stripped)
            elif any(
                stripped.startswith(cmd)
                for cmd in ["T:", "A:", "J:", "Y:", "N:", "U:", "C:", "R:", "M:", "E:"]
            ):
                # Command - standard format
                formatted.append(stripped)
            else:
                formatted.append(stripped)

        return "\n".join(formatted)

    def get_indentation(self, text: str, line_num: int) -> str:
        """Get PILOT indentation (minimal)"""
        return ""


class BASICEngine(BaseLanguageEngine):
    """BASIC language engine"""

    def __init__(self):
        config = LanguageConfig(
            name="BASIC",
            extensions=[".bas", ".basic"],
            keywords=[
                "PRINT",
                "INPUT",
                "LET",
                "IF",
                "THEN",
                "ELSE",
                "END",
                "FOR",
                "TO",
                "NEXT",
                "WHILE",
                "WEND",
                "GOTO",
                "GOSUB",
                "RETURN",
                "DIM",
                "REM",
                "DATA",
                "READ",
                "RESTORE",
                "ON",
                "STOP",
                "RUN",
                "LIST",
                "SAVE",
                "LOAD",
                "AND",
                "OR",
                "NOT",
            ],
            operators=["+", "-", "*", "/", "^", "=", "<", ">", "<=", ">=", "<>"],
            delimiters=["(", ")", ",", ";", ":"],
            comment_markers=["REM", "'"],
            line_comment="REM",
            supports_compilation=True,
            compiler_extensions=["_compiled"],
            executable_extensions=[".exe", ".bin"],
        )
        super().__init__(config)

        # BASIC-specific patterns
        self.line_number_pattern = re.compile(r"^\s*\d+\s+")
        self.string_pattern = re.compile(r'"[^"]*"')
        self.variable_pattern = re.compile(r"[A-Za-z][A-Za-z0-9]*[$%]?")

    def get_completions(self, text: str, cursor_pos: int) -> List[str]:
        """Get BASIC-specific completions"""
        lines = text[:cursor_pos].split("\n")
        current_line = lines[-1] if lines else ""

        completions = []

        # Keyword completions
        completions.extend(self.config.keywords)

        # Built-in functions
        functions = [
            "ABS(",
            "ASC(",
            "ATN(",
            "CHR$(",
            "COS(",
            "EXP(",
            "INT(",
            "LEFT$(",
            "LEN(",
            "LOG(",
            "MID$(",
            "RIGHT$(",
            "RND(",
            "SGN(",
            "SIN(",
            "SQR(",
            "STR$(",
            "TAN(",
            "VAL(",
        ]
        completions.extend(functions)

        # Variable completions
        variables = set(re.findall(r"[A-Za-z][A-Za-z0-9]*[$%]?", text))
        completions.extend(list(variables))

        return completions

    def check_syntax(self, text: str) -> List[Dict[str, Any]]:
        """Check BASIC syntax"""
        errors = []
        lines = text.split("\n")

        for i, line in enumerate(lines):
            original_line = line
            line = line.strip()
            if not line or line.startswith("REM") or line.startswith("'"):
                continue

            # Check for line numbers (optional in modern BASIC)
            line_number_match = self.line_number_pattern.match(original_line)
            if line_number_match:
                line = line[line_number_match.end() :].strip()

            # Check basic structure
            if line and not any(
                line.upper().startswith(kw) for kw in self.config.keywords
            ):
                # Check if it's an assignment
                if "=" not in line:
                    errors.append(
                        {
                            "type": "warning",
                            "line": i + 1,
                            "message": f"Unrecognized statement: {line}",
                        }
                    )

        return errors

    def format_code(self, text: str) -> str:
        """Format BASIC code"""
        lines = text.split("\n")
        formatted = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted.append("")
                continue

            # Preserve line numbers if present
            line_number_match = self.line_number_pattern.match(line)
            if line_number_match:
                line_num = line_number_match.group().strip()
                rest = line[line_number_match.end() :].strip()
                formatted.append(f"{line_num} {rest}")
            else:
                formatted.append(stripped)

        return "\n".join(formatted)

    def get_indentation(self, text: str, line_num: int) -> str:
        """Get BASIC indentation"""
        # BASIC traditionally doesn't use significant indentation
        return ""


class LogoEngine(BaseLanguageEngine):
    """Logo language engine"""

    def __init__(self):
        config = LanguageConfig(
            name="Logo",
            extensions=[".logo", ".lg"],
            keywords=[
                "FORWARD",
                "FD",
                "BACK",
                "BK",
                "LEFT",
                "LT",
                "RIGHT",
                "RT",
                "PENUP",
                "PU",
                "PENDOWN",
                "PD",
                "HOME",
                "CLEARSCREEN",
                "CS",
                "REPEAT",
                "TO",
                "END",
                "IF",
                "IFELSE",
                "WHILE",
                "FOR",
                "MAKE",
                "SHOW",
                "PRINT",
                "TYPE",
                "READ",
                "READCHAR",
                "READWORD",
                "SETPENCOLOR",
                "SETPENSIZE",
                "HIDETURTLE",
                "HT",
                "SHOWTURTLE",
                "ST",
            ],
            operators=["+", "-", "*", "/", "=", "<", ">", "<=", ">=", "<>"],
            delimiters=["[", "]", "(", ")", ":"],
            comment_markers=[";"],
            line_comment=";",
            supports_compilation=True,
            compiler_extensions=["_compiled"],
            executable_extensions=[".exe", ".bin"],
        )
        super().__init__(config)

        # Logo-specific patterns
        self.procedure_pattern = re.compile(
            r"TO\s+([A-Za-z][A-Za-z0-9]*)", re.IGNORECASE
        )
        self.variable_pattern = re.compile(r":[A-Za-z][A-Za-z0-9]*")

    def get_completions(self, text: str, cursor_pos: int) -> List[str]:
        """Get Logo-specific completions"""
        lines = text[:cursor_pos].split("\n")
        current_line = lines[-1] if lines else ""

        completions = []

        # Keyword completions
        completions.extend(self.config.keywords)

        # Procedure completions
        procedures = set(
            re.findall(r"TO\s+([A-Za-z][A-Za-z0-9]*)", text, re.IGNORECASE)
        )
        completions.extend(list(procedures))

        # Variable completions
        variables = set(re.findall(r":[A-Za-z][A-Za-z0-9]*", text))
        completions.extend(list(variables))

        return completions

    def check_syntax(self, text: str) -> List[Dict[str, Any]]:
        """Check Logo syntax"""
        errors = []
        lines = text.split("\n")
        procedure_stack = []

        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith(";"):
                continue

            # Check procedure definitions
            if line.upper().startswith("TO "):
                procedure_stack.append(i + 1)
            elif line.upper() == "END":
                if not procedure_stack:
                    errors.append(
                        {
                            "type": "error",
                            "line": i + 1,
                            "message": "END without matching TO",
                        }
                    )
                else:
                    procedure_stack.pop()

        # Check for unmatched TOs
        for line_num in procedure_stack:
            errors.append(
                {
                    "type": "error",
                    "line": line_num,
                    "message": "TO without matching END",
                }
            )

        return errors

    def format_code(self, text: str) -> str:
        """Format Logo code"""
        lines = text.split("\n")
        formatted = []
        indent_level = 0

        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted.append("")
                continue

            # Decrease indent for END
            if stripped.upper() == "END":
                indent_level = max(0, indent_level - 1)

            # Add indentation
            formatted.append("  " * indent_level + stripped)

            # Increase indent for TO
            if stripped.upper().startswith("TO "):
                indent_level += 1

        return "\n".join(formatted)

    def get_indentation(self, text: str, line_num: int) -> str:
        """Get Logo indentation"""
        lines = text.split("\n")
        indent_level = 0

        # Count nesting level up to current line
        for i in range(min(line_num, len(lines))):
            line = lines[i].strip().upper()
            if line.startswith("TO "):
                indent_level += 1
            elif line == "END":
                indent_level = max(0, indent_level - 1)

        return "  " * indent_level


class PythonEngine(BaseLanguageEngine):
    """Python language engine"""

    def __init__(self):
        config = LanguageConfig(
            name="Python",
            extensions=[".py", ".pyw"],
            keywords=[
                "and",
                "as",
                "assert",
                "break",
                "class",
                "continue",
                "def",
                "del",
                "elif",
                "else",
                "except",
                "finally",
                "for",
                "from",
                "global",
                "if",
                "import",
                "in",
                "is",
                "lambda",
                "nonlocal",
                "not",
                "or",
                "pass",
                "raise",
                "return",
                "try",
                "while",
                "with",
                "yield",
                "True",
                "False",
                "None",
            ],
            operators=[
                "+",
                "-",
                "*",
                "/",
                "//",
                "%",
                "**",
                "=",
                "==",
                "!=",
                "<",
                ">",
                "<=",
                ">=",
            ],
            delimiters=["(", ")", "[", "]", "{", "}", ",", ":", ";"],
            comment_markers=["#"],
            line_comment="#",
            string_quotes=['"', "'"],
            block_comment=('"""', '"""'),
            supports_compilation=False,  # Python is interpreted
        )
        super().__init__(config)

        # Python-specific patterns
        self.function_pattern = re.compile(
            r"def\s+([A-Za-z_][A-Za-z0-9_]*)", re.IGNORECASE
        )
        self.class_pattern = re.compile(
            r"class\s+([A-Za-z_][A-Za-z0-9_]*)", re.IGNORECASE
        )

    def get_completions(self, text: str, cursor_pos: int) -> List[str]:
        """Get Python-specific completions"""
        lines = text[:cursor_pos].split("\n")
        current_line = lines[-1] if lines else ""

        completions = []

        # Keyword completions
        completions.extend(self.config.keywords)

        # Built-in functions
        builtins = [
            "abs",
            "all",
            "any",
            "bin",
            "bool",
            "chr",
            "dict",
            "dir",
            "enumerate",
            "eval",
            "exec",
            "filter",
            "float",
            "format",
            "frozenset",
            "getattr",
            "globals",
            "hasattr",
            "hash",
            "help",
            "hex",
            "id",
            "input",
            "int",
            "isinstance",
            "issubclass",
            "iter",
            "len",
            "list",
            "locals",
            "map",
            "max",
            "min",
            "next",
            "object",
            "oct",
            "open",
            "ord",
            "pow",
            "print",
            "range",
            "repr",
            "reversed",
            "round",
            "set",
            "setattr",
            "slice",
            "sorted",
            "str",
            "sum",
            "super",
            "tuple",
            "type",
            "vars",
            "zip",
        ]
        completions.extend(builtins)

        # Functions and classes defined in the text
        functions = set(
            re.findall(r"def\s+([A-Za-z_][A-Za-z0-9_]*)", text, re.IGNORECASE)
        )
        classes = set(
            re.findall(r"class\s+([A-Za-z_][A-Za-z0-9_]*)", text, re.IGNORECASE)
        )
        completions.extend(list(functions))
        completions.extend(list(classes))

        return completions

    def check_syntax(self, text: str) -> List[Dict[str, Any]]:
        """Check Python syntax"""
        errors = []

        try:
            compile(text, "<string>", "exec")
        except SyntaxError as e:
            errors.append(
                {"type": "error", "line": e.lineno or 1, "message": str(e.msg)}
            )
        except Exception as e:
            errors.append(
                {"type": "error", "line": 1, "message": f"Python error: {str(e)}"}
            )

        return errors

    def format_code(self, text: str) -> str:
        """Format Python code (basic)"""
        try:
            import ast

            # Parse and reformat (basic implementation)
            tree = ast.parse(text)
            # For now, just return original text
            # A full implementation would use a library like 'black'
            return text
        except:
            return text

    def get_indentation(self, text: str, line_num: int) -> str:
        """Get Python indentation"""
        lines = text.split("\n")
        if line_num <= 0 or line_num > len(lines):
            return ""

        # Look at previous non-empty line
        for i in range(line_num - 1, -1, -1):
            prev_line = lines[i].rstrip()
            if prev_line:
                # Count current indentation
                indent = len(prev_line) - len(prev_line.lstrip())

                # If line ends with :, increase indentation
                if prev_line.endswith(":"):
                    return " " * (indent + 4)
                else:
                    return " " * indent

        return ""


class LanguageEngine:
    """Main language engine that manages all language-specific engines"""

    def __init__(self):
        self.engines = {
            "pilot": PILOTEngine(),
            "basic": BASICEngine(),
            "logo": LogoEngine(),
            "python": PythonEngine(),
        }
        self.current_language = "pilot"

    def set_language(self, language: str):
        """Set the current language"""
        if language.lower() in self.engines:
            self.current_language = language.lower()
            return True
        return False

    def get_current_engine(self) -> BaseLanguageEngine:
        """Get the current language engine"""
        return self.engines.get(self.current_language)

    def get_completions(self, text: str, cursor_pos: int) -> List[str]:
        """Get completions for current language"""
        engine = self.get_current_engine()
        return engine.get_completions(text, cursor_pos) if engine else []

    def check_syntax(self, text: str) -> List[Dict[str, Any]]:
        """Check syntax for current language"""
        engine = self.get_current_engine()
        return engine.check_syntax(text) if engine else []

    def format_code(self, text: str) -> str:
        """Format code for current language"""
        engine = self.get_current_engine()
        return engine.format_code(text) if engine else text

    def get_indentation(self, text: str, line_num: int) -> str:
        """Get indentation for current language"""
        engine = self.get_current_engine()
        return engine.get_indentation(text, line_num) if engine else ""

    def get_syntax_highlights(self, text: str) -> List[Tuple[str, int, int]]:
        """Get syntax highlights for current language"""
        engine = self.get_current_engine()
        return engine.get_syntax_highlights(text) if engine else []

    def get_language_info(self) -> Optional[LanguageConfig]:
        """Get current language configuration"""
        engine = self.get_current_engine()
        return engine.config if engine else None

    def supports_compilation(self) -> bool:
        """Check if current language supports compilation"""
        engine = self.get_current_engine()
        return engine.config.supports_compilation if engine else False
