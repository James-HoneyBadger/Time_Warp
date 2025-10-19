"""
Code Formatter for Time_Warp IDE
Provides language-specific code formatting capabilities
"""

import re
from typing import List, Dict, Optional
from .language_engine import LanguageEngine, BaseLanguageEngine


class CodeFormatter:
    """Main code formatter that works with language engines"""

    def __init__(self, language_engine: LanguageEngine):
        self.language_engine = language_engine

    def format_code(self, text: str, language: str = None) -> str:
        """Format code for the specified or current language"""
        if language:
            original_lang = self.language_engine.current_language
            self.language_engine.set_language(language)
            try:
                result = self._format_with_current_engine(text)
            finally:
                self.language_engine.set_language(original_lang)
            return result
        else:
            return self._format_with_current_engine(text)

    def _format_with_current_engine(self, text: str) -> str:
        """Format code with the current language engine"""
        engine = self.language_engine.get_current_engine()
        if engine:
            return engine.format_code(text)
        return text

    def format_selection(
        self, text: str, start_line: int, end_line: int, language: str = None
    ) -> str:
        """Format a selection of lines"""
        lines = text.split("\n")
        if start_line < 0 or end_line >= len(lines) or start_line > end_line:
            return text

        # Extract the selection
        selection = "\n".join(lines[start_line : end_line + 1])

        # Format the selection
        formatted_selection = self.format_code(selection, language)

        # Replace the selection in the original text
        formatted_lines = formatted_selection.split("\n")
        result_lines = lines[:start_line] + formatted_lines + lines[end_line + 1 :]

        return "\n".join(result_lines)

    def auto_indent(self, text: str, cursor_line: int, language: str = None) -> str:
        """Auto-indent a specific line"""
        if language:
            original_lang = self.language_engine.current_language
            self.language_engine.set_language(language)
            try:
                result = self._auto_indent_with_current_engine(text, cursor_line)
            finally:
                self.language_engine.set_language(original_lang)
            return result
        else:
            return self._auto_indent_with_current_engine(text, cursor_line)

    def _auto_indent_with_current_engine(self, text: str, cursor_line: int) -> str:
        """Auto-indent with current language engine"""
        engine = self.language_engine.get_current_engine()
        if not engine:
            return ""

        return engine.get_indentation(text, cursor_line)

    def smart_tab(self, text: str, cursor_pos: int, language: str = None) -> str:
        """Handle smart tabbing (indentation or completion)"""
        lines = text[:cursor_pos].split("\n")
        current_line = lines[-1] if lines else ""

        # If line is empty or only whitespace, add language-appropriate indentation
        if not current_line.strip():
            indent = self.auto_indent(text, len(lines) - 1, language)
            return indent

        # If at beginning of word, add standard tab
        if cursor_pos > 0 and text[cursor_pos - 1].isspace():
            return "    "  # 4 spaces

        # Otherwise, trigger completion (return empty to let completion system handle)
        return ""

    def format_on_type(
        self, text: str, cursor_pos: int, typed_char: str, language: str = None
    ) -> Optional[str]:
        """Format code as user types (on specific trigger characters)"""
        # Get language-specific trigger characters
        engine = self.language_engine.get_current_engine()
        if not engine:
            return None

        triggers = self._get_format_triggers(engine)

        if typed_char not in triggers:
            return None

        # Handle specific formatting based on typed character
        if typed_char == "\n":
            return self._handle_newline_formatting(text, cursor_pos, engine)
        elif typed_char in ")}]":
            return self._handle_bracket_formatting(text, cursor_pos, typed_char, engine)
        elif typed_char == ":" and engine.config.name.lower() in ["python", "pilot"]:
            return self._handle_colon_formatting(text, cursor_pos, engine)

        return None

    def _get_format_triggers(self, engine: BaseLanguageEngine) -> List[str]:
        """Get format trigger characters for a language"""
        base_triggers = ["\n"]

        if engine.config.name.lower() == "python":
            return base_triggers + [":", ")", "}", "]"]
        elif engine.config.name.lower() == "pilot":
            return base_triggers + [":"]
        elif engine.config.name.lower() in ["basic", "logo"]:
            return base_triggers + [")", "]"]

        return base_triggers

    def _handle_newline_formatting(
        self, text: str, cursor_pos: int, engine: BaseLanguageEngine
    ) -> Optional[str]:
        """Handle formatting when newline is typed"""
        lines = text[:cursor_pos].split("\n")
        if len(lines) < 2:
            return None

        prev_line = lines[-2].rstrip()
        current_line_num = len(lines) - 1

        # Get appropriate indentation for new line
        indent = engine.get_indentation(text, current_line_num)

        # Replace current line with proper indentation
        new_text = text[:cursor_pos] + indent + text[cursor_pos:]
        return new_text

    def _handle_bracket_formatting(
        self, text: str, cursor_pos: int, bracket: str, engine: BaseLanguageEngine
    ) -> Optional[str]:
        """Handle formatting when closing bracket is typed"""
        # For now, just ensure proper alignment
        # More sophisticated bracket matching could be added
        return None

    def _handle_colon_formatting(
        self, text: str, cursor_pos: int, engine: BaseLanguageEngine
    ) -> Optional[str]:
        """Handle formatting when colon is typed (Python, PILOT)"""
        if engine.config.name.lower() == "python":
            # Check if this looks like a function/class/if/for/while definition
            lines = text[:cursor_pos].split("\n")
            current_line = lines[-1] if lines else ""

            keywords = [
                "def ",
                "class ",
                "if ",
                "elif ",
                "else:",
                "for ",
                "while ",
                "try:",
                "except",
                "finally:",
                "with ",
            ]
            if any(current_line.strip().startswith(kw) for kw in keywords):
                # This line will need increased indentation for next line
                return None  # Let the newline handler deal with it

        return None

    def get_formatting_options(self, language: str = None) -> Dict[str, any]:
        """Get formatting options for a language"""
        if language:
            self.language_engine.set_language(language)

        engine = self.language_engine.get_current_engine()
        if not engine:
            return {}

        options = {
            "language": engine.config.name,
            "tab_size": 4,
            "use_spaces": True,
            "auto_indent": True,
            "format_on_type": True,
            "format_on_save": False,
        }

        # Language-specific options
        if engine.config.name.lower() == "python":
            options.update(
                {
                    "max_line_length": 88,
                    "quote_style": "double",
                    "trailing_commas": True,
                }
            )
        elif engine.config.name.lower() == "pilot":
            options.update({"uppercase_commands": True, "space_after_colon": True})
        elif engine.config.name.lower() == "basic":
            options.update({"uppercase_keywords": True, "line_numbers": False})
        elif engine.config.name.lower() == "logo":
            options.update({"uppercase_commands": False, "indent_procedures": True})

        return options

    def apply_formatting_options(self, text: str, options: Dict[str, any]) -> str:
        """Apply specific formatting options to text"""
        result = text

        language = options.get("language", "").lower()

        # Apply tab size and space conversion
        if options.get("use_spaces", True):
            tab_size = options.get("tab_size", 4)
            result = result.replace("\t", " " * tab_size)

        # Language-specific formatting
        if language == "pilot" and options.get("uppercase_commands", True):
            result = self._uppercase_pilot_commands(result)
        elif language == "basic" and options.get("uppercase_keywords", True):
            result = self._uppercase_basic_keywords(result)

        return result

    def _uppercase_pilot_commands(self, text: str) -> str:
        """Convert PILOT commands to uppercase"""
        lines = text.split("\n")
        result = []

        for line in lines:
            if ":" in line and not line.strip().startswith("R:"):
                # This is likely a command line
                parts = line.split(":", 1)
                if len(parts) == 2:
                    command = parts[0].strip().upper()
                    rest = parts[1]
                    line = f"{command}: {rest}"
            result.append(line)

        return "\n".join(result)

    def _uppercase_basic_keywords(self, text: str) -> str:
        """Convert BASIC keywords to uppercase"""
        keywords = [
            "print",
            "input",
            "let",
            "if",
            "then",
            "else",
            "end",
            "for",
            "to",
            "next",
            "while",
            "wend",
            "goto",
            "gosub",
            "return",
            "dim",
            "rem",
            "data",
            "read",
            "restore",
            "on",
            "stop",
            "run",
            "list",
            "save",
            "load",
            "and",
            "or",
            "not",
        ]

        result = text
        for keyword in keywords:
            # Use word boundaries to avoid partial matches
            pattern = r"\b" + re.escape(keyword) + r"\b"
            result = re.sub(pattern, keyword.upper(), result, flags=re.IGNORECASE)

        return result
