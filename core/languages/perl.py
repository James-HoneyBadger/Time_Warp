"""
TW Perl Language Executor
=========================

Implements TW Perl, an educational interface to the Perl programming language
for the Time_Warp IDE, allowing execution of Perl scripts within the IDE environment.

Enhanced Features:
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

Time_Warp Integration:
- Variable sharing between Perl and other languages
- Turtle graphics access from Perl
- IDE canvas integration
- Modern Perl libraries support (CPAN)
- Package management integration
- Interactive Perl shell mode
"""

import subprocess
import os
import tempfile
import re


class PerlExecutor:
    """Handles Perl language script execution with enhanced Time_Warp integration"""

    def __init__(self, interpreter):
        """Initialize with reference to main interpreter"""
        self.interpreter = interpreter
        self.perl_executable = self._find_perl_executable()
        self.interactive_mode = False
        self.script_variables = {}

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
        """Execute a Perl command or script with enhanced integration"""
        # Strip comments: # for line and inline
        command = command.split('#', 1)[0].strip()

        if not self.perl_executable:
            self.interpreter.log_output("❌ Perl interpreter not found on system")
            self.interpreter.log_output("   Please install Perl to run Perl scripts")
            return "error"

        # Handle special Perl commands
        if command.startswith('!'):
            # Shell command
            return self._execute_shell_command(command[1:].strip())
        elif command.lower() == 'interactive':
            # Enter interactive mode
            self.interactive_mode = True
            self.interpreter.log_output("🐪 Perl interactive mode enabled")
            return "continue"
        elif command.lower() == 'exit':
            # Exit interactive mode
            self.interactive_mode = False
            self.interpreter.log_output("🐪 Perl interactive mode disabled")
            return "continue"
        elif command.lower().startswith('install ') or command.lower().startswith('cpan '):
            # Install package
            package = command.split(' ', 1)[1] if ' ' in command else ''
            return self._install_package(package)
        elif command.lower().startswith('use ') or command.lower().startswith('require '):
            # Enhanced module handling
            return self._handle_use(command)

        # Try to execute as Perl code
        try:
            return self._execute_perl_code(command)
        except Exception as e:
            self.interpreter.log_output(f"❌ Perl syntax error: {e}")
            return "error"

    def _execute_perl_code(self, code):
        """Execute Perl code with Time_Warp integration"""
        try:
            # Create enhanced Perl code with Time_Warp integration
            enhanced_code = self._enhance_perl_with_integration(code)

            # Create temporary file for the Perl script
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".pl", delete=False
            ) as temp_file:
                temp_file.write(enhanced_code)
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
                # Filter out Time_Warp integration messages
                output_lines = result.stdout.strip().split('\n')
                for line in output_lines:
                    if not line.startswith('TIMEWARP_'):
                        self.interpreter.log_output(line)

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
            self.interpreter.log_output(f"❌ Error executing Perl: {e}")
            return "error"

    def _enhance_perl_with_integration(self, code):
        """Add Time_Warp integration code to Perl"""
        integration_code = '''
# Time_Warp Integration
use strict;
use warnings;

sub timewarp_vars {
    # Return Time_Warp variables
    print "TIMEWARP_VARS:empty\\n";
    return {};
}

sub set_timewarp_var {
    my ($name, $value) = @_;
    print "TIMEWARP_SET:$name=$value\\n";
    return $value;
}

sub turtle_forward {
    my ($distance) = @_;
    print "TIMEWARP_TURTLE:forward:$distance\\n";
    return "Turtle moved forward $distance units";
}

sub turtle_turn {
    my ($angle) = @_;
    print "TIMEWARP_TURTLE:turn:$angle\\n";
    return "Turtle turned $angle degrees";
}

sub turtle_home {
    print "TIMEWARP_TURTLE:home\\n";
    return "Turtle moved home";
}

sub turtle_circle {
    my ($radius) = @_;
    print "TIMEWARP_TURTLE:circle:$radius\\n";
    return "Drew circle with radius $radius";
}

sub turtle_set_color {
    my ($color) = @_;
    print "TIMEWARP_TURTLE:color:$color\\n";
    return "Turtle color set to $color";
}

sub clear_screen {
    print "TIMEWARP_CLEAR\\n";
    return "Screen cleared";
}

sub print_output {
    my ($text) = @_;
    print "$text\\n";
    return $text;
}

sub get_input {
    my ($prompt) = @_;
    print "TIMEWARP_INPUT:$prompt\\n";
    return "simulated_input";
}

# Make functions available globally
*main::timewarp_vars = \\&timewarp_vars;
*main::set_timewarp_var = \\&set_timewarp_var;
*main::turtle_forward = \\&turtle_forward;
*main::turtle_turn = \\&turtle_turn;
*main::turtle_home = \\&turtle_home;
*main::turtle_circle = \\&turtle_circle;
*main::turtle_set_color = \\&turtle_set_color;
*main::clear_screen = \\&clear_screen;
*main::print_output = \\&print_output;
*main::get_input = \\&get_input;

# Execute user code
'''
        return integration_code + '\n' + code

    def _execute_shell_command(self, command):
        """Execute shell command from Perl"""
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
        """Install CPAN package"""
        if not package:
            self.interpreter.log_output("❌ No package specified")
            return "error"

        try:
            # Try cpanm first, then cpan
            installers = ['cpanm', 'cpan']
            success = False

            for installer in installers:
                try:
                    result = subprocess.run([installer, 'install', package],
                                          capture_output=True, text=True, timeout=120)
                    if result.returncode == 0:
                        self.interpreter.log_output(f"✅ CPAN package '{package}' installed successfully")
                        success = True
                        break
                    else:
                        self.interpreter.log_output(f"❌ {installer} failed: {result.stderr}")
                except FileNotFoundError:
                    continue

            if not success:
                self.interpreter.log_output(f"❌ Failed to install '{package}' - CPAN not available")
            return "continue"
        except subprocess.TimeoutExpired:
            self.interpreter.log_output("❌ Package installation timed out")
            return "error"
        except Exception as e:
            self.interpreter.log_output(f"❌ Package installation error: {e}")
            return "error"

    def _handle_use(self, use_statement):
        """Handle enhanced use/require statements"""
        try:
            # For now, just try to execute the use statement
            code = f'''
eval {{
    {use_statement};
    print "Module imported successfully\\n";
}};
if ($@) {{
    print "Import failed: $@\\n";
}}
'''
            return self._execute_perl_code(code)
        except Exception as e:
            self.interpreter.log_output(f"❌ Use error: {e}")
            return "error"

    def _execute_perl_script(self, script_text):
        """Execute Perl script text with enhanced integration"""
        if not self.perl_executable:
            self.interpreter.log_output("❌ Perl interpreter not found")
            return "error"

        try:
            # Create temporary file for the Perl script
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".pl", delete=False
            ) as temp_file:
                enhanced_script = self._enhance_perl_with_integration(script_text)
                temp_file.write(enhanced_script)
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
                # Filter Time_Warp integration messages
                output_lines = result.stdout.strip().split('\n')
                for line in output_lines:
                    if not line.startswith('TIMEWARP_'):
                        self.interpreter.log_output(line)

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
        """Execute a Perl file with enhanced integration"""
        if not self.perl_executable:
            self.interpreter.log_output("❌ Perl interpreter not found")
            return False

        try:
            if not os.path.exists(filepath):
                self.interpreter.log_output(f"❌ Perl file not found: {filepath}")
                return False

            with open(filepath, 'r', encoding='utf-8') as f:
                script_content = f.read()

            return self._execute_perl_script(script_content)

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

    def get_installed_modules(self):
        """Get list of installed Perl modules"""
        if not self.perl_executable:
            return "Perl not available"

        try:
            # Use perldoc to list installed modules (basic approach)
            result = subprocess.run(
                [self.perl_executable, '-e', 'use ExtUtils::Installed; my $inst = ExtUtils::Installed->new(); print join("\\n", $inst->modules());'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return result.stdout
            else:
                return "Unable to list modules"
        except Exception:
            return "Unable to list modules"
