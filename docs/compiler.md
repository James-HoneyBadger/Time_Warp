# Time_Warp Compiler Documentation

## Overview

The Time_Warp Compiler transforms your educational programming languages into standalone Linux executables. This major enhancement allows you to distribute and run your programs independently of the IDE.

## Supported Languages

The compiler supports all 6 custom educational languages:

- **PILOT** - Educational language with turtle graphics
- **BASIC** - Classic line-numbered programming
- **Logo** - Turtle graphics programming language
- **Pascal** - Structured programming language
- **Prolog** - Logic programming language
- **Forth** - Stack-based programming language

## How It Works

The compiler uses a **C code generation** approach:

1. **Source Code** → Your PILOT/BASIC/Logo/etc. program
2. **C Generator** → Converts to portable C code with custom runtime
3. **GCC/Clang** → Compiles C code to native Linux executable
4. **Standalone Binary** → Runs independently on Linux systems

## Using the Compiler

### Method 1: IDE Menu (Recommended)
1. Open Time_Warp IDE: `python Time_Warp.py`
2. Load or write your program in the code editor
3. Go to **Tools → Compile to Executable...** (Ctrl+Shift+E)
4. Choose output location and filename
5. Click "Compile" to generate the executable

### Method 2: Python API
```python
from core.compiler import Time_WarpCompiler

# Initialize compiler
compiler = Time_WarpCompiler()

# Compile a program
result = compiler.compile_to_executable(
    code="10 PRINT \"Hello World\"\n20 END",
    language="basic",
    output_path="./hello_basic"
)

if result['success']:
    print(f"✅ Compiled successfully: {result['executable']}")
    print(f"Size: {result['size']} bytes")
else:
    print(f"❌ Compilation failed: {result['error']}")
```

## Example Programs

Hello World examples for each language are available in the `examples/` directory:

- `examples/hello_pilot.pilot`
- `examples/hello_basic.bas`
- `examples/hello_logo.logo`
- `examples/hello_pascal.pas`
- `examples/hello_prolog.plg`
- `examples/hello_forth.fs`

## Running Compiled Programs

After compilation, you'll be asked if you want to run the executable immediately. If you choose "Yes", the program will run and its output will be displayed directly in the IDE's Output panel. This makes it easy to see the results without leaving the IDE.

You can also run compiled programs anytime from the command line:
```bash
./program_name
```

### What Happens During Execution

When you run a compiled program through the IDE:
1. The executable launches in the background
2. All output (stdout and stderr) is captured
3. Results are displayed in the IDE's Output panel
4. The Output tab is automatically selected for easy viewing
5. Exit codes and any errors are shown

## Compilation Details

### Generated Executables
- **Platform**: Linux x86_64 (and compatible architectures)
- **Dependencies**: None (statically linked where possible)
- **Size**: Typically 15-20KB for simple programs
- **Permissions**: Automatically set to executable

### Compiler Requirements
- **GCC** or **Clang** compiler must be installed
- **glibc** standard library (standard on Linux)
- **No external dependencies** required at runtime

### Language-Specific Features

#### PILOT
- Full turtle graphics support
- Educational command structure (T:, A:, J:, etc.)
- Simple text-based output

#### BASIC
- Line-numbered program execution
- Standard BASIC commands (PRINT, LET, GOTO, etc.)
- Input/output operations

#### Logo
- Turtle graphics with canvas simulation
- Movement commands (FORWARD, RIGHT, etc.)
- Text-based graphics representation

#### Pascal
- Structured programming constructs
- Variable management (integer, real, string, boolean)
- Standard Pascal I/O

#### Prolog
- Logic programming with facts and rules
- Query processing capabilities
- Knowledge base management

#### Forth
- Stack-based execution model
- Dictionary-based word definitions
- Low-level programming constructs

## Technical Architecture

### C Code Generation
Each language has a dedicated C code generator that creates:
- **Runtime structures** for language-specific data
- **Execution functions** that interpret the source code
- **Memory management** with proper cleanup
- **Portable C code** using standard library functions

### Compilation Pipeline
```
Source Code → Language Parser → C Code Generator → GCC/Clang → Executable
```

### Error Handling
- **Compilation errors** are caught and reported
- **Missing compiler** detection with helpful messages
- **Timeout protection** (60-second limit per compilation)
- **Cross-platform compatibility** checks

## System Requirements

### Minimum Requirements
- Linux operating system
- GCC 4.8+ or Clang 3.5+
- Python 3.6+ (for the IDE)
- 50MB free disk space

### Recommended Setup
- Ubuntu 18.04+ or equivalent
- GCC 9.0+ for best compatibility
- 100MB free disk space for development

## Troubleshooting

### Common Issues

#### "No C compiler found"
**Solution**: Install GCC or Clang
```bash
# Ubuntu/Debian
sudo apt-get install gcc

# CentOS/RHEL
sudo yum install gcc

# Arch Linux
sudo pacman -S gcc
```

#### "Compilation failed: M_PI undeclared"
**Solution**: This should be fixed in the current version. If you encounter it, the Logo compiler needs the math.h header and M_PI definition.

#### "Permission denied" when running executable
**Solution**: The compiler automatically sets executable permissions. If issues persist:
```bash
chmod +x your_executable
```

#### Large executable sizes
**Solution**: This is normal. The runtime includes full language support. Simple programs are typically 15-20KB.

### Testing Compilation
Run the test suite to verify your setup:
```bash
python test_compiler.py
```

This will test compilation of all 6 languages and report any issues.

## Advanced Usage

### Custom Compilation Options
The compiler supports optimization levels and debug builds through the internal API.

### Integration with Build Systems
The compiler can be integrated into Makefiles or other build systems for automated compilation.

### Cross-Compilation
While currently targeting Linux x86_64, the architecture supports cross-compilation to other platforms with appropriate toolchains.

## Future Enhancements

Planned improvements include:
- **Windows support** (MinGW cross-compilation)
- **macOS support** (Clang-based compilation)
- **WebAssembly output** for browser execution
- **Optimization passes** for smaller executables
- **Debug information** embedding
- **Source code embedding** in executables

## Contributing

The compiler system is designed to be extensible. To add support for new languages:

1. Create a new C code generator method in `core/compiler.py`
2. Implement the language runtime structures
3. Add the language to the supported languages list
4. Test compilation and execution

## License

The Time_Warp Compiler is part of the Time_Warp IDE project and follows the same licensing terms.

---

**Ready to compile your first program?** Open Time_Warp IDE, load an example from the `examples/` directory, and select **Tools → Compile to Executable...**!