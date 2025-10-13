"""
Python Language Executor for Time_Warp IDE
==========================================

Python is a high-level, general-purpose programming language.

This module handles Python script execution for the Time_Warp IDE.
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
