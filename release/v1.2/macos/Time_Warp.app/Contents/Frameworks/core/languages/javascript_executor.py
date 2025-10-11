"""
JavaScript Language Executor for Time_Warp IDE
==============================================

JavaScript is a high-level, dynamic programming language.

This module handles JavaScript script execution for the Time_Warp IDE using Node.js.
"""

import subprocess
import sys
import os
import tempfile


class JavaScriptExecutor:
    """Handles JavaScript language script execution"""

    def __init__(self, interpreter):
        """Initialize with reference to main interpreter"""
        self.interpreter = interpreter
        self.node_executable = self._find_node_executable()

    def _find_node_executable(self):
        """Find the Node.js executable on the system"""
        # Try common Node.js executable names
        node_names = ["node", "nodejs"]

        for node_name in node_names:
            try:
                # Check if node is available
                result = subprocess.run(
                    [node_name, "--version"], capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    return node_name
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue

        return None

    def execute_command(self, command):
        """Execute a JavaScript command or script"""
        # Handle multi-line JavaScript scripts
        if hasattr(self, "_js_script_buffer"):
            self._js_script_buffer.append(command)
        else:
            self._js_script_buffer = [command]

        # Check if this looks like a complete JavaScript script
        script_text = "\n".join(self._js_script_buffer)

        # For now, execute each command immediately
        # In future versions, could buffer until explicit run command
        return self._execute_javascript_script(script_text)

    def _execute_javascript_script(self, script_text):
        """Execute JavaScript script text"""
        if not self.node_executable:
            self.interpreter.log_output("❌ Node.js not found on system")
            self.interpreter.log_output(
                "   Please install Node.js to run JavaScript scripts"
            )
            return "error"

        try:
            # Create temporary file for the JavaScript script
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".js", delete=False
            ) as temp_file:
                temp_file.write(script_text)
                temp_file_path = temp_file.name

            # Execute the JavaScript script
            result = subprocess.run(
                [self.node_executable, temp_file_path],
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
                self.interpreter.log_output(f"JavaScript Error: {result.stderr}")
                return "error"

            if result.returncode != 0:
                self.interpreter.log_output(
                    f"JavaScript script exited with code {result.returncode}"
                )
                return "error"

            return "continue"

        except subprocess.TimeoutExpired:
            self.interpreter.log_output("❌ JavaScript script execution timed out")
            return "error"
        except Exception as e:
            self.interpreter.log_output(f"❌ Error executing JavaScript script: {e}")
            return "error"

    def execute_javascript_file(self, filepath):
        """Execute a JavaScript file"""
        if not self.node_executable:
            self.interpreter.log_output("❌ Node.js not found")
            return False

        try:
            if not os.path.exists(filepath):
                self.interpreter.log_output(f"❌ JavaScript file not found: {filepath}")
                return False

            result = subprocess.run(
                [self.node_executable, filepath],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.stdout:
                self.interpreter.log_output(result.stdout)

            if result.stderr:
                self.interpreter.log_output(f"JavaScript Error: {result.stderr}")
                return False

            return result.returncode == 0

        except Exception as e:
            self.interpreter.log_output(f"❌ Error executing JavaScript file: {e}")
            return False

    def get_node_version(self):
        """Get Node.js version information"""
        if not self.node_executable:
            return "Node.js not available"

        try:
            result = subprocess.run(
                [self.node_executable, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return f"Node.js {result.stdout.strip()}"
            else:
                return "Node.js not available"
        except Exception:
            return "Node.js not available"
