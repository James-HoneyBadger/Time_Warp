#!/usr/bin/env python3
"""
Enhanced Code Completion Engine for Time_Warp IDE
Provides intelligent code completion for all supported languages
"""

import re
import ast
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass


@dataclass
class CompletionItem:
    """Represents a single code completion suggestion"""

    text: str
    kind: str  # 'keyword', 'function', 'variable', 'constant'
    description: str
    insert_text: Optional[str] = None
    detail: Optional[str] = None
    score: float = 1.0


class CodeCompletionEngine:
    """
    Advanced code completion engine with multi-language support
    """

    def __init__(self):
        self.language_keywords = {
            "pilot": [
                "T:",
                "A:",
                "J:",
                "Y:",
                "N:",
                "R:",
                "E:",
                "U:",
                "D:",
                "C:",
                "M:",
                "FORWARD",
                "BACK",
                "LEFT",
                "RIGHT",
                "PENUP",
                "PENDOWN",
                "SETCOLOR",
                "FILL",
                "CIRCLE",
                "SQUARE",
                "TRIANGLE",
            ],
            "basic": [
                "PRINT",
                "LET",
                "INPUT",
                "IF",
                "THEN",
                "ELSE",
                "END",
                "FOR",
                "TO",
                "STEP",
                "NEXT",
                "WHILE",
                "WEND",
                "GOTO",
                "GOSUB",
                "RETURN",
                "DATA",
                "READ",
                "RESTORE",
                "DIM",
                "REM",
                "STOP",
                "RUN",
                "LIST",
                "NEW",
            ],
            "logo": [
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
                "SETPENCOLOR",
                "SETPENSIZE",
                "HOME",
                "CLEARSCREEN",
                "CS",
                "REPEAT",
                "TO",
                "END",
                "IF",
                "IFELSE",
                "MAKE",
                "THING",
                "WORD",
                "SENTENCE",
            ],
            "python": [
                "def",
                "class",
                "if",
                "elif",
                "else",
                "for",
                "while",
                "try",
                "except",
                "finally",
                "with",
                "as",
                "import",
                "from",
                "return",
                "yield",
                "break",
                "continue",
                "pass",
                "lambda",
                "and",
                "or",
                "not",
                "in",
                "is",
                "True",
                "False",
                "None",
            ],
            "javascript": [
                "function",
                "var",
                "let",
                "const",
                "if",
                "else",
                "for",
                "while",
                "do",
                "switch",
                "case",
                "default",
                "break",
                "continue",
                "return",
                "try",
                "catch",
                "finally",
                "throw",
                "new",
                "this",
                "super",
                "class",
                "extends",
                "async",
                "await",
            ],
        }

        self.language_functions = {
            "pilot": {
                "T:": "Move turtle forward by specified distance",
                "A:": "Turn turtle left by specified angle",
                "J:": "Jump to absolute position without drawing",
                "Y:": "Check if condition is true",
                "N:": "Check if condition is false",
                "R:": "Add comment or remark",
                "E:": "End program or procedure",
                "U:": "Pen up - stop drawing",
                "D:": "Pen down - start drawing",
                "C:": "Change pen color",
                "M:": "Move to position",
            },
            "basic": {
                "PRINT": "Display text or variables",
                "INPUT": "Get user input",
                "LET": "Assign value to variable",
                "IF": "Conditional statement",
                "FOR": "Loop with counter",
                "WHILE": "Loop while condition is true",
                "GOTO": "Jump to line number",
                "GOSUB": "Call subroutine",
                "DIM": "Declare array",
            },
            "logo": {
                "FORWARD": "Move turtle forward",
                "BACK": "Move turtle backward",
                "LEFT": "Turn turtle left",
                "RIGHT": "Turn turtle right",
                "PENUP": "Lift pen up",
                "PENDOWN": "Put pen down",
                "REPEAT": "Repeat commands",
                "TO": "Define procedure",
                "HOME": "Return turtle to center",
            },
        }

        self.context_cache = {}

    def get_completions(
        self,
        language: str,
        text: str,
        position: int,
        line_text: str = "",
        cursor_column: int = 0,
    ) -> List[CompletionItem]:
        """
        Get code completion suggestions for given context

        Args:
            language: Programming language ('pilot', 'basic', 'logo', etc.)
            text: Full text content
            position: Cursor position in full text
            line_text: Current line text
            cursor_column: Column position in current line

        Returns:
            List of completion suggestions
        """
        try:
            completions = []

            # Get word being typed
            current_word = self._get_current_word(line_text, cursor_column)

            # Add keyword completions
            completions.extend(self._get_keyword_completions(language, current_word))

            # Add function completions
            completions.extend(self._get_function_completions(language, current_word))

            # Add variable completions
            completions.extend(
                self._get_variable_completions(text, current_word, language)
            )

            # Add context-specific completions
            completions.extend(
                self._get_context_completions(language, line_text, current_word)
            )

            # Sort by relevance score
            completions.sort(key=lambda x: x.score, reverse=True)

            return completions[:20]  # Limit to top 20 suggestions

        except Exception as e:
            print(f"Error in code completion: {e}")
            return []

    def _get_current_word(self, line_text: str, cursor_column: int) -> str:
        """Extract the word being typed at cursor position"""
        if not line_text or cursor_column <= 0:
            return ""

        # Find word boundaries
        start = cursor_column - 1
        while start > 0 and line_text[start - 1].isalnum():
            start -= 1

        end = cursor_column
        while end < len(line_text) and line_text[end].isalnum():
            end += 1

        return line_text[start:cursor_column]

    def _get_keyword_completions(
        self, language: str, current_word: str
    ) -> List[CompletionItem]:
        """Get keyword completions for the language"""
        completions = []
        keywords = self.language_keywords.get(language, [])

        for keyword in keywords:
            if not current_word or keyword.lower().startswith(current_word.lower()):
                completion = CompletionItem(
                    text=keyword,
                    kind="keyword",
                    description=f"{language.upper()} keyword",
                    insert_text=keyword,
                    score=0.9 if not current_word else 0.8,
                )
                completions.append(completion)

        return completions

    def _get_function_completions(
        self, language: str, current_word: str
    ) -> List[CompletionItem]:
        """Get function completions for the language"""
        completions = []
        functions = self.language_functions.get(language, {})

        for func_name, description in functions.items():
            if not current_word or func_name.lower().startswith(current_word.lower()):
                completion = CompletionItem(
                    text=func_name,
                    kind="function",
                    description=description,
                    insert_text=func_name,
                    detail=f"{language.upper()} function",
                    score=0.85,
                )
                completions.append(completion)

        return completions

    def _get_variable_completions(
        self, text: str, current_word: str, language: str
    ) -> List[CompletionItem]:
        """Extract variables from code and suggest completions"""
        completions = []
        variables = set()

        try:
            if language == "basic":
                # Find BASIC variables (LET statements, FOR loops)
                var_patterns = [
                    r"LET\s+([A-Z][A-Z0-9]*)",
                    r"FOR\s+([A-Z][A-Z0-9]*)",
                    r"INPUT\s+([A-Z][A-Z0-9]*)",
                ]

                for pattern in var_patterns:
                    matches = re.findall(pattern, text.upper())
                    variables.update(matches)

            elif language == "pilot":
                # PILOT uses memory locations and labels
                var_patterns = [
                    r"Y:\s*([A-Z][A-Z0-9]*)",
                    r"N:\s*([A-Z][A-Z0-9]*)",
                    r"#([A-Z][A-Z0-9]*)",
                ]

                for pattern in var_patterns:
                    matches = re.findall(pattern, text.upper())
                    variables.update(matches)

            elif language == "logo":
                # Logo variables from MAKE statements
                make_pattern = r'MAKE\s+"([A-Z][A-Z0-9]*)'
                matches = re.findall(make_pattern, text.upper())
                variables.update(matches)

            # Create completions for found variables
            for var in variables:
                if not current_word or var.lower().startswith(current_word.lower()):
                    completion = CompletionItem(
                        text=var,
                        kind="variable",
                        description=f"Variable in {language}",
                        insert_text=var,
                        score=0.7,
                    )
                    completions.append(completion)

        except Exception as e:
            print(f"Error extracting variables: {e}")

        return completions

    def _get_context_completions(
        self, language: str, line_text: str, current_word: str
    ) -> List[CompletionItem]:
        """Get context-aware completions based on current line"""
        completions = []

        try:
            line_upper = line_text.upper().strip()

            # Language-specific context completions
            if language == "basic":
                if line_upper.startswith("IF"):
                    completions.append(
                        CompletionItem(
                            text="THEN",
                            kind="keyword",
                            description="THEN clause for IF statement",
                            score=0.95,
                        )
                    )
                elif line_upper.startswith("FOR"):
                    completions.append(
                        CompletionItem(
                            text="TO",
                            kind="keyword",
                            description="TO clause for FOR loop",
                            score=0.95,
                        )
                    )

            elif language == "pilot":
                if line_upper.startswith("T:"):
                    completions.extend(
                        [
                            CompletionItem(
                                "50", "constant", "Move 50 units", score=0.8
                            ),
                            CompletionItem(
                                "100", "constant", "Move 100 units", score=0.8
                            ),
                        ]
                    )
                elif line_upper.startswith("A:"):
                    completions.extend(
                        [
                            CompletionItem(
                                "90", "constant", "Turn 90 degrees", score=0.8
                            ),
                            CompletionItem(
                                "45", "constant", "Turn 45 degrees", score=0.8
                            ),
                        ]
                    )

            elif language == "logo":
                if line_upper.startswith("REPEAT"):
                    completions.extend(
                        [
                            CompletionItem(
                                "4", "constant", "Repeat 4 times", score=0.8
                            ),
                            CompletionItem(
                                "6", "constant", "Repeat 6 times", score=0.8
                            ),
                            CompletionItem(
                                "[", "constant", "Start command block", score=0.9
                            ),
                        ]
                    )

        except Exception as e:
            print(f"Error getting context completions: {e}")

        return completions

    def get_signature_help(
        self, language: str, function_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get function signature and parameter information"""
        functions = self.language_functions.get(language, {})

        if function_name in functions:
            return {
                "name": function_name,
                "description": functions[function_name],
                "parameters": self._get_function_parameters(language, function_name),
            }

        return None

    def _get_function_parameters(
        self, language: str, function_name: str
    ) -> List[Dict[str, str]]:
        """Get parameter information for function"""
        param_info = {
            "pilot": {
                "T:": [
                    {
                        "name": "distance",
                        "type": "number",
                        "description": "Distance to move",
                    }
                ],
                "A:": [
                    {
                        "name": "angle",
                        "type": "number",
                        "description": "Angle to turn in degrees",
                    }
                ],
                "C:": [
                    {
                        "name": "color",
                        "type": "string",
                        "description": "Color name or code",
                    }
                ],
            },
            "basic": {
                "PRINT": [
                    {
                        "name": "expression",
                        "type": "any",
                        "description": "Value to print",
                    }
                ],
                "LET": [
                    {
                        "name": "variable",
                        "type": "identifier",
                        "description": "Variable name",
                    },
                    {"name": "value", "type": "any", "description": "Value to assign"},
                ],
                "FOR": [
                    {
                        "name": "variable",
                        "type": "identifier",
                        "description": "Loop variable",
                    },
                    {"name": "start", "type": "number", "description": "Start value"},
                    {"name": "end", "type": "number", "description": "End value"},
                ],
            },
            "logo": {
                "FORWARD": [
                    {
                        "name": "distance",
                        "type": "number",
                        "description": "Distance to move",
                    }
                ],
                "LEFT": [
                    {"name": "angle", "type": "number", "description": "Angle to turn"}
                ],
                "REPEAT": [
                    {
                        "name": "count",
                        "type": "number",
                        "description": "Number of repetitions",
                    },
                    {
                        "name": "commands",
                        "type": "list",
                        "description": "Commands to repeat",
                    },
                ],
            },
        }

        return param_info.get(language, {}).get(function_name, [])

    def validate_syntax(
        self, language: str, code: str
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Validate syntax and return errors/warnings

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        try:
            if language == "python":
                try:
                    ast.parse(code)
                    return True, []
                except SyntaxError as e:
                    issues.append(
                        {
                            "type": "error",
                            "line": e.lineno,
                            "column": e.offset,
                            "message": str(e),
                            "severity": "error",
                        }
                    )

            else:
                # Basic syntax validation for educational languages
                lines = code.split("\n")
                for i, line in enumerate(lines, 1):
                    line = line.strip()
                    if not line or line.startswith("REM") or line.startswith("R:"):
                        continue

                    # Check for basic syntax issues
                    if language == "basic":
                        if line.startswith("IF") and "THEN" not in line.upper():
                            issues.append(
                                {
                                    "type": "warning",
                                    "line": i,
                                    "message": "IF statement missing THEN clause",
                                    "severity": "warning",
                                }
                            )

                    elif language == "pilot":
                        if not re.match(r"^[A-Z]:", line.upper()):
                            issues.append(
                                {
                                    "type": "warning",
                                    "line": i,
                                    "message": "PILOT commands should start with letter:",
                                    "severity": "info",
                                }
                            )

            return len([i for i in issues if i["type"] == "error"]) == 0, issues

        except Exception as e:
            issues.append(
                {
                    "type": "error",
                    "line": 1,
                    "message": f"Syntax validation error: {str(e)}",
                    "severity": "error",
                }
            )
            return False, issues


# Global instance for easy access
completion_engine = CodeCompletionEngine()
