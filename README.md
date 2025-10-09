# ⏰ TimeWarp IDE

**A Revolutionary Multi-Language Educational Programming Environment**

TimeWarp IDE is a comprehensive educational programming environment that supports multiple programming languages across different eras of computing history. Designed for learners, educators, and developers, it provides an intuitive interface for exploring programming concepts through time.

[![PyPI version](https://badge.fury.io/py/timewarp-ide.svg)](https://pypi.org/project/timewarp-ide/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI/CD](https://github.com/James-HoneyBadger/Time_Warp/actions/workflows/ci.yml/badge.svg)](https://github.com/James-HoneyBadger/Time_Warp/actions)

## ✨ Features

### 🎯 Multi-Language Support
TimeWarp IDE supports 6 programming languages, each representing different eras and paradigms:

- **PILOT** - Educational language with turtle graphics (1960s)
- **BASIC** - Classic line-numbered programming (1960s)
- **Logo** - Educational turtle graphics language (1960s)
- **Python** - Modern scripting language (1990s)
- **JavaScript** - Web programming language (1990s)
- **Perl** - Text processing powerhouse (1980s)

### 🎨 Immersive Theme System
8 beautifully crafted themes that transport you through computing eras:

**Dark Themes:**
- **Dracula** - Gothic purple and pink
- **Monokai** - Vibrant coding colors
- **Solarized Dark** - Eye-friendly contrast
- **Ocean** - Cool blue depths

**Light Themes:**
- **Spring** - Fresh and vibrant
- **Sunset** - Warm and inviting
- **Candy** - Playful and sweet
- **Forest** - Natural and calming

### 🚀 Advanced Features

- **Real-time Execution** - Immediate feedback as you code
- **Turtle Graphics** - Visual programming with PILOT and Logo
- **Syntax Highlighting** - Language-appropriate code coloring
- **Intelligent Code Completion** - Context-aware suggestions
- **Interactive Debugging** - Step-through execution
- **File Management** - Save, load, and organize projects
- **Plugin System** - Extensible architecture
- **Performance Profiling** - Code optimization tools
- **Gamification** - Achievement system and progress tracking
- **AI Assistant** - Intelligent code help and suggestions

### 📚 Educational Tools

- **Tutorial System** - Guided learning paths
- **Code Analysis** - Quality and style feedback
- **Progress Tracking** - Learning milestones
- **Interactive Examples** - Hands-on demonstrations
- **Comprehensive Documentation** - In-depth language guides

## 🚀 Quick Start

### Installation

#### Option 1: PyPI (Recommended)
```bash
pip install timewarp-ide
timewarp-ide
```

#### Option 2: From Source
```bash
git clone https://github.com/James-HoneyBadger/Time_Warp.git
cd Time_Warp
pip install -r requirements.txt
python TimeWarp.py
```

### System Requirements
- **Python**: 3.9 or higher
- **OS**: Windows, macOS, Linux
- **Display**: GUI support (tkinter included with Python)
- **Memory**: 256MB RAM minimum
- **Storage**: 50MB free space

## 📖 User Guide

### Getting Started

1. **Launch TimeWarp IDE**
   ```bash
   timewarp-ide
   # or
   python TimeWarp.py
   ```

2. **Select a Language**
   - Use the Language menu or toolbar dropdown
   - Each language has unique syntax and capabilities

3. **Choose a Theme**
   - Access through View → Themes
   - Settings persist between sessions

4. **Start Coding**
   - Type in the editor panel
   - Use Run → Execute to run your code
   - View output in the console panel
   - See graphics in the turtle canvas

### Language Tutorials

#### PILOT Programming
PILOT (Programmed Inquiry, Learning Or Teaching) is an educational language designed for interactive learning.

**Basic Syntax:**
```
T: Hello, World!
A: What is your name?
T: Nice to meet you, *NAME*
J: *START
```

**Turtle Graphics:**
```
T: Drawing a square
FORWARD 100
RIGHT 90
FORWARD 100
RIGHT 90
FORWARD 100
RIGHT 90
FORWARD 100
RIGHT 90
```

#### BASIC Programming
Classic BASIC with line numbers and simple syntax.

**Basic Program:**
```
10 PRINT "Hello, World!"
20 INPUT "What is your name"; NAME$
30 PRINT "Nice to meet you, "; NAME$
40 END
```

**Graphics Example:**
```
10 SCREEN 12
20 CIRCLE (320, 240), 100, 15
30 PAINT (320, 240), 15
40 SLEEP 2000
```

#### Logo Programming
Turtle graphics with procedural programming.

**Basic Movement:**
```
FORWARD 100
RIGHT 90
FORWARD 100
RIGHT 90
FORWARD 100
RIGHT 90
FORWARD 100
```

**Procedures:**
```
TO SQUARE :SIZE
  REPEAT 4 [FORWARD :SIZE RIGHT 90]
END

SQUARE 100
```

### Advanced Features

#### Code Completion
- Press `Ctrl+Space` for intelligent suggestions
- Context-aware completions for each language
- Variable and function name suggestions

#### Debugging
- Set breakpoints with `F9`
- Step through code with `F10`
- Inspect variables in the debug panel

#### Plugins
- Access through Tools menu
- Learning Assistant for educational help
- Code Analysis for quality feedback
- Performance Profiler for optimization

## 📚 Sample Programs

### PILOT Examples

#### Calculator Program
```
R: PILOT Calculator Program
R: Demonstrates arithmetic operations

*START
T: Welcome to PILOT Calculator!
T: Enter two numbers to add

A: First number
C: #NUM1 = *ANS

A: Second number
C: #NUM2 = *ANS

C: #RESULT = #NUM1 + #NUM2
T: Result: #RESULT

J: *START
```

#### Interactive Story
```
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

### BASIC Examples

#### Number Guessing Game
```
10 PRINT "Number Guessing Game"
20 PRINT "I'm thinking of a number between 1 and 100"
30 SECRET = INT(RND(1) * 100) + 1
40 GUESSES = 0
50 INPUT "Your guess"; GUESS
60 GUESSES = GUESSES + 1
70 IF GUESS = SECRET THEN GOTO 100
80 IF GUESS < SECRET THEN PRINT "Too low!"
90 IF GUESS > SECRET THEN PRINT "Too high!"
95 GOTO 50
100 PRINT "Correct! You took"; GUESSES; "guesses"
110 END
```

#### Graphics Demo
```
10 SCREEN 12
20 CLS
30 PRINT "BASIC Graphics Demo"
40 CIRCLE (320, 240), 50, 15
50 PAINT (320, 240), 15
60 FOR I = 1 TO 10
70   CIRCLE (320 + I * 20, 240), 30, I + 1
80 NEXT I
90 SLEEP 3000
100 END
```

### Logo Examples

#### Fractal Tree
```
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

#### Color Spiral
```
TO SPIRAL :SIZE :ANGLE
  IF :SIZE > 200 [STOP]
  SETPENCOLOR :SIZE / 2
  FORWARD :SIZE
  RIGHT :ANGLE
  SPIRAL :SIZE + 2 :ANGLE
END

PENUP
SETXY 0 0
PENDOWN
SPIRAL 1 15
```

#### Interactive Drawing
```
TO DRAW
  PENDOWN
  WHILE [TRUE] [
    IF MOUSEPRESSED [
      SETXY MOUSEX MOUSEY
    ]
  ]
END

TO CLEAR
  CLEARSCREEN
  PENUP
  SETXY 0 0
END

DRAW
```

## 🔧 Configuration

### User Settings
TimeWarp IDE stores configuration in:
- **Linux/macOS**: `~/.timewarp/config.json`
- **Windows**: `%APPDATA%\TimeWarp\config.json`

### Customization Options
```json
{
  "theme": "dracula",
  "language": "pilot",
  "font_size": 12,
  "auto_save": true,
  "syntax_check": true,
  "code_completion": true
}
```

### Keyboard Shortcuts
- `Ctrl+N` - New file
- `Ctrl+O` - Open file
- `Ctrl+S` - Save file
- `F5` - Run program
- `F9` - Toggle breakpoint
- `F10` - Step debugging
- `Ctrl+Space` - Code completion

## 🏗️ Architecture

### Core Components

```
TimeWarp IDE/
├── core/                    # Core system components
│   ├── interpreter.py      # Main execution engine
│   ├── languages/          # Language-specific interpreters
│   └── framework.py        # Plugin and extension system
├── features/               # Advanced features
│   ├── ai_assistant.py     # AI-powered help
│   ├── gamification.py     # Achievement system
│   └── learning.py         # Educational tools
├── tools/                  # Utility tools
│   ├── theme.py           # Theme management
│   └── plugin_manager.py   # Plugin system
├── gui/                    # User interface
│   ├── editor.py          # Code editor
│   ├── canvas.py          # Graphics display
│   └── menu.py            # Menu system
└── plugins/               # Extensible plugins
    ├── learning_assistant/
    └── sample_plugin/
```

### Language Architecture
Each language implements a consistent interface:

```python
class LanguageInterpreter:
    def execute(self, code: str) -> ExecutionResult
    def validate_syntax(self, code: str) -> List[SyntaxError]
    def get_completions(self, code: str, position: int) -> List[str]
    def debug_step(self, state: DebugState) -> DebugState
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md).

### Development Setup
```bash
git clone https://github.com/James-HoneyBadger/Time_Warp.git
cd Time_Warp
pip install -r requirements.txt
pip install -e .[dev]
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=timewarp_ide --cov-report=html

# Run specific test
pytest tests/test_interpreter.py
```

### Code Quality
```bash
# Format code
black .

# Lint code
flake8 .

# Type checking (future)
# mypy .
```

## 📄 License

TimeWarp IDE is open source software licensed under the MIT License. See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- **PILOT**: Inspired by the original educational programming language
- **BASIC**: Based on classic BASIC implementations
- **Logo**: Built on the turtle graphics paradigm
- **Python Community**: For the excellent ecosystem
- **Open Source Contributors**: For their valuable contributions

## 📞 Support

- **Documentation**: [Full User Guide](docs/)
- **Issues**: [GitHub Issues](https://github.com/James-HoneyBadger/Time_Warp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/James-HoneyBadger/Time_Warp/discussions)
- **Email**: timewarp-ide@example.com

---

**⏰ TimeWarp IDE** - Journey through programming history, one line of code at a time.