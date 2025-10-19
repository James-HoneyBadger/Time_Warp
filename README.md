# Time_Warp IDE

A modern educational programming environment built with Python and Tkinter, featuring a unified canvas interface with GW BASIC screen mode emulation.

## Overview

Time_Warp IDE is a powerful educational tool that allows users to write and execute programs in 7 different programming languages using a unified canvas that supports both text and graphics rendering. It features authentic retro computing aesthetics with GW BASIC screen mode emulation.

## Features

- **Multi-Language Support**: Execute code in Time Warp, Pascal, Prolog, Forth, Perl, Python, and JavaScript
- **Unified Canvas Interface**: Single display surface for text and graphics with GW BASIC screen modes
- **GW BASIC Screen Modes**: Authentic emulation of classic screen modes (0,1,2,7,8,9,10) with proper resolutions and color palettes
- **Retro Computing Aesthetics**: Faithful recreation of classic BASIC computing environments
- **Turtle Graphics**: Visual programming support integrated into unified canvas
- **Keyboard Input Prompts**: Interactive input system built into the canvas
- **Educational Focus**: Clear error messages and immediate execution feedback
- **Theme Support**: Multiple color themes including retro computing palettes

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
2. **Select Screen Mode** from View → Screen Modes menu for different resolutions and color palettes
3. **Write** your program in an external editor (code editing is handled externally in unified canvas mode)
4. **Execute** programs through the interpreter (program execution methods to be implemented)
5. **View results** directly on the unified canvas with proper text/graphics rendering

## Screen Modes

Time_Warp IDE supports all major GW BASIC screen modes:

- **Mode 0**: CGA 40-column Text (320x200, 16 colors)
- **Mode 1**: CGA 40-column Text Alt (320x200, 16 colors)
- **Mode 2**: CGA 80-column Text (640x200, 16 colors)
- **Mode 7**: EGA 320x200 Graphics (320x200, 16 colors)
- **Mode 8**: EGA 640x200 Graphics (640x200, 16 colors)
- **Mode 9**: EGA 640x350 Graphics (640x350, 16 colors)
- **Mode 10**: MDA Monochrome Graphics (720x350, 2 colors)

## Supported Languages

### Time Warp (Unified Educational Language)

```time_warp
T:Hello World!
A:What is your name?
T:Nice to meet you, *NAME*!

LET X = 10
PRINT "X equals *X*"

FORWARD 100
RIGHT 90
REPEAT 4 [FORWARD 100 RIGHT 90]
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
│   │   ├── time_warp.py  # Time Warp unified executor
│   │   └── ...           # Other language executors
│   └── utilities/        # Helper utilities
├── requirements.txt      # Python dependencies
└── scripts/
    └── start.sh          # Launch script
```

## Language Details

### Time Warp

- **Purpose**: Unified educational programming language combining PILOT, BASIC, and Logo features
- **Commands**: T: (text), A: (input), J: (jump), Y: (yes branch), N: (no branch), U: (update variable), PRINT, LET, IF...THEN, FORWARD, RIGHT, LEFT, REPEAT
- **Features**: Variable interpolation with `*VAR*` syntax, turtle graphics integration, modern variable assignment, structured programming

### Modern Languages (Pascal, Prolog, Forth, Perl, Python, JavaScript)

- **Purpose**: Full programming language support for advanced concepts
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
