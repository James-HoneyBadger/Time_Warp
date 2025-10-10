# ⏰ TimeWarp IDE

**A Multi-Language Educational Programming Environment**

TimeWarp IDE is a comprehensive educational programming environment that supports multiple classic and modern programming languages. Featuring an intuitive GUI interface, turtle graphics, interactive code execution, theme system, plugin architecture, and educational tools designed to make programming accessible and engaging.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macOS%20%7C%20windows-lightgrey)](https://github.com/TimeWarpIDE/TimeWarp)

## ✨ Features

### 🎯 Multi-Language Support
TimeWarp IDE supports six programming languages in one integrated environment:

- **PILOT** (1962) - Educational language with branching logic and turtle graphics
- **BASIC** (1964) - Classic line-numbered programming with variables and loops  
- **Logo** (1967) - Turtle graphics programming with procedures and recursion
- **Python** (1991) - Modern high-level programming with full library support
- **JavaScript** (1995) - Web scripting language with dynamic features
- **Perl** (1987) - Text processing and system administration language

### 🖥️ Integrated Development Environment
- **Rich Text Editor** - Syntax highlighting, auto-completion, and code formatting
- **Interactive Canvas** - Real-time turtle graphics and visual programming output
- **Immediate Execution** - Run code instantly without compilation delays
- **Multi-Pane Interface** - Code editor, output console, and graphics canvas
- **File Management** - Open, save, and organize programs with proper file associations

### 🎨 Customization & Themes
- **8 Built-in Themes** - Dark and light themes optimized for different preferences
  - Dark themes: Dracula, Monokai, Solarized Dark, Ocean
  - Light themes: Spring, Sunset, Candy, Forest
- **Persistent Settings** - Theme preferences saved between sessions
- **Visual Polish** - Consistent styling across all UI components

### 🧩 Plugin Architecture
- **Extensible Framework** - Add custom functionality through plugins
- **Built-in Plugins** - Code formatter, syntax highlighter, and development tools
- **Plugin Manager** - Easy installation and management of extensions
- **Sample Plugins** - Complete examples for plugin development

### 🎮 Educational Features
- **Tutorial System** - Interactive learning modules for each language
- **AI Assistant** - Context-aware programming help and suggestions
- **Gamification** - Achievement system and progress tracking
- **Hardware Simulation** - Raspberry Pi GPIO simulation for IoT learning
- **Audio Feedback** - Sound effects and music integration

### 🔧 Advanced Capabilities
- **Performance Monitoring** - Built-in benchmarking and profiling tools
- **Collaboration Tools** - Share projects and code snippets
- **Version Control** - Git integration for project management
- **Cross-Platform** - Runs on Linux, macOS, and Windows
- **No Dependencies** - Self-contained installation with all required libraries

## 🚀 Quick Start

### System Requirements
- **Python**: 3.9 or higher
- **Operating System**: Linux, macOS, or Windows
- **Memory**: 512MB RAM minimum, 1GB recommended
- **Storage**: 100MB free disk space

### Installation

#### Option 1: Quick Install (Recommended)
```bash
git clone https://github.com/TimeWarpIDE/TimeWarp.git
cd TimeWarp
python TimeWarp.py
```

#### Option 2: Development Setup
```bash
git clone https://github.com/TimeWarpIDE/TimeWarp.git
cd TimeWarp
pip install -r requirements.txt
python TimeWarp.py
```

#### Option 3: Virtual Environment
```bash
git clone https://github.com/TimeWarpIDE/TimeWarp.git
cd TimeWarp
python -m venv timewarp_env
source timewarp_env/bin/activate  # On Windows: timewarp_env\\Scripts\\activate
pip install -r requirements.txt
python TimeWarp.py
```

### First Launch
1. Run `python TimeWarp.py`
2. Choose your preferred theme from the Theme menu
3. Select a programming language from the Language menu
4. Start coding in the editor pane
5. Click "Run" to execute your program
6. View output in the console and graphics on the canvas

## 💻 Programming Languages

### PILOT Language
Educational programming language designed for interactive learning:

```pilot
T: Welcome to PILOT programming!
T: What is your name?
A: #NAME
T: Hello, #NAME! Let's do some math.
T: What is 5 + 3?
A: #ANSWER
M: #ANSWER = 8
J: *CORRECT
T: Try again!
J: *END

*CORRECT
T: Excellent! You got it right.

*END
T: Thanks for trying PILOT!
```

### BASIC Language
Classic programming with line numbers and structured flow:

```basic
10 PRINT "Welcome to BASIC programming!"
20 INPUT "Enter your name: "; NAME$
30 PRINT "Hello, "; NAME$
40 FOR I = 1 TO 5
50   PRINT "Counting: "; I
60 NEXT I
70 PRINT "Program complete!"
80 END
```

### Logo Language  
Turtle graphics programming with procedures:

```logo
TO SQUARE :SIZE
  REPEAT 4 [FORWARD :SIZE RIGHT 90]
END

TO FLOWER
  REPEAT 8 [
    SQUARE 50
    RIGHT 45
  ]
END

CLEARSCREEN
FLOWER
```

### Python Integration
Full Python language support with TimeWarp IDE integration:

```python
import math
import random

# TimeWarp IDE provides turtle graphics
print("Python in TimeWarp IDE!")

# Generate random numbers
for i in range(5):
    num = random.randint(1, 100)
    sqrt_num = math.sqrt(num)
    print(f"√{num} = {sqrt_num:.2f}")
```

### JavaScript Support
Modern JavaScript execution with console output:

```javascript
console.log("JavaScript in TimeWarp IDE!");

// Array manipulation
const numbers = [1, 2, 3, 4, 5];
const squared = numbers.map(n => n * n);
console.log("Original:", numbers);
console.log("Squared:", squared);

// Object-oriented programming
class Student {
    constructor(name, grade) {
        this.name = name;
        this.grade = grade;
    }
    
    introduce() {
        console.log(`Hi, I'm ${this.name} in grade ${this.grade}`);
    }
}

const student = new Student("Alice", 10);
student.introduce();
```

### Perl Language
Text processing and system scripting:

```perl
#!/usr/bin/perl
use strict;
use warnings;

print "Perl in TimeWarp IDE!\n";

# Text processing example
my $text = "Hello, World!";
$text =~ s/World/TimeWarp/;
print "$text\n";

# Array operations
my @numbers = (1, 2, 3, 4, 5);
my @doubled = map { $_ * 2 } @numbers;
print "Doubled: " . join(", ", @doubled) . "\n";
```

## 🏗️ Architecture

### Core Components

#### TimeWarp Interpreter (`core/interpreter.py`)
- Central execution engine that dispatches commands to language-specific executors
- Manages program state, variables, and execution context
- Provides unified interface for all supported languages
- Handles turtle graphics, audio, and hardware simulation

#### Language Executors (`core/languages/`)
- **PilotExecutor** - PILOT language implementation with branching logic
- **BasicExecutor** - BASIC language with line numbers and traditional commands
- **LogoExecutor** - Logo turtle graphics with procedures and functions
- **PythonExecutor** - Python integration with full standard library
- **JavaScriptExecutor** - JavaScript execution environment
- **PerlExecutor** - Perl scripting and text processing

#### GUI Framework (`gui/`)
- **Main Interface** - Primary application window with menu system
- **Code Editor** - Syntax-highlighted text editor with auto-completion
- **Canvas System** - Turtle graphics rendering and display
- **Component Library** - Reusable UI elements and dialogs

#### Plugin System (`plugins/`)
- **Plugin Manager** - Dynamic loading and management of extensions
- **Base Framework** - Abstract classes for plugin development
- **Sample Plugins** - Examples including code formatter and syntax highlighter

### Directory Structure

```
TimeWarp/
├── core/                   # Core interpreter and language engines
├── gui/                    # User interface components  
├── plugins/                # Plugin system and extensions
├── tools/                  # Development and utility tools
├── games/                  # Game engine and examples
├── examples/               # Sample programs for all languages
├── docs/                   # Comprehensive documentation
├── testing/                # Test suite and quality assurance
├── marketing/              # Promotional materials and outreach
└── TimeWarp.py            # Main application entry point
```

## 📚 Documentation

### User Guides
- [Getting Started Guide](docs/getting-started.md) - First steps with TimeWarp IDE
- [PILOT Language Reference](docs/languages/pilot.md) - Complete PILOT documentation
- [BASIC Language Reference](docs/languages/basic.md) - BASIC programming guide
- [Logo Language Reference](docs/languages/logo.md) - Logo turtle graphics manual

### Developer Documentation
- [Architecture Overview](docs/MODULAR_ARCHITECTURE.md) - System design and structure
- [Plugin Development](docs/plugin-development.md) - Creating custom extensions
- [Contributing Guide](CONTRIBUTING.md) - How to contribute to the project
- [API Reference](docs/api-reference.md) - Complete API documentation

### Educational Resources
- [Teaching with TimeWarp](docs/education/teaching-guide.md) - Classroom integration
- [Curriculum Integration](docs/education/curriculum.md) - Lesson plans and activities
- [Student Projects](docs/education/projects.md) - Example assignments and exercises

## 🎓 Educational Use

TimeWarp IDE is designed specifically for educational environments:

### Classroom Features
- **Multi-Language Learning** - Introduce programming concepts across different languages
- **Visual Programming** - Turtle graphics make abstract concepts concrete
- **Immediate Feedback** - See results instantly without compilation delays
- **Progressive Complexity** - Start with PILOT/BASIC, advance to Python/JavaScript
- **Cross-Curricular** - Integrate math, art, and logic through programming

### Age-Appropriate Progression
1. **Elementary (Ages 8-11)**: Logo turtle graphics and simple PILOT programs
2. **Middle School (Ages 12-14)**: BASIC programming with variables and loops
3. **High School (Ages 15-18)**: Python and JavaScript for real-world applications
4. **Advanced/College**: Full language features, plugins, and project development

### Assessment Tools
- **Progress Tracking** - Built-in gamification system tracks student achievement
- **Code Analysis** - Automatic feedback on code quality and style
- **Project Portfolio** - Save and organize student work over time
- **Collaboration** - Share projects and learn from peers

## 🔧 Development

### Building from Source
```bash
# Clone the repository
git clone https://github.com/TimeWarpIDE/TimeWarp.git
cd TimeWarp

# Install development dependencies
pip install -r requirements.txt

# Run the application
python TimeWarp.py

# Run tests
python -m pytest testing/

# Generate documentation
python -m sphinx docs/ docs/_build/
```

### Testing
```bash
# Run all tests
python run_tests.py

# Run specific test categories
python -m pytest testing/tests/test_interpreters.py  # Language tests
python -m pytest testing/tests/test_gui_components.py  # GUI tests
python -m pytest testing/tests/test_plugins.py  # Plugin tests

# Performance benchmarking
python tools/benchmark_timewarp.py

# Integration testing
python scripts/integration_tests.py
```

### Contributing

We welcome contributions from educators, students, and developers! Areas where you can help:

- **Language Support** - Add new programming languages
- **Educational Content** - Create tutorials, examples, and lesson plans
- **Plugin Development** - Build extensions for specialized use cases
- **Documentation** - Improve guides, references, and help content
- **Testing** - Expand test coverage and quality assurance
- **Localization** - Translate the interface to other languages

See our [Contributing Guide](CONTRIBUTING.md) for detailed information.

## 🌟 Community

### Getting Help
- **GitHub Issues** - Report bugs and request features
- **Discussions** - Ask questions and share ideas
- **Discord Server** - Real-time chat with other users
- **Educational Forum** - Teaching strategies and classroom experiences

### Showcase
- **Student Projects** - Share creative programs and artwork
- **Classroom Success Stories** - How teachers use TimeWarp IDE
- **Plugin Gallery** - Community-developed extensions
- **Language Examples** - Advanced programming demonstrations

## 📄 License

TimeWarp IDE is open source software licensed under the MIT License. See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- **Educational Programming Pioneer Languages** - PILOT, BASIC, Logo, and their creators
- **Python Community** - For the robust ecosystem and libraries
- **Tkinter** - GUI framework that makes TimeWarp IDE possible
- **Open Source Contributors** - Everyone who has contributed to this project
- **Educators Worldwide** - Teachers who inspire the next generation of programmers

---

**⏰ TimeWarp IDE** - Where classic programming languages meet modern educational technology.

*Journey through the history of programming while building skills for the future.*