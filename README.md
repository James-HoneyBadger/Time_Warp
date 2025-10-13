# Time_Warp IDE

A simple educational programming environment built with Python and Tkinter, supporting multiple programming languages through a unified interpreter.

## Overview

Time_Warp IDE is a minimal but powerful educational tool that allows users to write and execute programs in 9 different programming languages using a single, simple interface. It's designed for learning programming concepts across different paradigms.

## Features

- **Multi-Language Support**: Execute code in PILOT, BASIC, Logo, Pascal, Prolog, Forth, Perl, Python, and JavaScript
- **Simple GUI**: Clean Tkinter interface with text editor and run button
- **Turtle Graphics**: Visual programming support for Logo and PILOT languages
- **Educational Focus**: Clear error messages and immediate execution feedback
- **Keyboard Shortcuts**: F5 or Ctrl+R to run programs

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/James-HoneyBadger/Time_Warp.git
   cd Time_Warp
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the IDE:

   ```bash
   python Time_Warp.py
   ```

## Usage

1. **Launch** the application with `python Time_Warp.py`
2. **Write** your program in the text area
3. **Click "▶ Run Program"** or press **F5** to execute
4. **View results** in the console output

## Supported Languages

### TW PILOT (Educational Language)

```pilot
T:Hello World!
A:What is your name?
T:Nice to meet you, *NAME*!
U:X=10
T:X equals *X*
```

### TW BASIC (Classic Programming)

```basic
10 PRINT "Hello BASIC!"
20 LET X = 5
30 PRINT "X = "; X
40 END
```

### TW Logo (Turtle Graphics)

```logo
FORWARD 100
RIGHT 90
FORWARD 100
RIGHT 90
FORWARD 100
RIGHT 90
FORWARD 100
```

### Python

```python
print("Hello from Python!")
x = 42
print(f"x = {x}")
```

### JavaScript

```javascript
console.log("Hello from JavaScript!");
let x = 42;
console.log(`x = ${x}`);
```

### Perl

```perl
print "Hello from Perl!\n";
my $x = 42;
print "x = $x\n";
```

## Architecture

```
Time_Warp/
├── Time_Warp.py          # Main GUI application
├── core/
│   ├── __init__.py       # Core module exports
│   ├── interpreter.py    # Main interpreter engine
│   ├── languages/        # Language-specific executors
│   │   ├── __init__.py
│   │   ├── pilot.py      # TW PILOT executor
│   │   ├── basic.py      # TW BASIC executor
│   │   ├── logo.py       # TW Logo executor
│   │   └── ...           # Other language executors
│   └── utilities/        # Helper utilities
├── requirements.txt      # Python dependencies
└── scripts/
    └── start.sh          # Launch script
```

## Language Details

### TW PILOT

- **Purpose**: Educational programming with simple commands
- **Commands**: T: (text), A: (input), J: (jump), Y: (yes branch), N: (no branch), U: (update variable)
- **Features**: Variable interpolation with `*VAR*` syntax, turtle graphics integration

### TW BASIC

- **Purpose**: Classic line-numbered programming
- **Commands**: PRINT, LET, GOTO, IF...THEN, FOR...NEXT, INPUT
- **Features**: Traditional BASIC syntax with modern enhancements

### TW Logo

- **Purpose**: Educational turtle graphics programming
- **Commands**: FORWARD, BACK, LEFT, RIGHT, PENUP, PENDOWN, REPEAT
- **Features**: Visual programming with turtle graphics

### Modern Languages (Perl, Python, JavaScript)

- **Purpose**: Full scripting language support
- **Execution**: Direct execution with proper error handling
- **Features**: Access to standard libraries and modern language features

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Adding a New Language

1. Create executor class in `core/languages/newlang.py`
2. Implement `execute_command()` method
3. Add import to `core/languages/__init__.py`
4. Register in `interpreter.py` language mapping

### Code Style

- Use descriptive docstrings for all classes and methods
- Follow PEP 8 style guidelines
- Include type hints where helpful
- Write clear, educational error messages

## Requirements

- Python 3.8+
- Tkinter (usually included with Python)
- PIL/Pillow (optional, for image features)

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please:

1. Test your changes
2. Update documentation
3. Follow existing code style
4. Add examples for new features
