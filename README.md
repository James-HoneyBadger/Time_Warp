# ⏰ TimeWarp Compiler

**Compile Educational Programming Languages to Native Executables**

TimeWarp Compiler is a command-line tool that compiles educational programming languages (PILOT, BASIC, Logo) to native Linux executables. Transform your educational code into standalone programs that run without interpreters.

[![PyPI version](https://badge.fury.io/py/timewarp-ide.svg)](https://pypi.org/project/timewarp-ide/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

### 🎯 Multi-Language Compilation
Compile 3 educational programming languages to native executables:

- **PILOT** - Educational language with turtle graphics (1960s)
- **BASIC** - Classic line-numbered programming (1960s)
- **Logo** - Educational turtle graphics language (1960s)

### 🚀 Native Performance
- **GCC Compilation** - Generate optimized C code and compile to native executables
- **Cross-Platform** - Linux executables (easily extensible to other platforms)
- **No Runtime Dependencies** - Standalone binaries that run anywhere

### 📚 Rich Sample Programs
Comprehensive examples demonstrating language features:
- **BASIC**: Hello world, arrays, functions, loops
- **Logo**: Shapes, complex drawings, fractals
- **PILOT**: Math quizzes, interactive adventures

## 🚀 Quick Start

### Installation

#### Option 1: PyPI (Recommended)
```bash
pip install timewarp-ide
```

#### Option 2: From Source
```bash
git clone https://github.com/TimeWarpIDE/TimeWarp.git
cd Time_Warp
pip install -e .
```

### System Requirements
- **Python**: 3.9 or higher
- **GCC**: GNU C Compiler (build dependency)
- **OS**: Linux (executables), macOS/Windows (compilation)

## 📖 Usage

### Basic Compilation
```bash
# Compile a BASIC program
timewarp-compiler hello.bas -o hello

# Compile a Logo program
timewarp-compiler drawing.logo -o logo_app

# Compile a PILOT program
timewarp-compiler quiz.pilot -o math_quiz
```

### Command Line Options
```bash
timewarp-compiler [OPTIONS] INPUT_FILE

Options:
  -o, --output OUTPUT    Output executable name (default: same as input)
  --list-languages       List supported languages and exit
  --version              Show version information
  -h, --help             Show help message
```

### Supported File Extensions
- `.bas` - BASIC programs
- `.logo` - Logo programs
- `.pilot` - PILOT programs

## 📚 Sample Programs

### BASIC Examples

#### Hello World
```basic
10 PRINT "HELLO WORLD BASIC PROGRAM"
20 PRINT "This demonstrates basic BASIC features"
30 LET ANSWER = 21 * 2
40 PRINT "The answer is: "; ANSWER
50 INPUT "Enter your name"; NAME$
60 PRINT "Hello, "; NAME$
70 PRINT "Counting from 1 to 5:"
80 FOR I = 1 TO 5
90 PRINT I
100 NEXT I
110 PRINT "Done!"
120 END
```

#### Array Operations
```basic
10 DIM SCORES(10)
20 FOR I = 1 TO 10
30 SCORES(I) = I * 10
40 NEXT I
50 PRINT "Scores:"
60 FOR I = 1 TO 10
70 PRINT "Score"; I; ": "; SCORES(I)
80 NEXT I
90 END
```

### Logo Examples

#### Simple Shapes
```logo
TO SQUARE :SIZE
  REPEAT 4 [FORWARD :SIZE RIGHT 90]
END

TO TRIANGLE :SIZE
  REPEAT 3 [FORWARD :SIZE RIGHT 120]
END

TO CIRCLE :RADIUS
  REPEAT 36 [FORWARD (2 * 3.14159 * :RADIUS / 36) RIGHT 10]
END

SQUARE 100
TRIANGLE 80
CIRCLE 50
```

#### Fractal Tree
```logo
TO TREE :SIZE
  IF :SIZE < 5 [STOP]
  FORWARD :SIZE
  RIGHT 25
  TREE :SIZE * 0.7
  LEFT 50
  TREE :SIZE * 0.7
  RIGHT 25
  BACK :SIZE
END

TREE 100
```

### PILOT Examples

#### Math Quiz
```pilot
R: PILOT Math Quiz
R: Test your arithmetic skills

*START
T: Welcome to the Math Quiz!
T: Answer the following questions:

T: What is 5 + 3?
A: Your answer
C: #CORRECT = 8
J: (#ANS = #CORRECT) *CORRECT
T: Sorry, 5 + 3 = 8
J: *NEXT

*CORRECT
T: Correct! 5 + 3 = 8

*NEXT
T: What is 10 - 4?
A: Your answer
C: #CORRECT = 6
J: (#ANS = #CORRECT) *CORRECT2
T: Sorry, 10 - 4 = 6
J: *END

*CORRECT2
T: Excellent! 10 - 4 = 6

*END
T: Quiz complete!
E:
```

#### Interactive Story
```pilot
R: Choose Your Own Adventure

*BEGIN
T: You find yourself in a dark forest.
T: Do you go LEFT or RIGHT?

A: Your choice (LEFT/RIGHT)
J: (*ANS = LEFT) *LEFT_PATH
J: (*ANS = RIGHT) *RIGHT_PATH
T: Please choose LEFT or RIGHT
J: *BEGIN

*LEFT_PATH
T: You find a treasure chest!
T: Congratulations!
E:

*RIGHT_PATH
T: You encounter a dragon!
T: Game Over!
E:
```

## 🏗️ Architecture

### Compilation Pipeline
1. **Parse Source** - Language-specific parsing of source code
2. **Generate C Code** - Convert to optimized C with runtime libraries
3. **Compile Executable** - GCC compilation to native binary
4. **Standalone Binary** - No external dependencies required

### Language Compilers
- **BaseCompiler** - Abstract framework for language implementations
- **BasicCompiler** - Line-numbered BASIC with arrays and functions
- **LogoCompiler** - Turtle graphics with procedures and recursion
- **PilotCompiler** - Educational language with branching and variables

### Runtime Libraries
Each language includes optimized C runtime libraries for:
- String manipulation and I/O
- Mathematical operations
- Turtle graphics rendering (PPM format)
- Variable management and scope

## 📚 Documentation

### Language References
- [BASIC Language Reference](docs/languages/basic.md)
- [Logo Language Reference](docs/languages/logo.md)
- [PILOT Language Reference](docs/languages/pilot.md)

### Compiler Documentation
- [Compiler Usage Guide](docs/compiler.md)

## 🔧 Development

### Building from Source
```bash
# Clone repository
git clone https://github.com/TimeWarpIDE/TimeWarp.git
cd Time_Warp

# Install in development mode
pip install -e .

# Run tests
python -m pytest

# Build package
python -m build
```

### Testing Compilers
```bash
# Test all compilers
python -m pytest tests/

# Test specific language
python -c "from timewarp_ide.compiler import compile_file; compile_file('samples/basic/hello.bas', 'test_output')"
```

### Adding New Languages
1. Create compiler class inheriting from `BaseCompiler`
2. Implement `parse_source()` and `generate_c_code()` methods
3. Add file extension mapping in `compiler.py`
4. Include runtime library functions
5. Add comprehensive tests

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md).

### Areas for Contribution
- **New Languages** - Add support for additional educational languages
- **Performance** - Optimize compilation and runtime performance
- **Platforms** - Extend support to Windows/macOS executables
- **Features** - Enhanced language features and capabilities
- **Documentation** - Improve guides and examples

## 📄 License

TimeWarp Compiler is open source software licensed under the MIT License. See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- **PILOT**: Inspired by the original educational programming language
- **BASIC**: Based on classic BASIC implementations
- **Logo**: Built on the turtle graphics paradigm
- **GCC**: For the excellent C compilation toolchain
- **Python Community**: For the robust packaging ecosystem

---

**⏰ TimeWarp Compiler** - Transform educational code into native executables.