"""
TW Python Language Executor
===========================

Implements TW Python, an educational interface to the Python programming language
for the Time_Warp IDE, allowing execution of Python code within the IDE environment.

Enhanced Features:
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

Time_Warp Integration:
- Variable sharing between Python and other languages
- Turtle graphics access from Python
- IDE canvas integration
- Modern Python libraries support (matplotlib, numpy, etc.)
- Interactive Python shell mode
- Package management integration
"""

import subprocess
import sys
import os
import tempfile
import ast
import importlib.util
import traceback


class PythonExecutor:
    """Handles Python language script execution with enhanced Time_Warp integration"""

    def __init__(self, interpreter):
        """Initialize with reference to main interpreter"""
        self.interpreter = interpreter
        self.python_executable = sys.executable  # Use the same Python as Time_Warp
        self.interactive_mode = False
        self.script_globals = {}
        self.script_locals = {}
        self._initialize_script_environment()

    def _initialize_script_environment(self):
        """Initialize the Python script execution environment"""
        # Create a custom globals dict with Time_Warp integration
        self.script_globals = {
            '__name__': '__main__',
            '__builtins__': __builtins__,
            # Time_Warp integration functions
            'timewarp_vars': self._get_timewarp_variables,
            'set_timewarp_var': self._set_timewarp_variable,
            'turtle_forward': self._turtle_forward,
            'turtle_turn': self._turtle_turn,
            'turtle_home': self._turtle_home,
            'turtle_circle': self._turtle_circle,
            'turtle_set_color': self._turtle_set_color,
            'clear_screen': self._clear_screen,
            'print_output': self.interpreter.log_output,
            'get_input': self.interpreter.get_user_input,
            # Common imports
            'math': __import__('math'),
            'random': __import__('random'),
            'datetime': __import__('datetime'),
            'json': __import__('json'),
            'os': __import__('os'),
            'sys': __import__('sys'),
        }

        # Try to add optional libraries
        optional_libs = ['numpy', 'matplotlib', 'pandas', 'requests']
        for lib in optional_libs:
            try:
                self.script_globals[lib] = __import__(lib)
            except ImportError:
                pass  # Library not available

        self.script_locals = {}

    def _get_timewarp_variables(self):
        """Get all Time_Warp variables as a Python dict"""
        return dict(self.interpreter.variables)

    def _set_timewarp_variable(self, name, value):
        """Set a Time_Warp variable from Python"""
        self.interpreter.variables[name.upper()] = value
        return value

    def _turtle_forward(self, distance):
        """Move turtle forward from Python"""
        self.interpreter.turtle_forward(distance)
        return f"Turtle moved forward {distance} units"

    def _turtle_turn(self, angle):
        """Turn turtle from Python"""
        self.interpreter.turtle_turn(angle)
        return f"Turtle turned {angle} degrees"

    def _turtle_home(self):
        """Move turtle home from Python"""
        self.interpreter.turtle_home()
        return "Turtle moved home"

    def _turtle_circle(self, radius):
        """Draw circle from Python"""
        self.interpreter.turtle_circle(radius)
        return f"Drew circle with radius {radius}"

    def _turtle_set_color(self, color):
        """Set turtle color from Python"""
        self.interpreter.turtle_set_color(color)
        return f"Turtle color set to {color}"

    def _clear_screen(self):
        """Clear the screen from Python"""
        self.interpreter.clear_turtle_screen()
        return "Screen cleared"

    def execute_command(self, command):
        """Execute a Python command or script with enhanced integration"""
        command = command.strip()

        # Handle special Python commands
        if command.startswith('!'):
            # Shell command
            return self._execute_shell_command(command[1:].strip())
        elif command.lower() == 'interactive':
            # Enter interactive mode
            self.interactive_mode = True
            self.interpreter.log_output("🐍 Python interactive mode enabled")
            return "continue"
        elif command.lower() == 'exit':
            # Exit interactive mode
            self.interactive_mode = False
            self.interpreter.log_output("🐍 Python interactive mode disabled")
            return "continue"
        elif command.lower().startswith('install '):
            # Install package
            return self._install_package(command[8:].strip())
        elif command.lower().startswith('import '):
            # Enhanced import handling
            return self._handle_import(command[7:].strip())

        # Try to execute as Python code
        try:
            # Parse the command to determine if it's complete
            if self._is_complete_python_statement(command):
                return self._execute_python_code(command)
            else:
                # Buffer incomplete statements
                if not hasattr(self, '_python_buffer'):
                    self._python_buffer = []
                self._python_buffer.append(command)
                return "continue"

        except Exception as e:
            self.interpreter.log_output(f"❌ Python syntax error: {e}")
            return "error"

    def _is_complete_python_statement(self, code):
        """Check if the Python code is a complete statement"""
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            # Check if it's an incomplete statement (like just "def" or "if")
            try:
                ast.parse(code + "\npass")
                return False  # Incomplete
            except SyntaxError:
                return False  # Invalid syntax

    def _execute_python_code(self, code):
        """Execute Python code with Time_Warp integration"""
        try:
            # Handle buffered code
            if hasattr(self, '_python_buffer') and self._python_buffer:
                full_code = '\n'.join(self._python_buffer) + '\n' + code
                self._python_buffer = []
            else:
                full_code = code

            # Execute the code
            result = eval(full_code, self.script_globals, self.script_locals)

            # Handle the result
            if result is not None:
                # Store result in special variable
                self.script_locals['_'] = result
                self.interpreter.variables['PYTHON_RESULT'] = str(result)
                self.interpreter.log_output(f"🐍 {result}")

            return "continue"

        except SyntaxError as e:
            # Try to compile and execute as statements
            try:
                compiled_code = compile(full_code, '<string>', 'exec')
                exec(compiled_code, self.script_globals, self.script_locals)
                return "continue"
            except Exception as exec_error:
                self.interpreter.log_output(f"❌ Python execution error: {exec_error}")
                return "error"
        except Exception as e:
            self.interpreter.log_output(f"❌ Python error: {e}")
            return "error"

    def _execute_shell_command(self, command):
        """Execute shell command from Python"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            if result.stdout:
                self.interpreter.log_output(result.stdout)
            if result.stderr:
                self.interpreter.log_output(f"Shell Error: {result.stderr}")
            return "continue"
        except subprocess.TimeoutExpired:
            self.interpreter.log_output("❌ Shell command timed out")
            return "error"
        except Exception as e:
            self.interpreter.log_output(f"❌ Shell command error: {e}")
            return "error"

    def _install_package(self, package):
        """Install Python package"""
        try:
            import pip
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', package],
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                self.interpreter.log_output(f"✅ Package '{package}' installed successfully")
                # Try to import it
                try:
                    self.script_globals[package] = __import__(package)
                    self.interpreter.log_output(f"📦 Package '{package}' imported and available")
                except ImportError:
                    pass
            else:
                self.interpreter.log_output(f"❌ Failed to install '{package}': {result.stderr}")
            return "continue"
        except Exception as e:
            self.interpreter.log_output(f"❌ Package installation error: {e}")
            return "error"

    def _handle_import(self, import_statement):
        """Handle enhanced import statements"""
        try:
            # Execute the import in our environment
            exec(f"import {import_statement}", self.script_globals, self.script_locals)
            self.interpreter.log_output(f"📦 Imported {import_statement}")
            return "continue"
        except ImportError as e:
            self.interpreter.log_output(f"❌ Import error: {e}")
            # Try to suggest installation
            module_name = import_statement.split()[0]
            self.interpreter.log_output(f"💡 Try: install {module_name}")
            return "error"
        except Exception as e:
            self.interpreter.log_output(f"❌ Import error: {e}")
            return "error"

    def _execute_python_script(self, script_text):
        """Execute Python script text with enhanced integration"""
        try:
            # Create temporary file for the Python script
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False
            ) as temp_file:
                # Add Time_Warp integration imports at the top
                enhanced_script = self._enhance_script_with_integration(script_text)
                temp_file.write(enhanced_script)
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

    def _enhance_script_with_integration(self, script_text):
        """Add Time_Warp integration code to Python scripts"""
        integration_code = '''
# Time_Warp Integration
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def timewarp_vars():
    """Get Time_Warp variables"""
    return {}

def set_timewarp_var(name, value):
    """Set Time_Warp variable"""
    print(f"Time_Warp variable {name} = {value}")

def turtle_forward(distance):
    print(f"Turtle forward {distance}")

def turtle_turn(angle):
    print(f"Turtle turn {angle}")

def turtle_home():
    print("Turtle home")

def turtle_circle(radius):
    print(f"Turtle circle {radius}")

def turtle_set_color(color):
    print(f"Turtle color {color}")

def clear_screen():
    print("Screen cleared")

# Common libraries
try:
    import math
    import random
    import json
    import datetime
except ImportError:
    pass

'''
        return integration_code + script_text

    def execute_python_file(self, filepath):
        """Execute a Python file with enhanced integration"""
        try:
            if not os.path.exists(filepath):
                self.interpreter.log_output(f"❌ Python file not found: {filepath}")
                return False

            with open(filepath, 'r', encoding='utf-8') as f:
                script_content = f.read()

            # Execute with integration
            return self._execute_python_script(script_content)

        except Exception as e:
            self.interpreter.log_output(f"❌ Error executing Python file: {e}")
            return False

    def get_python_version(self):
        """Get Python version information"""
        return f"Python {sys.version}"

    def get_available_packages(self):
        """Get list of available Python packages"""
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'list'],
                                  capture_output=True, text=True, timeout=10)
            return result.stdout
        except Exception:
            return "Unable to get package list"

    def create_python_environment(self, requirements_file=None):
        """Create a Python virtual environment"""
        try:
            env_dir = os.path.join(os.getcwd(), 'venv')
            subprocess.run([sys.executable, '-m', 'venv', env_dir], check=True)

            if requirements_file and os.path.exists(requirements_file):
                pip_path = os.path.join(env_dir, 'bin', 'pip') if os.name != 'nt' else os.path.join(env_dir, 'Scripts', 'pip')
                subprocess.run([pip_path, 'install', '-r', requirements_file], check=True)

            self.interpreter.log_output(f"✅ Python environment created at {env_dir}")
            return True
        except Exception as e:
            self.interpreter.log_output(f"❌ Failed to create environment: {e}")
            return False
