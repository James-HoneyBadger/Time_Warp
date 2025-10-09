# ⏰ IDE Time Warp - Journey Through Code

IDE Time Warp is a revolutionary time-traveling programming environment that lets you journey through different coding eras while supporting multiple programming languages across time and space.

## Features

### Multi-Language Support
- **PILOT**: Educational programming language with turtle graphics
- **BASIC**: Classic programming language with line numbers
- **Logo**: Turtle graphics programming language  
- **Python**: Modern scripting language
- **Perl**: Text processing and scripting
- **JavaScript**: Web programming language

### Time Era Theme System
IDE Time Warp features 8 stunning time era themes that transport you through coding history:

**Dark Themes:**
- **Dracula**: Purple and pink accents on dark background
- **Monokai**: Vibrant colors on charcoal background
- **Solarized Dark**: Easy on the eyes with balanced contrast
- **Ocean**: Cool blues and teals on dark navy

**Light Themes:**
- **Spring**: Fresh greens and soft colors
- **Sunset**: Warm oranges and gentle pastels
- **Candy**: Playful pinks and purples
- **Forest**: Natural greens and earth tones

### User Interface
- **Clean Design**: Streamlined interface without visual clutter
- **Persistent Settings**: Theme preferences saved between sessions
- **Consistent Theming**: Colors applied uniformly across menus, panels, and components
- **Three-Panel Layout**: Code editor, output display, and turtle graphics canvas

### Educational Features
- **Real-time Execution**: Immediate feedback for learning
- **Turtle Graphics**: Visual programming with Logo and PILOT
- **Syntax Highlighting**: Language-appropriate code coloring
- **Error Handling**: Clear error messages for debugging
- **File Management**: Save and load programs easily

## Installation

### Prerequisites
- Python 3.7 or higher
- tkinter (usually included with Python)

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/TimeWarp-IDE.git
   cd TimeWarp-IDE
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Launch Time Warp:
   ```bash
   python TimeWarp.py
   ```

## Usage

### Getting Started
1. Launch Time Warp by running `python TimeWarp.py`
2. Select your preferred programming language from the Language menu
3. Choose a theme from the Theme menu
4. Start coding in the editor panel
5. Use Run → Execute to run your programs

### Language-Specific Features

#### PILOT Programming
- Turtle graphics commands: `FORWARD`, `RIGHT`, `LEFT`
- Control structures: `IF`, `WHILE`, `FOR`
- Variables and expressions
- File I/O operations

#### BASIC Programming
- Line numbers required
- Commands: `PRINT`, `INPUT`, `LET`, `GOTO`, `IF...THEN`
- Support for variables and expressions
- Classic BASIC syntax

#### Logo Programming
- Turtle graphics: `FORWARD`, `BACK`, `LEFT`, `RIGHT`
- Procedures and functions
- Recursion support
- Mathematical operations

### File Operations
- **New**: Start a fresh program
- **Open**: Load existing code files
- **Save**: Save your current work
- **Save As**: Save with a new filename

### Customization
- Themes are automatically saved and restored between sessions
- Configuration stored in `~/.timewarp/config.json`
- Customizable through the preferences system

## Project Structure

```
TimeWarp-IDE/
├── TimeWarp.py              # Main time-traveling application
├── tools/
│   ├── theme.py            # Theme management system
│   ├── pilot_interpreter.py # PILOT language interpreter
│   ├── basic_interpreter.py # BASIC language interpreter
│   ├── logo_interpreter.py  # Logo language interpreter
│   └── js_interpreter.py    # JavaScript interpreter
├── demo/                   # Example programs
├── docs/                   # Documentation
└── README.md              # This file
```

## Contributing

We welcome contributions to IDE Time Warp! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Educational Context

IDE Time Warp was designed as a revolutionary time-traveling tool to help students journey through programming concepts across multiple languages and eras. It provides:

- **Visual Feedback**: Turtle graphics make programming concepts tangible
- **Multi-Language Learning**: Compare syntax and concepts across languages
- **Immediate Results**: See code execution in real-time
- **Clean Interface**: Focus on learning without distractions

## Technical Details

### Architecture
- Built with Python and tkinter for cross-platform compatibility
- Modular interpreter design for easy language addition
- JSON-based configuration system
- Event-driven UI with consistent theming

### Performance
- Lightweight and fast startup
- Real-time syntax processing
- Efficient turtle graphics rendering
- Minimal resource usage

## License

This project is open source and available under the MIT License.

## Support

For questions, issues, or contributions, please visit our GitHub repository or contact the development team.

---

**⏰ IDE Time Warp** - Making programming education a time-traveling adventure across coding eras for learners of all levels.