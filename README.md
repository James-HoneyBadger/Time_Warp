# JAMES IDE - Joint Algorithm Model Environment System

JAMES is a comprehensive educational programming environment designed to support multiple programming languages and provide an intuitive learning experience for students and educators.

## Features

### Multi-Language Support
- **PILOT**: Educational programming language with turtle graphics
- **BASIC**: Classic programming language with line numbers
- **Logo**: Turtle graphics programming language  
- **Python**: Modern scripting language
- **Perl**: Text processing and scripting
- **JavaScript**: Web programming language

### Advanced Theme System
JAMES features 8 beautiful themes with consistent styling across all UI components:

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
   git clone https://github.com/yourusername/JAMES-IDE.git
   cd JAMES-IDE
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run JAMES:
   ```bash
   python JAMES.py
   ```

## Usage

### Getting Started
1. Launch JAMES by running `python JAMES.py`
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
- Configuration stored in `~/.james/config.json`
- Customizable through the preferences system

## Project Structure

```
JAMES-IDE/
├── JAMES.py                 # Main application
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

We welcome contributions to JAMES! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Educational Context

JAMES was designed as an educational tool to help students learn programming concepts across multiple languages. It provides:

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

**JAMES IDE** - Making programming education accessible, visual, and enjoyable for learners of all levels.