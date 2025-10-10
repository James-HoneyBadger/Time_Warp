#!/usr/bin/env python3
"""
Time_Warp Native Compilers
==========================

A unified compiler framework for converting Time_Warp IDE languages
(BASIC, Logo, PILOT) into standalone Linux executables.

This framework provides:
- Unified compiler interface
- Common code generation utilities
- Cross-language optimizations
- Native executable output
"""

import os
import subprocess
import tempfile
from abc import ABC, abstractmethod
from typing import List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class Language(Enum):
    """Supported programming languages"""

    BASIC = "basic"
    LOGO = "logo"
    PILOT = "pilot"


@dataclass
class CompilerResult:
    """Result of compilation process"""

    success: bool
    executable_path: Optional[str] = None
    error_message: Optional[str] = None
    warnings: Optional[List[str]] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class CodeGenerator(ABC):
    """Abstract base class for code generators"""

    def __init__(self, language: Language):
        self.language = language
        self.debug = False
        self.optimize = False

    @abstractmethod
    def generate_header(self) -> List[str]:
        """Generate language-specific header code"""
        raise NotImplementedError

    @abstractmethod
    def generate_runtime(self) -> List[str]:
        """Generate runtime support functions"""
        raise NotImplementedError

    @abstractmethod
    def generate_main(self, statements: List[Any]) -> List[str]:
        """Generate main function from parsed statements"""
        raise NotImplementedError

    def generate_c_code(self, statements: List[Any]) -> str:
        """Generate complete C code"""
        lines = []

        # Add header
        lines.extend(self.generate_header())

        # Add runtime functions
        lines.extend(self.generate_runtime())

        # Add main function
        lines.extend(self.generate_main(statements))

        return "\n".join(lines)


class BaseCompiler(ABC):
    """Abstract base compiler class"""

    def __init__(self, language: Language):
        self.language = language
        self.debug = False
        self.optimize = False
        self.code_generator = self.create_code_generator()

    @abstractmethod
    def create_code_generator(self) -> CodeGenerator:
        """Create the appropriate code generator"""
        raise NotImplementedError

    @abstractmethod
    def parse_source(self, source: str) -> List[Any]:
        """Parse source code into statements"""
        raise NotImplementedError

    def compile_file(
        self, input_file: str, output_file: Optional[str] = None
    ) -> CompilerResult:
        """Compile source file to executable"""
        try:
            # Read source
            with open(input_file, "r", encoding="utf-8") as f:
                source = f.read()

            # Determine output filename
            if not output_file:
                base_name = os.path.splitext(os.path.basename(input_file))[0]
                output_file = f"{base_name}_compiled"

            return self.compile_source(source, output_file)

        except (IOError, OSError) as e:
            return CompilerResult(success=False, error_message=f"File error: {str(e)}")

    def compile_source(self, source: str, output_file: str) -> CompilerResult:
        """Compile source code to executable"""
        try:
            print(
                f"🔧 Compiling {self.language.value.upper()} source to executable: {output_file}"
            )

            # Parse source
            print("📝 Step 1: Parsing source...")
            statements = self.parse_source(source)
            print(f"   Found {len(statements)} statements")

            if self.debug:
                self.print_statements(statements)

            # Generate C code
            print("⚙️  Step 2: Generating C code...")
            c_code = self.code_generator.generate_c_code(statements)

            if self.debug:
                print("Generated C code preview:")
                print(c_code[:1000] + "..." if len(c_code) > 1000 else c_code)

            # Build executable
            print("🔨 Step 3: Building executable...")
            success = self.build_executable(c_code, output_file)

            if success:
                print(f"✅ Compilation successful: {output_file}")
                os.chmod(output_file, 0o755)
                return CompilerResult(success=True, executable_path=output_file)
            else:
                return CompilerResult(
                    success=False, error_message="C compilation failed"
                )

        except (ValueError, RuntimeError) as e:
            return CompilerResult(
                success=False, error_message=f"Compilation failed: {str(e)}"
            )

    def build_executable(self, c_code: str, output_file: str) -> bool:
        """Compile C code to executable"""
        try:
            # Create temporary C file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
                f.write(c_code)
                c_file = f.name

            try:
                # Compile with gcc
                cmd = ["gcc", "-o", output_file, c_file, "-lm"]

                if self.optimize:
                    cmd.extend(["-O2"])
                else:
                    cmd.extend(["-g"])  # Debug symbols

                result = subprocess.run(
                    cmd, capture_output=True, text=True, check=False
                )

                if result.returncode == 0:
                    print("   C compilation successful")
                    return True
                else:
                    print(f"   C compilation failed: {result.stderr}")
                    return False

            finally:
                # Clean up temporary file
                os.unlink(c_file)

        except (subprocess.SubprocessError, OSError) as e:
            print(f"   Build error: {e}")
            return False

    def print_statements(self, statements: List[Any]):
        """Print statements for debugging"""
        print(f"\n=== {self.language.value.upper()} STATEMENTS ===")
        for i, stmt in enumerate(statements[:20]):  # Limit output
            print(f"{i}: {stmt}")
        if len(statements) > 20:
            print(f"... and {len(statements) - 20} more statements")
        print()
