"""
TW Perl Language Executor
=========================

Implements TW Perl, an educational interface to the Perl programming language
for the Time_Warp IDE, allowing execution of Perl scripts within the IDE environment.

Language Features:
- Full Perl syntax and semantics support
- Scalar variables: $variable
- Arrays: @array with indexing
- Hashes: %hash with key-value pairs
- Regular expressions: pattern matching with =~ and !~
- Control structures: if/elsif/else, while, for, foreach
- Subroutines: sub keyword for function definition
- File I/O: open, close, read, write operations
- String operations: concatenation, substr, length, split, join
- Built-in functions: print, chomp, split, join, sort, grep, map
- Modules: use pragma for importing modules
- Object-oriented programming with packages and methods

The executor provides a bridge to system Perl installations, allowing
execution of Perl code with output capture and error handling within the IDE.
"""

import subprocess
import sys
import os
import tempfile


class PerlExecutor:
    """Handles Perl language script execution"""

    def __init__(self, interpreter):
        """Initialize with reference to main interpreter"""
        self.interpreter = interpreter
        self.perl_executable = self._find_perl_executable()

    def _find_perl_executable(self):
        """Find the Perl executable on the system"""
        # Try common Perl executable names
        perl_names = ["perl", "perl5"]

        for perl_name in perl_names:
            try:
                # Check if perl is available
                result = subprocess.run(
                    [perl_name, "--version"], capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    return perl_name
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue

        return None

    def execute_command(self, command):
        """Execute a Perl command or script"""
        # Handle multi-line Perl scripts
        if hasattr(self, "_perl_script_buffer"):
            self._perl_script_buffer.append(command)
        else:
            self._perl_script_buffer = [command]

        # Check if this looks like a complete Perl script
        script_text = "\n".join(self._perl_script_buffer)

        # For now, execute each command immediately
        # In future versions, could buffer until explicit run command
        return self._execute_perl_script(script_text)

    def _execute_perl_script(self, script_text):
        """Execute Perl script text"""
        if not self.perl_executable:
            self.interpreter.log_output("❌ Perl interpreter not found on system")
            self.interpreter.log_output("   Please install Perl to run Perl scripts")
            return "error"

        try:
            # Create temporary file for the Perl script
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".pl", delete=False
            ) as temp_file:
                temp_file.write(script_text)
                temp_file_path = temp_file.name

            # Execute the Perl script
            result = subprocess.run(
                [self.perl_executable, temp_file_path],
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
                self.interpreter.log_output(f"Perl Error: {result.stderr}")
                return "error"

            if result.returncode != 0:
                self.interpreter.log_output(
                    f"Perl script exited with code {result.returncode}"
                )
                return "error"

            return "continue"

        except subprocess.TimeoutExpired:
            self.interpreter.log_output("❌ Perl script execution timed out")
            return "error"
        except Exception as e:
            self.interpreter.log_output(f"❌ Error executing Perl script: {e}")
            return "error"

    def execute_perl_file(self, filepath):
        """Execute a Perl file"""
        if not self.perl_executable:
            self.interpreter.log_output("❌ Perl interpreter not found")
            return False

        try:
            if not os.path.exists(filepath):
                self.interpreter.log_output(f"❌ Perl file not found: {filepath}")
                return False

            result = subprocess.run(
                [self.perl_executable, filepath],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.stdout:
                self.interpreter.log_output(result.stdout)

            if result.stderr:
                self.interpreter.log_output(f"Perl Error: {result.stderr}")
                return False

            return result.returncode == 0

        except Exception as e:
            self.interpreter.log_output(f"❌ Error executing Perl file: {e}")
            return False

    def get_perl_version(self):
        """Get Perl version information"""
        if not self.perl_executable:
            return "Perl not available"

        try:
            result = subprocess.run(
                [self.perl_executable, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                # Extract version from output
                lines = result.stdout.split("\n")
                for line in lines:
                    if "version" in line.lower():
                        return line.strip()
                return "Perl available"
            else:
                return "Perl not available"
        except Exception:
            return "Perl not available"
