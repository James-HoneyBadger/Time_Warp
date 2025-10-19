"""
Syntax Analyzer for Time_Warp IDE
Provides real-time syntax checking and error reporting
"""

import re
import threading
import time
from typing import List, Dict, Optional, Callable, Any, Tuple
from .language_engine import LanguageEngine, BaseLanguageEngine


class SyntaxError:
    """Represents a syntax error or warning"""

    def __init__(
        self,
        line: int,
        column: int,
        message: str,
        error_type: str = "error",
        severity: str = "error",
    ):
        self.line = line
        self.column = column
        self.message = message
        self.error_type = error_type  # error, warning, info
        self.severity = severity
        self.start_pos = None
        self.end_pos = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for easy serialization"""
        return {
            "line": self.line,
            "column": self.column,
            "message": self.message,
            "type": self.error_type,
            "severity": self.severity,
            "start_pos": self.start_pos,
            "end_pos": self.end_pos,
        }


class SyntaxAnalyzer:
    """Main syntax analyzer that works with language engines"""

    def __init__(self, language_engine: LanguageEngine):
        self.language_engine = language_engine
        self.last_analysis_time = 0
        self.analysis_delay = 0.5  # Delay in seconds before analysis
        self.error_callback: Optional[Callable[[List[SyntaxError]], None]] = None
        self.analysis_thread: Optional[threading.Thread] = None
        self.should_analyze = False

    def set_error_callback(self, callback: Callable[[List[SyntaxError]], None]):
        """Set callback for syntax errors"""
        self.error_callback = callback

    def analyze_syntax(
        self, text: str, language: str = None, immediate: bool = False
    ) -> List[SyntaxError]:
        """Analyze syntax and return errors/warnings"""
        if language:
            original_lang = self.language_engine.current_language
            self.language_engine.set_language(language)
            try:
                result = self._analyze_with_current_engine(text, immediate)
            finally:
                self.language_engine.set_language(original_lang)
            return result
        else:
            return self._analyze_with_current_engine(text, immediate)

    def _analyze_with_current_engine(
        self, text: str, immediate: bool = False
    ) -> List[SyntaxError]:
        """Analyze syntax with current language engine"""
        engine = self.language_engine.get_current_engine()
        if not engine:
            return []

        if immediate:
            return self._perform_analysis(text, engine)
        else:
            # Schedule delayed analysis to avoid analyzing while user is typing
            self.should_analyze = True
            self.last_analysis_time = time.time()

            if self.analysis_thread is None or not self.analysis_thread.is_alive():
                self.analysis_thread = threading.Thread(
                    target=self._delayed_analysis, args=(text, engine), daemon=True
                )
                self.analysis_thread.start()

            return []  # Return empty list for now, results will come via callback

    def _delayed_analysis(self, text: str, engine: BaseLanguageEngine):
        """Perform delayed syntax analysis"""
        time.sleep(self.analysis_delay)

        # Check if we should still analyze (user might still be typing)
        if (
            not self.should_analyze
            or time.time() - self.last_analysis_time < self.analysis_delay
        ):
            return

        self.should_analyze = False
        errors = self._perform_analysis(text, engine)

        if self.error_callback:
            self.error_callback(errors)

    def _perform_analysis(
        self, text: str, engine: BaseLanguageEngine
    ) -> List[SyntaxError]:
        """Perform the actual syntax analysis"""
        try:
            # Use the language engine's syntax checking
            engine_errors = engine.check_syntax(text)

            # Convert engine errors to SyntaxError objects
            errors = []
            for error_dict in engine_errors:
                error = SyntaxError(
                    line=error_dict.get("line", 1),
                    column=error_dict.get("column", 1),
                    message=error_dict.get("message", "Unknown error"),
                    error_type=error_dict.get("type", "error"),
                    severity=error_dict.get("severity", "error"),
                )
                errors.append(error)

            # Add additional analysis based on language
            errors.extend(self._additional_analysis(text, engine))

            return errors

        except Exception as e:
            # Return a generic error if analysis fails
            return [
                SyntaxError(
                    line=1,
                    column=1,
                    message=f"Analysis error: {str(e)}",
                    error_type="error",
                    severity="error",
                )
            ]

    def _additional_analysis(
        self, text: str, engine: BaseLanguageEngine
    ) -> List[SyntaxError]:
        """Perform additional language-specific analysis"""
        errors = []
        language = engine.config.name.lower()

        if language == "pilot":
            errors.extend(self._analyze_pilot_specific(text))
        elif language == "basic":
            errors.extend(self._analyze_basic_specific(text))
        elif language == "logo":
            errors.extend(self._analyze_logo_specific(text))
        elif language == "python":
            errors.extend(self._analyze_python_specific(text))

        return errors

    def _analyze_pilot_specific(self, text: str) -> List[SyntaxError]:
        """PILOT-specific syntax analysis"""
        errors = []
        lines = text.split("\n")

        defined_labels = set()
        used_labels = set()

        for i, line in enumerate(lines):
            line_num = i + 1
            stripped = line.strip()

            if not stripped or stripped.startswith("R:"):
                continue

            # Check for label definitions
            if stripped.startswith("*"):
                label = stripped[1:].strip()
                if not label:
                    errors.append(
                        SyntaxError(
                            line=line_num,
                            column=2,
                            message="Empty label definition",
                            error_type="error",
                        )
                    )
                elif label in defined_labels:
                    errors.append(
                        SyntaxError(
                            line=line_num,
                            column=1,
                            message=f"Duplicate label definition: {label}",
                            error_type="error",
                        )
                    )
                else:
                    defined_labels.add(label)
                continue

            # Check command format
            if ":" not in stripped:
                errors.append(
                    SyntaxError(
                        line=line_num,
                        column=1,
                        message="Missing command separator ':'",
                        error_type="error",
                    )
                )
                continue

            command, rest = stripped.split(":", 1)
            command = command.strip().upper()

            # Check for valid commands
            valid_commands = ["T", "A", "J", "Y", "N", "U", "C", "R", "M", "E"]
            if command not in valid_commands:
                errors.append(
                    SyntaxError(
                        line=line_num,
                        column=1,
                        message=f"Unknown PILOT command: {command}",
                        error_type="error",
                    )
                )

            # Check for jump labels
            if command == "J":
                label_match = re.search(r"\*([A-Za-z][A-Za-z0-9]*)", rest)
                if label_match:
                    used_labels.add(label_match.group(1))
                else:
                    errors.append(
                        SyntaxError(
                            line=line_num,
                            column=len(command) + 2,
                            message="Jump command requires a label",
                            error_type="error",
                        )
                    )

        # Check for undefined labels
        for label in used_labels:
            if label not in defined_labels:
                errors.append(
                    SyntaxError(
                        line=1,
                        column=1,
                        message=f"Undefined label: {label}",
                        error_type="warning",
                    )
                )

        return errors

    def _analyze_basic_specific(self, text: str) -> List[SyntaxError]:
        """BASIC-specific syntax analysis"""
        errors = []
        lines = text.split("\n")

        line_numbers = set()

        for i, line in enumerate(lines):
            line_num = i + 1
            stripped = line.strip()

            if not stripped or stripped.startswith("REM") or stripped.startswith("'"):
                continue

            # Check for duplicate line numbers
            line_number_match = re.match(r"^(\d+)\s+", stripped)
            if line_number_match:
                basic_line_num = int(line_number_match.group(1))
                if basic_line_num in line_numbers:
                    errors.append(
                        SyntaxError(
                            line=line_num,
                            column=1,
                            message=f"Duplicate line number: {basic_line_num}",
                            error_type="error",
                        )
                    )
                else:
                    line_numbers.add(basic_line_num)

            # Check for unmatched parentheses
            open_parens = stripped.count("(")
            close_parens = stripped.count(")")
            if open_parens != close_parens:
                errors.append(
                    SyntaxError(
                        line=line_num,
                        column=1,
                        message="Unmatched parentheses",
                        error_type="error",
                    )
                )

            # Check for unmatched quotes
            quote_count = stripped.count('"')
            if quote_count % 2 != 0:
                errors.append(
                    SyntaxError(
                        line=line_num,
                        column=1,
                        message="Unmatched quotes",
                        error_type="error",
                    )
                )

        return errors

    def _analyze_logo_specific(self, text: str) -> List[SyntaxError]:
        """Logo-specific syntax analysis"""
        errors = []
        lines = text.split("\n")

        procedure_stack = []
        defined_procedures = set()

        for i, line in enumerate(lines):
            line_num = i + 1
            stripped = line.strip()

            if not stripped or stripped.startswith(";"):
                continue

            # Check procedure definitions
            to_match = re.match(
                r"^TO\s+([A-Za-z][A-Za-z0-9]*)", stripped, re.IGNORECASE
            )
            if to_match:
                proc_name = to_match.group(1)
                if proc_name.upper() in defined_procedures:
                    errors.append(
                        SyntaxError(
                            line=line_num,
                            column=1,
                            message=f"Duplicate procedure definition: {proc_name}",
                            error_type="error",
                        )
                    )
                else:
                    defined_procedures.add(proc_name.upper())
                    procedure_stack.append((line_num, proc_name))
                continue

            if stripped.upper() == "END":
                if not procedure_stack:
                    errors.append(
                        SyntaxError(
                            line=line_num,
                            column=1,
                            message="END without matching TO",
                            error_type="error",
                        )
                    )
                else:
                    procedure_stack.pop()
                continue

            # Check for unmatched brackets
            open_brackets = stripped.count("[")
            close_brackets = stripped.count("]")
            if open_brackets != close_brackets:
                errors.append(
                    SyntaxError(
                        line=line_num,
                        column=1,
                        message="Unmatched brackets",
                        error_type="error",
                    )
                )

        # Check for unmatched TOs
        for line_num, proc_name in procedure_stack:
            errors.append(
                SyntaxError(
                    line=line_num,
                    column=1,
                    message=f"Procedure {proc_name} missing END",
                    error_type="error",
                )
            )

        return errors

    def _analyze_python_specific(self, text: str) -> List[SyntaxError]:
        """Python-specific syntax analysis"""
        errors = []

        try:
            # Try to compile the code
            compile(text, "<string>", "exec")
        except SyntaxError as e:
            errors.append(
                SyntaxError(
                    line=e.lineno or 1,
                    column=e.offset or 1,
                    message=e.msg or "Syntax error",
                    error_type="error",
                )
            )
        except Exception as e:
            errors.append(
                SyntaxError(
                    line=1,
                    column=1,
                    message=f"Python error: {str(e)}",
                    error_type="error",
                )
            )

        # Additional checks
        lines = text.split("\n")
        for i, line in enumerate(lines):
            line_num = i + 1
            stripped = line.strip()

            if not stripped or stripped.startswith("#"):
                continue

            # Check indentation consistency (simplified)
            if line.startswith(" ") and line.startswith("\t"):
                errors.append(
                    SyntaxError(
                        line=line_num,
                        column=1,
                        message="Mixed tabs and spaces in indentation",
                        error_type="warning",
                    )
                )

        return errors

    def get_error_summary(self, errors: List[SyntaxError]) -> Dict[str, int]:
        """Get summary of errors by type"""
        summary = {"error": 0, "warning": 0, "info": 0}

        for error in errors:
            error_type = error.error_type
            if error_type in summary:
                summary[error_type] += 1

        return summary

    def filter_errors(
        self,
        errors: List[SyntaxError],
        error_types: List[str] = None,
        min_severity: str = None,
    ) -> List[SyntaxError]:
        """Filter errors by type and severity"""
        filtered = errors

        if error_types:
            filtered = [e for e in filtered if e.error_type in error_types]

        if min_severity:
            severity_order = {"info": 0, "warning": 1, "error": 2}
            min_level = severity_order.get(min_severity, 0)
            filtered = [
                e for e in filtered if severity_order.get(e.severity, 0) >= min_level
            ]

        return filtered

    def clear_analysis(self):
        """Clear any pending analysis"""
        self.should_analyze = False
        if self.error_callback:
            self.error_callback([])
