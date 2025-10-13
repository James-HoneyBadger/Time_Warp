"""
TW Python Language Executor
===========================

Implements TW Python, an educational interface to the Python programming language
for the Time_Warp IDE, allowing execution of Python code within the IDE environment.

Language Features:
- Full Python 3 syntax and semantics support
- Variables: dynamic typing with automatic memory management
- Data structures: lists, tuples, dictionaries, sets
- Control structures: if/elif/else, for/while loops, try/except
- Functions: def keyword with parameters and return values
- Classes: object-oriented programming with inheritance
- Modules: import system for code organization
- Built-in functions: print(), len(), range(), enumerate(), zip()
- String operations: formatting, slicing, methods
- File I/O: open(), read(), write(), close()
- Exception handling: raise, try/except/finally blocks
- List comprehensions and generator expressions
- Lambda functions and higher-order functions

The executor provides a bridge to the Python interpreter, allowing
execution of Python code with output capture and error handling within the IDE.
"""

import subprocess
import sys
import os
import tempfile


class PythonExecutor:
    """Handles Python language script execution"""

    def __init__(self, interpreter):
        """Initialize with reference to main interpreter"""
        self.interpreter = interpreter
        self.python_executable = sys.executable  # Use the same Python as Time_Warp

    def execute_command(self, command):
        """Execute a Python command or script"""
        # Handle multi-line Python scripts
        if hasattr(self, "_python_script_buffer"):
            self._python_script_buffer.append(command)
        else:
            self._python_script_buffer = [command]

        # Check if this looks like a complete Python script
        script_text = "\n".join(self._python_script_buffer)

        # For now, execute each command immediately
        # In future versions, could buffer until explicit run command
        return self._execute_python_script(script_text)

    def _execute_python_script(self, script_text):
        """Execute Python script text"""
        try:
            # Create temporary file for the Python script
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False
            ) as temp_file:
                temp_file.write(script_text)
                temp_file_path = temp_file.name

            # Execute the Python script
            result = subprocess.run(
                [self.python_executable, temp_file_path],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Clean up temporary file
            os.unlink(temp_file_path)

            # Display output
            if result.stdout:
                self.interpreter.log_output(result.stdout)

            if result.stderr:
                self.interpreter.log_output(f"Python Error: {result.stderr}")
                return "error"

            if result.returncode != 0:
                self.interpreter.log_output(
                    f"Python script exited with code {result.returncode}"
                )
                return "error"

            return "continue"

        except subprocess.TimeoutExpired:
            self.interpreter.log_output("❌ Python script execution timed out")
            return "error"
        except Exception as e:
            self.interpreter.log_output(f"❌ Error executing Python script: {e}")
            return "error"

    def execute_python_file(self, filepath):
        """Execute a Python file"""
        try:
            if not os.path.exists(filepath):
                self.interpreter.log_output(f"❌ Python file not found: {filepath}")
                return False

            result = subprocess.run(
                [self.python_executable, filepath],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.stdout:
                self.interpreter.log_output(result.stdout)

            if result.stderr:
                self.interpreter.log_output(f"Python Error: {result.stderr}")
                return False

            return result.returncode == 0

        except Exception as e:
            self.interpreter.log_output(f"❌ Error executing Python file: {e}")
            return False

    def get_python_version(self):
        """Get Python version information"""
        return f"Python {sys.version}"
