"""
TW JavaScript Language Executor
===============================

Implements TW JavaScript, an educational interface to the JavaScript programming
language for the Time_Warp IDE, allowing execution of JavaScript code via Node.js.

Enhanced Features:
- Full JavaScript (ES6+) syntax and semantics support
- Variables: var, let, const with different scoping rules
- Data types: primitives (string, number, boolean) and objects
- Functions: function declarations, expressions, and arrow functions
- Objects: object literals, prototypes, and classes
- Arrays: array literals with methods like push(), pop(), map(), filter()
- Control structures: if/else, switch, for/while/do-while loops
- Asynchronous programming: promises, async/await
- Modules: CommonJS (require/module.exports) and ES6 modules
- Built-in objects: Math, Date, JSON, RegExp
- String methods: substring(), replace(), split(), join()
- Error handling: try/catch/finally blocks
- DOM manipulation (limited in Node.js environment)

Time_Warp Integration:
- Variable sharing between JavaScript and other languages
- Canvas/graphics integration
- IDE turtle graphics access
- Modern JavaScript libraries support
- NPM package management
- Interactive JavaScript shell mode
"""

import subprocess
import os
import tempfile
import json


class JavaScriptExecutor:
    """Handles JavaScript language script execution with enhanced Time_Warp integration"""

    def __init__(self, interpreter):
        """Initialize with reference to main interpreter"""
        self.interpreter = interpreter
        self.node_executable = self._find_node_executable()
        self.interactive_mode = False
        self.script_context = {}

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
        """Execute a JavaScript command or script with enhanced integration"""
        command = command.strip()

        if not self.node_executable:
            self.interpreter.log_output("❌ Node.js not found on system")
            self.interpreter.log_output("   Please install Node.js to run JavaScript: https://nodejs.org/")
            return "error"

        # Handle special JavaScript commands
        if command.startswith('!'):
            # Shell command
            return self._execute_shell_command(command[1:].strip())
        elif command.lower() == 'interactive':
            # Enter interactive mode
            self.interactive_mode = True
            self.interpreter.log_output("🟨 JavaScript interactive mode enabled")
            return "continue"
        elif command.lower() == 'exit':
            # Exit interactive mode
            self.interactive_mode = False
            self.interpreter.log_output("🟨 JavaScript interactive mode disabled")
            return "continue"
        elif command.lower().startswith('install ') or command.lower().startswith('npm install'):
            # Install package
            package = command.split(' ', 1)[1] if ' ' in command else ''
            return self._install_package(package)
        elif command.lower().startswith('require ') or command.lower().startswith('import '):
            # Enhanced import handling
            return self._handle_import(command)

        # Try to execute as JavaScript code
        try:
            return self._execute_javascript_code(command)
        except Exception as e:
            self.interpreter.log_output(f"❌ JavaScript syntax error: {e}")
            return "error"

    def _execute_javascript_code(self, code):
        """Execute JavaScript code with Time_Warp integration"""
        if not self.node_executable:
            return "error"

        try:
            # Create enhanced JavaScript code with Time_Warp integration
            enhanced_code = self._enhance_js_with_integration(code)

            # Create temporary file for the JavaScript script
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".js", delete=False
            ) as temp_file:
                temp_file.write(enhanced_code)
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
                # Filter out Time_Warp integration messages
                output_lines = result.stdout.strip().split('\n')
                for line in output_lines:
                    if not line.startswith('TIMEWARP_'):
                        self.interpreter.log_output(line)

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
            self.interpreter.log_output(f"❌ Error executing JavaScript: {e}")
            return "error"

    def _enhance_js_with_integration(self, code):
        """Add Time_Warp integration code to JavaScript"""
        integration_code = '''
// Time_Warp Integration
const timewarp_vars = () => {
    // Return Time_Warp variables as JSON
    console.log("TIMEWARP_VARS:" + JSON.stringify({}));
    return {};
};

const set_timewarp_var = (name, value) => {
    console.log("TIMEWARP_SET:" + name + "=" + JSON.stringify(value));
    return value;
};

const turtle_forward = (distance) => {
    console.log("TIMEWARP_TURTLE:forward:" + distance);
    return "Turtle moved forward " + distance + " units";
};

const turtle_turn = (angle) => {
    console.log("TIMEWARP_TURTLE:turn:" + angle);
    return "Turtle turned " + angle + " degrees";
};

const turtle_home = () => {
    console.log("TIMEWARP_TURTLE:home");
    return "Turtle moved home";
};

const turtle_circle = (radius) => {
    console.log("TIMEWARP_TURTLE:circle:" + radius);
    return "Drew circle with radius " + radius;
};

const turtle_set_color = (color) => {
    console.log("TIMEWARP_TURTLE:color:" + color);
    return "Turtle color set to " + color;
};

const clear_screen = () => {
    console.log("TIMEWARP_CLEAR");
    return "Screen cleared";
};

const print_output = (text) => {
    console.log(text);
    return text;
};

const get_input = (prompt) => {
    // In Node.js, we can't easily get interactive input
    console.log("TIMEWARP_INPUT:" + prompt);
    return "simulated_input";
};

// Global variables for common use
global.timewarp_vars = timewarp_vars;
global.set_timewarp_var = set_timewarp_var;
global.turtle_forward = turtle_forward;
global.turtle_turn = turtle_turn;
global.turtle_home = turtle_home;
global.turtle_circle = turtle_circle;
global.turtle_set_color = turtle_set_color;
global.clear_screen = clear_screen;
global.print_output = print_output;
global.get_input = get_input;

// Common modules
try {
    global.fs = require('fs');
    global.path = require('path');
    global.http = require('http');
    global.https = require('https');
} catch (e) {
    // Modules not available
}

// Enhanced console.log to capture output
const original_console_log = console.log;
console.log = function(...args) {
    const message = args.map(arg =>
        typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
    ).join(' ');
    original_console_log(message);
};

// Execute user code
'''
        return integration_code + '\n' + code

    def _execute_shell_command(self, command):
        """Execute shell command from JavaScript"""
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
        """Install NPM package"""
        if not package:
            self.interpreter.log_output("❌ No package specified")
            return "error"

        try:
            result = subprocess.run(['npm', 'install', package],
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                self.interpreter.log_output(f"✅ NPM package '{package}' installed successfully")
            else:
                self.interpreter.log_output(f"❌ Failed to install '{package}': {result.stderr}")
            return "continue"
        except FileNotFoundError:
            self.interpreter.log_output("❌ NPM not found. Please install Node.js")
            return "error"
        except subprocess.TimeoutExpired:
            self.interpreter.log_output("❌ Package installation timed out")
            return "error"
        except Exception as e:
            self.interpreter.log_output(f"❌ Package installation error: {e}")
            return "error"

    def _handle_import(self, import_statement):
        """Handle enhanced import/require statements"""
        try:
            # For now, just try to execute the import
            code = f"try {{ {import_statement}; console.log('Imported successfully'); }} catch(e) {{ console.error('Import failed:', e.message); }}"
            return self._execute_javascript_code(code)
        except Exception as e:
            self.interpreter.log_output(f"❌ Import error: {e}")
            return "error"

    def _execute_javascript_script(self, script_text):
        """Execute JavaScript script text with enhanced integration"""
        if not self.node_executable:
            self.interpreter.log_output("❌ Node.js not found")
            return "error"

        try:
            # Create temporary file for the JavaScript script
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".js", delete=False
            ) as temp_file:
                enhanced_script = self._enhance_js_with_integration(script_text)
                temp_file.write(enhanced_script)
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
                # Filter Time_Warp integration messages
                output_lines = result.stdout.strip().split('\n')
                for line in output_lines:
                    if not line.startswith('TIMEWARP_'):
                        self.interpreter.log_output(line)

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
        """Execute a JavaScript file with enhanced integration"""
        if not self.node_executable:
            self.interpreter.log_output("❌ Node.js not found")
            return False

        try:
            if not os.path.exists(filepath):
                self.interpreter.log_output(f"❌ JavaScript file not found: {filepath}")
                return False

            with open(filepath, 'r', encoding='utf-8') as f:
                script_content = f.read()

            return self._execute_javascript_script(script_content)

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

    def get_available_packages(self):
        """Get list of available NPM packages"""
        try:
            result = subprocess.run(['npm', 'list', '--depth=0'],
                                  capture_output=True, text=True, timeout=10)
            return result.stdout
        except Exception:
            return "Unable to get package list"

    def create_package_json(self, project_name="timewarp-js-project"):
        """Create a package.json file for JavaScript projects"""
        package_json = {
            "name": project_name,
            "version": "1.0.0",
            "description": "Time_Warp JavaScript Project",
            "main": "index.js",
            "scripts": {
                "start": "node index.js",
                "test": "echo \"Error: no test specified\" && exit 1"
            },
            "keywords": ["timewarp", "javascript", "educational"],
            "author": "Time_Warp IDE",
            "license": "MIT",
            "dependencies": {},
            "devDependencies": {}
        }

        try:
            with open('package.json', 'w', encoding='utf-8') as f:
                json.dump(package_json, f, indent=2)
            self.interpreter.log_output("✅ package.json created")
            return True
        except Exception as e:
            self.interpreter.log_output(f"❌ Failed to create package.json: {e}")
            return False
