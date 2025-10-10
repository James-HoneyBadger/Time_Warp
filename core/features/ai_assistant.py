"""
AI Code Assistant for Time_Warp IDE
Provides intelligent code suggestions, bug detection, explanations, and refactoring
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass


@dataclass
class CodeSuggestion:
    """Represents a code suggestion from the AI assistant"""

    suggestion_type: str  # "completion", "fix", "refactor", "optimization"
    original_code: str
    suggested_code: str
    explanation: str
    confidence: float  # 0.0 to 1.0
    line_number: int = 0


@dataclass
class CodeIssue:
    """Represents a code issue detected by the AI"""

    issue_type: str  # "syntax", "logic", "style", "performance"
    severity: str  # "error", "warning", "info"
    message: str
    line_number: int
    column: int
    suggestion: Optional[str] = None


class PilotAnalyzer:
    """Analyzer for PILOT language code"""

    def __init__(self):
        self.valid_commands = ["T", "A", "J", "Y", "N", "U", "C", "L", "E", "END"]
        self.common_patterns = {
            "variable_usage": r"\*([A-Z][A-Z0-9_]*)\*",
            "variable_assignment": r"U:([A-Z][A-Z0-9_]*)=(.+)",
            "calculation": r"C:([A-Z][A-Z0-9_]*)=(.+)",
            "label": r"L:([A-Z][A-Z0-9_]*)",
            "jump": r"J:([A-Z][A-Z0-9_]*)",
            "condition": r"Y:(.+)",
        }

    def analyze_code(self, code: str) -> List[CodeIssue]:
        """Analyze PILOT code for issues"""
        issues = []
        lines = code.split("\n")

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            # Check for valid command structure
            if ":" in line:
                command = line.split(":")[0]
                if command not in self.valid_commands:
                    issues.append(
                        CodeIssue(
                            issue_type="syntax",
                            severity="error",
                            message=f"Unknown command '{command}'. Valid commands: {', '.join(self.valid_commands)}",
                            line_number=line_num,
                            column=0,
                            suggestion=f"Did you mean one of: {self._suggest_command(command)}",
                        )
                    )

            # Check for unmatched variables
            variables_used = re.findall(self.common_patterns["variable_usage"], line)
            for var in variables_used:
                # This is a simplified check - in a real implementation,
                # we'd track variable definitions across the entire program
                if not self._is_variable_defined(var, lines[:line_num]):
                    issues.append(
                        CodeIssue(
                            issue_type="logic",
                            severity="warning",
                            message=f"Variable '{var}' used before being defined",
                            line_number=line_num,
                            column=line.find(f"*{var}*"),
                            suggestion=f"Define the variable first: U:{var}=value",
                        )
                    )

        # Check for missing END statement
        if not any("END" in line for line in lines):
            issues.append(
                CodeIssue(
                    issue_type="syntax",
                    severity="error",
                    message="PILOT programs should end with 'END'",
                    line_number=len(lines),
                    column=0,
                    suggestion="Add 'END' at the end of your program",
                )
            )

        return issues

    def suggest_completions(
        self, code: str, cursor_line: int, cursor_col: int
    ) -> List[CodeSuggestion]:
        """Suggest code completions for PILOT"""
        suggestions = []
        lines = code.split("\n")
        current_line = lines[cursor_line - 1] if cursor_line <= len(lines) else ""

        # Command suggestions
        if current_line.strip() == "" or not ":" in current_line:
            for cmd in self.valid_commands:
                if cmd != "END":  # END doesn't need a colon
                    suggestions.append(
                        CodeSuggestion(
                            suggestion_type="completion",
                            original_code=current_line,
                            suggested_code=f"{cmd}:",
                            explanation=f"Start a {self._get_command_description(cmd)} command",
                            confidence=0.8,
                        )
                    )

        return suggestions

    def _suggest_command(self, invalid_cmd: str) -> str:
        """Suggest similar valid commands"""
        # Simple similarity matching
        similarities = []
        for valid_cmd in self.valid_commands:
            similarity = self._calculate_similarity(invalid_cmd, valid_cmd)
            similarities.append((valid_cmd, similarity))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return ", ".join([cmd for cmd, _ in similarities[:3]])

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate simple string similarity"""
        if str1 == str2:
            return 1.0
        if not str1 or not str2:
            return 0.0

        # Simple character overlap
        overlap = len(set(str1.lower()) & set(str2.lower()))
        return overlap / max(len(str1), len(str2))

    def _is_variable_defined(self, var_name: str, preceding_lines: List[str]) -> bool:
        """Check if a variable is defined in preceding lines"""
        for line in preceding_lines:
            if re.search(rf"U:{var_name}=", line):
                return True
        return False

    def _get_command_description(self, cmd: str) -> str:
        """Get description for PILOT commands"""
        descriptions = {
            "T": "text output",
            "A": "accept input",
            "J": "jump to label",
            "Y": "yes condition",
            "N": "no condition",
            "U": "use/set variable",
            "C": "calculate expression",
            "L": "label definition",
            "E": "end conditional",
        }
        return descriptions.get(cmd, "command")


class BasicAnalyzer:
    """Analyzer for BASIC language code"""

    def __init__(self):
        self.keywords = [
            "PRINT",
            "LET",
            "IF",
            "THEN",
            "GOTO",
            "FOR",
            "TO",
            "NEXT",
            "END",
        ]

    def analyze_code(self, code: str) -> List[CodeIssue]:
        """Analyze BASIC code for issues"""
        issues = []
        lines = code.split("\n")
        line_numbers = []

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            # Check line number format
            parts = line.split(None, 1)
            if parts and parts[0].isdigit():
                line_number = int(parts[0])

                # Check for duplicate line numbers
                if line_number in line_numbers:
                    issues.append(
                        CodeIssue(
                            issue_type="syntax",
                            severity="error",
                            message=f"Duplicate line number {line_number}",
                            line_number=line_num,
                            column=0,
                        )
                    )
                line_numbers.append(line_number)
            else:
                issues.append(
                    CodeIssue(
                        issue_type="syntax",
                        severity="warning",
                        message="BASIC lines should start with line numbers",
                        line_number=line_num,
                        column=0,
                        suggestion="Add a line number like '10 ' at the beginning",
                    )
                )

        return issues


class LogoAnalyzer:
    """Analyzer for Logo language code"""

    def __init__(self):
        self.commands = [
            "FORWARD",
            "FD",
            "BACK",
            "BK",
            "RIGHT",
            "RT",
            "LEFT",
            "LT",
            "PENUP",
            "PU",
            "PENDOWN",
            "PD",
            "REPEAT",
            "HOME",
            "CLEARSCREEN",
            "CS",
        ]

    def analyze_code(self, code: str) -> List[CodeIssue]:
        """Analyze Logo code for issues"""
        issues = []
        lines = code.split("\n")

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            # Check for balanced brackets in REPEAT commands
            if "REPEAT" in line.upper():
                bracket_count = line.count("[") - line.count("]")
                if bracket_count != 0:
                    issues.append(
                        CodeIssue(
                            issue_type="syntax",
                            severity="error",
                            message="Unbalanced brackets in REPEAT command",
                            line_number=line_num,
                            column=line.find("[") if "[" in line else 0,
                            suggestion="Make sure each '[' has a matching ']'",
                        )
                    )

        return issues


class AICodeAssistant:
    """Main AI Code Assistant for Time_Warp IDE"""

    def __init__(self):
        self.analyzers = {
            "pilot": PilotAnalyzer(),
            "basic": BasicAnalyzer(),
            "logo": LogoAnalyzer(),
        }
        self.learning_patterns = {}
        self.user_preferences = {}

    def analyze_code(self, code: str, language: str) -> List[CodeIssue]:
        """Analyze code and return issues found"""
        language = language.lower()
        if language in self.analyzers:
            return self.analyzers[language].analyze_code(code)
        return []

    def get_suggestions(
        self, code: str, language: str, cursor_line: int, cursor_col: int
    ) -> List[CodeSuggestion]:
        """Get intelligent code suggestions"""
        language = language.lower()
        suggestions = []

        if language in self.analyzers:
            analyzer = self.analyzers[language]
            if hasattr(analyzer, "suggest_completions"):
                suggestions.extend(
                    analyzer.suggest_completions(code, cursor_line, cursor_col)
                )

        # Add general suggestions
        suggestions.extend(self._get_general_suggestions(code, language))

        return sorted(suggestions, key=lambda x: x.confidence, reverse=True)

    def explain_code(self, code: str, language: str) -> str:
        """Provide natural language explanation of code"""
        language = language.lower()

        if language == "pilot":
            return self._explain_pilot_code(code)
        elif language == "basic":
            return self._explain_basic_code(code)
        elif language == "logo":
            return self._explain_logo_code(code)
        else:
            return "Code explanation not available for this language yet."

    def suggest_refactoring(self, code: str, language: str) -> List[CodeSuggestion]:
        """Suggest code improvements and refactoring"""
        suggestions = []
        language = language.lower()

        if language == "pilot":
            suggestions.extend(self._suggest_pilot_refactoring(code))

        return suggestions

    def _get_general_suggestions(
        self, code: str, language: str
    ) -> List[CodeSuggestion]:
        """Get general suggestions applicable to any language"""
        suggestions = []

        # Suggest comments for complex code
        if len(code.split("\n")) > 10 and not any(
            line.strip().startswith("#") or "comment" in line.lower()
            for line in code.split("\n")
        ):
            suggestions.append(
                CodeSuggestion(
                    suggestion_type="style",
                    original_code=code,
                    suggested_code=code,  # Would add comments in real implementation
                    explanation="Consider adding comments to explain complex parts of your code",
                    confidence=0.6,
                )
            )

        return suggestions

    def _explain_pilot_code(self, code: str) -> str:
        """Explain PILOT code in natural language"""
        lines = code.split("\n")
        explanations = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith("T:"):
                text = line[2:]
                explanations.append(f"Display the text: '{text}'")
            elif line.startswith("U:"):
                var_assignment = line[2:]
                explanations.append(f"Set variable: {var_assignment}")
            elif line.startswith("C:"):
                calculation = line[2:]
                explanations.append(f"Calculate: {calculation}")
            elif line == "END":
                explanations.append("End the program")

        return "This PILOT program:\n" + "\n".join(f"• {exp}" for exp in explanations)

    def _explain_basic_code(self, code: str) -> str:
        """Explain BASIC code in natural language"""
        lines = code.split("\n")
        explanations = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            parts = line.split(None, 1)
            if len(parts) >= 2 and parts[0].isdigit():
                line_num = parts[0]
                command = parts[1]

                if command.startswith("PRINT"):
                    explanations.append(f"Line {line_num}: Print output to screen")
                elif command.startswith("LET"):
                    explanations.append(f"Line {line_num}: Set a variable value")
                elif command == "END":
                    explanations.append(f"Line {line_num}: End the program")

        return "This BASIC program:\n" + "\n".join(f"• {exp}" for exp in explanations)

    def _explain_logo_code(self, code: str) -> str:
        """Explain Logo code in natural language"""
        lines = code.split("\n")
        explanations = []

        for line in lines:
            line = line.strip().upper()
            if not line:
                continue

            if line.startswith("FORWARD") or line.startswith("FD"):
                explanations.append("Move the turtle forward")
            elif line.startswith("RIGHT") or line.startswith("RT"):
                explanations.append("Turn the turtle right")
            elif line.startswith("LEFT") or line.startswith("LT"):
                explanations.append("Turn the turtle left")
            elif line.startswith("REPEAT"):
                explanations.append("Repeat the following commands")

        return "This Logo program makes the turtle:\n" + "\n".join(
            f"• {exp}" for exp in explanations
        )

    def _suggest_pilot_refactoring(self, code: str) -> List[CodeSuggestion]:
        """Suggest PILOT code improvements"""
        suggestions = []
        lines = code.split("\n")

        # Look for repeated text that could be variables
        text_outputs = []
        for line in lines:
            if line.strip().startswith("T:"):
                text_outputs.append(line.strip()[2:])

        # Find repeated strings
        from collections import Counter

        text_counts = Counter(text_outputs)
        for text, count in text_counts.items():
            if count > 1 and len(text) > 10:  # Only suggest for longer, repeated text
                suggestions.append(
                    CodeSuggestion(
                        suggestion_type="refactor",
                        original_code=f"T:{text}",
                        suggested_code=f"U:MESSAGE={text}\nT:*MESSAGE*",
                        explanation=f"The text '{text}' appears {count} times. Consider using a variable to avoid repetition.",
                        confidence=0.7,
                    )
                )

        return suggestions

    def get_help_for_error(self, error_message: str, language: str) -> str:
        """Provide helpful explanations for error messages"""
        language = language.lower()

        help_messages = {
            "pilot": {
                "unknown command": "Make sure you're using valid PILOT commands: T:, A:, J:, Y:, N:, U:, C:, L:, E:, END",
                "variable not defined": "Define variables before using them with U:VARNAME=value",
                "missing end": "All PILOT programs should end with 'END'",
            },
            "basic": {
                "syntax error": "Check your BASIC syntax - lines should start with numbers, use PRINT for output",
                "line number": "BASIC lines should start with line numbers like 10, 20, 30",
            },
            "logo": {
                "unbalanced": "Make sure all brackets [ ] are properly matched in REPEAT commands"
            },
        }

        if language in help_messages:
            for key, message in help_messages[language].items():
                if key.lower() in error_message.lower():
                    return message

        return "Check your syntax and try again. Use the tutorial system for help with language basics."

    def learn_from_user_code(self, code: str, language: str, success: bool):
        """Learn from user coding patterns to improve suggestions"""
        # In a real implementation, this would use machine learning
        # to improve suggestions based on user patterns
        if language not in self.learning_patterns:
            self.learning_patterns[language] = []

        pattern = {
            "code_length": len(code),
            "complexity": code.count("\n"),
            "success": success,
            "timestamp": datetime.now().isoformat(),
        }

        self.learning_patterns[language].append(pattern)

        # Keep only recent patterns (last 100)
        if len(self.learning_patterns[language]) > 100:
            self.learning_patterns[language] = self.learning_patterns[language][-100:]
