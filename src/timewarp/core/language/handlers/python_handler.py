"""
Python Integration Handler for Time_Warp IDE
Handles execution of Python code blocks within Time_Warp programs
"""

import sys
import traceback
from typing import Dict, Any, Optional, Callable, List
from ..parser import PythonBlockNode


class PythonHandler:
    """Handler for Python code integration"""

    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.python_globals: Dict[str, Any] = {}
        self.python_locals: Dict[str, Any] = {}
        self.setup_python_environment()

    def setup_python_environment(self):
        """Setup Python execution environment with Time_Warp interface"""
        # Standard Python builtins
        self.python_globals.update(
            __builtins__ if isinstance(__builtins__, dict) else __builtins__.__dict__
        )

        # Common modules
        self.python_globals.update(
            {
                "math": __import__("math"),
                "random": __import__("random"),
                "time": __import__("time"),
                "os": __import__("os"),
                "sys": sys,
            }
        )

        # Time_Warp interface
        self.python_globals["Time_Warp"] = TimeWarpPythonInterface(self.interpreter)

    def execute_python_block(self, node: PythonBlockNode) -> Dict[str, Any]:
        """Execute Python code block"""
        try:
            # Create fresh local scope for this block
            local_scope = dict(self.python_locals)

            # Execute the code
            exec(node.code, self.python_globals, local_scope)

            # Update persistent locals with new/modified variables
            self.python_locals.update(local_scope)

            # Return the local variables created/modified in this block
            new_vars = {
                k: v
                for k, v in local_scope.items()
                if k not in self.python_locals or self.python_locals[k] != v
            }

            return new_vars

        except Exception as e:
            error_msg = f"Python execution error: {str(e)}\\n{traceback.format_exc()}"
            raise RuntimeError(error_msg)

    def add_module(self, name: str, module: Any):
        """Add a module to the Python environment"""
        self.python_globals[name] = module

    def set_variable(self, name: str, value: Any):
        """Set a Python variable"""
        self.python_locals[name] = value

    def get_variable(self, name: str) -> Any:
        """Get a Python variable"""
        if name in self.python_locals:
            return self.python_locals[name]
        elif name in self.python_globals:
            return self.python_globals[name]
        else:
            raise NameError(f"Name '{name}' is not defined")

    def reset(self):
        """Reset Python environment"""
        self.python_locals.clear()
        self.setup_python_environment()


class TimeWarpPythonInterface:
    """Interface for accessing Time_Warp from Python code"""

    def __init__(self, interpreter):
        self.interpreter = interpreter

    def GET(self, name: str) -> Any:
        """Get a Time_Warp variable from Python"""
        try:
            return self.interpreter.environment.get(name)
        except Exception:
            raise NameError(f"Time_Warp variable '{name}' not found")

    def SET(self, name: str, value: Any):
        """Set a Time_Warp variable from Python"""
        self.interpreter.environment.set(name, value)

    def CALL(self, name: str, *args) -> Any:
        """Call a Time_Warp function from Python"""
        try:
            func = self.interpreter.environment.get(name)
            if hasattr(func, "call"):  # TimeWarpFunction
                return func.call(self.interpreter, list(args))
            elif callable(func):
                return func(*args)
            else:
                raise TypeError(f"'{name}' is not callable")
        except Exception as e:
            raise RuntimeError(f"Error calling Time_Warp function '{name}': {e}")

    def PRINT(self, *args, sep=" ", end="\\n"):
        """Print from Python to Time_Warp output"""
        output = sep.join(str(arg) for arg in args) + end
        self.interpreter.output_buffer.append(output.rstrip("\\n"))

    def INPUT(self, prompt: str = "") -> str:
        """Get input through Time_Warp input system"""
        if self.interpreter.input_callback:
            return self.interpreter.input_callback(prompt)
        else:
            return input(prompt)

    def VARS(self) -> Dict[str, Any]:
        """Get all Time_Warp variables as a dictionary"""
        return dict(self.interpreter.environment.variables)

    def EVAL(self, timewarp_expression: str) -> Any:
        """Evaluate a Time_Warp expression from Python"""
        from ..lexer import TimeWarpLexer
        from ..parser import TimeWarpParser

        try:
            lexer = TimeWarpLexer()
            parser = TimeWarpParser()

            tokens = lexer.tokenize(timewarp_expression)
            # Parse as a single expression
            parser.tokens = tokens
            parser.current = 0
            expr_node = parser._expression()

            return self.interpreter.execute(expr_node)
        except Exception as e:
            raise RuntimeError(
                f"Error evaluating Time_Warp expression '{timewarp_expression}': {e}"
            )

    def RUN(self, timewarp_code: str):
        """Execute Time_Warp code from Python"""
        from ..lexer import TimeWarpLexer
        from ..parser import TimeWarpParser

        try:
            lexer = TimeWarpLexer()
            parser = TimeWarpParser()

            tokens = lexer.tokenize(timewarp_code)
            program = parser.parse(tokens)

            for statement in program.statements:
                if statement:
                    self.interpreter.execute(statement)
        except Exception as e:
            raise RuntimeError(f"Error executing Time_Warp code: {e}")


class BasicHandler:
    """Handler for BASIC-style programming constructs"""

    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.line_numbers: Dict[int, int] = {}  # line_number -> statement_index
        self.data_statements: List[Any] = []
        self.data_pointer: int = 0
        self.gosub_stack: List[int] = []

    def register_line_number(self, line_num: int, stmt_index: int):
        """Register a line number for GOTO/GOSUB"""
        self.line_numbers[line_num] = stmt_index

    def goto_line(self, line_num: int) -> int:
        """Get statement index for line number"""
        if line_num in self.line_numbers:
            return self.line_numbers[line_num]
        else:
            raise RuntimeError(f"Line number {line_num} not found")

    def gosub_line(self, line_num: int) -> int:
        """GOSUB to line number"""
        # Push current position to stack
        self.gosub_stack.append(self.interpreter.current_statement_index)
        return self.goto_line(line_num)

    def return_from_gosub(self) -> int:
        """RETURN from GOSUB"""
        if not self.gosub_stack:
            raise RuntimeError("RETURN without GOSUB")
        return self.gosub_stack.pop()

    def add_data(self, values: List[Any]):
        """Add DATA values"""
        self.data_statements.extend(values)

    def read_data(self) -> Any:
        """READ next data value"""
        if self.data_pointer >= len(self.data_statements):
            raise RuntimeError("Out of DATA")

        value = self.data_statements[self.data_pointer]
        self.data_pointer += 1
        return value

    def restore_data(self, line_num: Optional[int] = None):
        """RESTORE data pointer"""
        if line_num is None:
            self.data_pointer = 0
        else:
            # Find DATA statement at or after line number
            # For now, just reset to beginning
            self.data_pointer = 0

    def reset(self):
        """Reset BASIC state"""
        self.line_numbers.clear()
        self.data_statements.clear()
        self.data_pointer = 0
        self.gosub_stack.clear()
