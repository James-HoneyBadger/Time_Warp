"""
PILOT Language Handler for Time_Warp IDE
Implements PILOT-style text processing and pattern matching
"""

import re
from typing import Dict, List, Any, Optional, Callable
from ..parser import PilotCommandNode


class PilotVariable:
    """Represents a PILOT variable with pattern matching capabilities"""

    def __init__(self, name: str, value: str = ""):
        self.name = name
        self.value = value
        self.matched_groups: List[str] = []


class PilotHandler:
    """Handler for PILOT language commands"""

    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.variables: Dict[str, PilotVariable] = {}
        self.labels: Dict[str, int] = {}
        self.output_callback: Optional[Callable[[str], None]] = None
        self.input_callback: Optional[Callable[[str], str]] = None

        # Built-in patterns
        self.patterns = {
            "ALPHA": r"[A-Za-z]+",
            "DIGIT": r"\\d+",
            "WORD": r"\\w+",
            "SPACE": r"\\s+",
            "ANY": r".*",
        }

    def execute_command(self, node: PilotCommandNode) -> Any:
        """Execute a PILOT command"""
        command = node.command.rstrip(":")
        argument = node.argument

        if command == "T":
            return self._type_command(argument)
        elif command == "A":
            return self._accept_command(argument)
        elif command == "M":
            return self._match_command(argument)
        elif command == "J":
            return self._jump_command(argument)
        elif command == "C":
            return self._compute_command(argument)
        elif command == "U":
            return self._use_command(argument)
        elif command == "R":
            return self._remark_command(argument)
        elif command == "E":
            return self._end_command(argument)
        else:
            raise ValueError(f"Unknown PILOT command: {command}")

    def _type_command(self, text: str) -> str:
        """T: command - Type/output text"""
        # Process variables in text
        processed_text = self._substitute_variables(text)

        if self.output_callback:
            self.output_callback(processed_text)
        else:
            print(processed_text)

        return processed_text

    def _accept_command(self, variable_spec: str) -> str:
        """A: command - Accept input into variable"""
        var_name = variable_spec.strip()
        if var_name.startswith("#"):
            var_name = var_name[1:]

        prompt = f"Enter {var_name}: " if var_name else ""

        if self.input_callback:
            value = self.input_callback(prompt)
        else:
            value = input(prompt)

        # Store in both PILOT variables and interpreter environment
        self.variables[var_name] = PilotVariable(var_name, value)
        self.interpreter.environment.set(var_name, value)

        return value

    def _match_command(self, match_spec: str) -> bool:
        """M: command - Match pattern against variable"""
        # Parse match specification: variable = pattern
        parts = match_spec.split("=", 1)
        if len(parts) != 2:
            raise ValueError("Invalid match specification")

        var_name = parts[0].strip()
        pattern_spec = parts[1].strip()

        if var_name.startswith("#"):
            var_name = var_name[1:]

        # Get variable value
        if var_name in self.variables:
            value = self.variables[var_name].value
        else:
            try:
                value = str(self.interpreter.environment.get(var_name))
            except:
                value = ""

        # Process pattern
        pattern = self._process_pattern(pattern_spec)

        # Perform match
        match = re.search(pattern, value)
        if match:
            # Store matched groups
            if var_name in self.variables:
                self.variables[var_name].matched_groups = match.groups()
            return True

        return False

    def _jump_command(self, label: str) -> str:
        """J: command - Jump to label"""
        label = label.strip()
        # This would be handled by the interpreter's control flow
        # For now, just return the label
        return label

    def _compute_command(self, expression: str) -> Any:
        """C: command - Compute expression"""
        # Process variables in expression
        processed_expr = self._substitute_variables(expression)

        # Parse assignment if present
        if "=" in processed_expr:
            var_name, expr_part = processed_expr.split("=", 1)
            var_name = var_name.strip()
            if var_name.startswith("#"):
                var_name = var_name[1:]

            # Evaluate expression (simplified)
            try:
                result = eval(expr_part.strip())
                self.variables[var_name] = PilotVariable(var_name, str(result))
                self.interpreter.environment.set(var_name, result)
                return result
            except Exception as e:
                raise ValueError(f"Computation error: {e}")
        else:
            # Just evaluate expression
            try:
                return eval(processed_expr)
            except Exception as e:
                raise ValueError(f"Computation error: {e}")

    def _use_command(self, subroutine: str) -> str:
        """U: command - Use subroutine"""
        subroutine = subroutine.strip()
        # This would call a subroutine
        # For now, just return the subroutine name
        return subroutine

    def _remark_command(self, comment: str) -> None:
        """R: command - Remark (comment)"""
        # Comments do nothing
        pass

    def _end_command(self, argument: str) -> None:
        """E: command - End program"""
        # This would terminate the program
        # For now, just mark end
        pass

    def _substitute_variables(self, text: str) -> str:
        """Substitute #VARIABLE references in text"""

        def replace_var(match):
            var_name = match.group(1)
            if var_name in self.variables:
                return self.variables[var_name].value
            else:
                try:
                    return str(self.interpreter.environment.get(var_name))
                except:
                    return f"#{var_name}"  # Keep original if not found

        # Replace #VARIABLE patterns
        return re.sub(r"#([A-Za-z_]\\w*)", replace_var, text)

    def _process_pattern(self, pattern_spec: str) -> str:
        """Process pattern specification into regex"""
        # Handle quoted strings
        if pattern_spec.startswith('"') and pattern_spec.endswith('"'):
            return re.escape(pattern_spec[1:-1])

        # Handle built-in patterns
        if pattern_spec in self.patterns:
            return self.patterns[pattern_spec]

        # Handle pattern variables
        if pattern_spec.startswith("#"):
            var_name = pattern_spec[1:]
            if var_name in self.variables:
                return re.escape(self.variables[var_name].value)

        # Default: treat as literal string
        return re.escape(pattern_spec)

    def set_callbacks(
        self,
        output_callback: Callable[[str], None],
        input_callback: Callable[[str], str],
    ):
        """Set I/O callbacks"""
        self.output_callback = output_callback
        self.input_callback = input_callback

    def reset(self):
        """Reset PILOT state"""
        self.variables.clear()
        self.labels.clear()
