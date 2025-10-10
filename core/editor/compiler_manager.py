"""
Compiler Manager for Time_Warp IDE
Handles compilation of different languages and execution of compiled programs
"""

import os
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
from typing import Dict, List, Optional, Callable, Any
from pathlib import Path
import tempfile
import shutil


class CompilerResult:
    """Result of compilation process"""

    def __init__(
        self,
        success: bool,
        output: str = "",
        error: str = "",
        executable_path: str = "",
    ):
        self.success = success
        self.output = output
        self.error = error
        self.executable_path = executable_path
        self.compilation_time = 0.0


class CompilerEngine:
    """Base compiler engine"""

    def __init__(self, name: str, language: str):
        self.name = name
        self.language = language
        self.output_callback: Optional[Callable[[str], None]] = None

    def set_output_callback(self, callback: Callable[[str], None]):
        """Set callback for compilation output"""
        self.output_callback = callback

    def compile(self, source_file: str, output_file: str = "") -> CompilerResult:
        """Compile source file"""
        raise NotImplementedError("Subclasses must implement compile method")

    def run_executable(self, executable_path: str) -> subprocess.Popen:
        """Run compiled executable"""
        try:
            return subprocess.Popen(
                [executable_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        except Exception as e:
            if self.output_callback:
                self.output_callback(f"❌ Error running executable: {str(e)}")
            return None


class PILOTCompiler(CompilerEngine):
    """PILOT language compiler"""

    def __init__(self):
        super().__init__("PILOT Compiler", "pilot")

    def compile(self, source_file: str, output_file: str = "") -> CompilerResult:
        """Compile PILOT source file"""
        if not output_file:
            output_file = source_file + "_compiled"

        try:
            # Import PILOT compiler
            from pilot_compiler import PILOTCompiler as PilotComp

            compiler = PilotComp()
            result = compiler.compile_file(source_file, output_file)

            if result.get("success", False):
                return CompilerResult(
                    success=True,
                    output=result.get("output", "Compilation successful"),
                    executable_path=output_file,
                )
            else:
                return CompilerResult(
                    success=False, error=result.get("error", "Compilation failed")
                )

        except ImportError:
            return CompilerResult(success=False, error="PILOT compiler not available")
        except Exception as e:
            return CompilerResult(success=False, error=f"Compilation error: {str(e)}")


class BASICCompiler(CompilerEngine):
    """BASIC language compiler"""

    def __init__(self):
        super().__init__("BASIC Compiler", "basic")

    def compile(self, source_file: str, output_file: str = "") -> CompilerResult:
        """Compile BASIC source file"""
        if not output_file:
            output_file = source_file + "_compiled"

        try:
            # Import BASIC compiler
            from basic_compiler import BASICCompiler as BasicComp

            compiler = BasicComp()
            result = compiler.compile_file(source_file, output_file)

            if result.get("success", False):
                return CompilerResult(
                    success=True,
                    output=result.get("output", "Compilation successful"),
                    executable_path=output_file,
                )
            else:
                return CompilerResult(
                    success=False, error=result.get("error", "Compilation failed")
                )

        except ImportError:
            return CompilerResult(success=False, error="BASIC compiler not available")
        except Exception as e:
            return CompilerResult(success=False, error=f"Compilation error: {str(e)}")


class LogoCompiler(CompilerEngine):
    """Logo language compiler"""

    def __init__(self):
        super().__init__("Logo Compiler", "logo")

    def compile(self, source_file: str, output_file: str = "") -> CompilerResult:
        """Compile Logo source file"""
        if not output_file:
            output_file = source_file + "_compiled"

        try:
            # Import Logo compiler
            from logo_compiler import LogoCompiler as LogoComp

            compiler = LogoComp()
            result = compiler.compile_file(source_file, output_file)

            if result.get("success", False):
                return CompilerResult(
                    success=True,
                    output=result.get("output", "Compilation successful"),
                    executable_path=output_file,
                )
            else:
                return CompilerResult(
                    success=False, error=result.get("error", "Compilation failed")
                )

        except ImportError:
            return CompilerResult(success=False, error="Logo compiler not available")
        except Exception as e:
            return CompilerResult(success=False, error=f"Compilation error: {str(e)}")


class CompilerManager:
    """Manages all compilers and compilation processes"""

    def __init__(self):
        self.compilers = {
            "pilot": PILOTCompiler(),
            "basic": BASICCompiler(),
            "logo": LogoCompiler(),
        }
        self.current_compiler = None
        self.output_callback: Optional[Callable[[str], None]] = None
        self.running_processes: List[subprocess.Popen] = []

    def set_output_callback(self, callback: Callable[[str], None]):
        """Set callback for output messages"""
        self.output_callback = callback
        for compiler in self.compilers.values():
            compiler.set_output_callback(callback)

    def get_available_compilers(self) -> List[str]:
        """Get list of available compilers"""
        return list(self.compilers.keys())

    def set_compiler(self, language: str) -> bool:
        """Set current compiler by language"""
        if language.lower() in self.compilers:
            self.current_compiler = self.compilers[language.lower()]
            return True
        return False

    def compile_file(
        self, source_file: str, language: str = None, output_file: str = ""
    ) -> CompilerResult:
        """Compile a source file"""
        if language:
            if not self.set_compiler(language):
                return CompilerResult(
                    success=False, error=f"Compiler for {language} not available"
                )

        if not self.current_compiler:
            return CompilerResult(success=False, error="No compiler selected")

        if not os.path.exists(source_file):
            return CompilerResult(
                success=False, error=f"Source file not found: {source_file}"
            )

        if self.output_callback:
            self.output_callback(
                f"🔨 Compiling {source_file} with {self.current_compiler.name}..."
            )

        # Perform compilation in a separate thread to avoid blocking UI
        result = self.current_compiler.compile(source_file, output_file)

        if result.success:
            if self.output_callback:
                self.output_callback(
                    f"✅ Compilation successful: {result.executable_path}"
                )
        else:
            if self.output_callback:
                self.output_callback(f"❌ Compilation failed: {result.error}")

        return result

    def compile_text(
        self, text: str, language: str, filename: str = "temp"
    ) -> CompilerResult:
        """Compile text content"""
        # Create temporary file
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, f"{filename}.{language}")

        try:
            with open(temp_file, "w") as f:
                f.write(text)

            result = self.compile_file(temp_file, language)

            # Copy compiled file to working directory if successful
            if result.success and result.executable_path:
                working_file = f"{filename}_{language}_compiled"
                if os.path.exists(result.executable_path):
                    shutil.copy2(result.executable_path, working_file)
                    result.executable_path = working_file

            return result

        except Exception as e:
            return CompilerResult(
                success=False, error=f"Error creating temporary file: {str(e)}"
            )
        finally:
            # Clean up temporary directory
            try:
                shutil.rmtree(temp_dir)
            except:
                pass

    def run_compiled_program(self, executable_path: str) -> Optional[subprocess.Popen]:
        """Run a compiled program"""
        if not os.path.exists(executable_path):
            if self.output_callback:
                self.output_callback(f"❌ Executable not found: {executable_path}")
            return None

        if self.output_callback:
            self.output_callback(f"🚀 Running {executable_path}...")

        try:
            process = subprocess.Popen(
                [executable_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            self.running_processes.append(process)

            # Start a thread to monitor the process
            def monitor_process():
                try:
                    stdout, stderr = process.communicate(timeout=30)

                    if stdout and self.output_callback:
                        self.output_callback(f"📤 Output:\n{stdout}")

                    if stderr and self.output_callback:
                        self.output_callback(f"⚠️ Errors:\n{stderr}")

                    if process.returncode == 0:
                        if self.output_callback:
                            self.output_callback("✅ Program completed successfully")
                    else:
                        if self.output_callback:
                            self.output_callback(
                                f"❌ Program exited with code {process.returncode}"
                            )

                except subprocess.TimeoutExpired:
                    process.kill()
                    if self.output_callback:
                        self.output_callback("⏰ Program execution timed out")
                except Exception as e:
                    if self.output_callback:
                        self.output_callback(f"❌ Error running program: {str(e)}")
                finally:
                    if process in self.running_processes:
                        self.running_processes.remove(process)

            thread = threading.Thread(target=monitor_process, daemon=True)
            thread.start()

            return process

        except Exception as e:
            if self.output_callback:
                self.output_callback(f"❌ Error starting program: {str(e)}")
            return None

    def stop_all_processes(self):
        """Stop all running processes"""
        for process in self.running_processes[:]:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception:
                pass

        self.running_processes.clear()

        if self.output_callback:
            self.output_callback("⏹️ All processes stopped")

    def get_compilation_menu_items(self) -> List[Dict[str, Any]]:
        """Get menu items for compilation options"""
        items = []

        for lang, compiler in self.compilers.items():
            items.append(
                {
                    "label": f"🔨 Compile {lang.upper()}",
                    "command": lambda l=lang: self._compile_current_file(l),
                    "language": lang,
                }
            )

            items.append(
                {
                    "label": f"🚀 Compile & Run {lang.upper()}",
                    "command": lambda l=lang: self._compile_and_run_current_file(l),
                    "language": lang,
                }
            )

        return items

    def _compile_current_file(self, language: str):
        """Compile current file (to be connected to main app)"""
        # This will be connected to the main application
        if self.output_callback:
            self.output_callback(f"Ready to compile {language} file")

    def _compile_and_run_current_file(self, language: str):
        """Compile and run current file (to be connected to main app)"""
        # This will be connected to the main application
        if self.output_callback:
            self.output_callback(f"Ready to compile and run {language} file")

    def supports_language(self, language: str) -> bool:
        """Check if language is supported for compilation"""
        return language.lower() in self.compilers

    def get_compiler_info(self, language: str) -> Optional[CompilerEngine]:
        """Get compiler information for a language"""
        return self.compilers.get(language.lower())
