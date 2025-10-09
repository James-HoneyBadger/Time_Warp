#!/usr/bin/env python3
"""
TimeWarp Compiler - Command Line Interface
==========================================

Command line interface for compiling TimeWarp programs to native executables.
"""

import sys
import os
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def main():
    """Main entry point for the compiler CLI"""
    parser = argparse.ArgumentParser(
        description="TimeWarp Compiler - Compile educational programs to native executables",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  timewarp-compiler program.bas -o myprogram    # Compile BASIC program
  timewarp-compiler drawing.logo -o logo_app    # Compile Logo program
  timewarp-compiler lesson.pilot -o quiz        # Compile PILOT program

Supported languages:
  .bas    - BASIC programming language
  .logo   - Logo turtle graphics
  .pilot  - PILOT educational language
        """
    )

    parser.add_argument(
        'input_file',
        help='Source file to compile (.bas, .logo, .pilot)'
    )

    parser.add_argument(
        '-o', '--output',
        help='Output executable name (default: same as input file)'
    )

    parser.add_argument(
        '--list-languages',
        action='store_true',
        help='List supported languages and exit'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='TimeWarp Compiler 1.0.0'
    )

    args = parser.parse_args()

    if args.list_languages:
        print("TimeWarp Compiler - Supported Languages:")
        print("  .bas   - BASIC programming language")
        print("  .logo  - Logo turtle graphics")
        print("  .pilot - PILOT educational language")
        return

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file '{args.input_file}' not found")
        sys.exit(1)

    # Determine output name
    if args.output:
        output_name = args.output
    else:
        output_name = input_path.stem

    # Determine language from file extension
    ext = input_path.suffix.lower()
    if ext == '.bas':
        from compilers.basic_compiler import BasicCompiler
        compiler = BasicCompiler()
    elif ext == '.logo':
        from compilers.logo_compiler import LogoCompiler
        compiler = LogoCompiler()
    elif ext == '.pilot':
        from compilers.pilot_compiler import PilotCompiler
        compiler = PilotCompiler()
    else:
        print(f"Error: Unsupported file extension '{ext}'")
        print("Supported extensions: .bas, .logo, .pilot")
        sys.exit(1)

    try:
        # Read source file
        with open(input_path, 'r', encoding='utf-8') as f:
            source = f.read()

        # Compile to executable
        print(f"Compiling {args.input_file} to executable '{output_name}'...")
        result = compiler.compile_source(source, output_name)

        if result.success:
            print("✅ Compilation successful!")
            print(f"   Executable: {result.executable_path}")
            print(f"   Run with: ./{output_name}")
        else:
            print("❌ Compilation failed!")
            if result.error_message:
                print(f"   Error: {result.error_message}")
            sys.exit(1)

    except (ImportError, FileNotFoundError, OSError) as e:
        print(f"❌ Compilation failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()