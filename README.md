<<<<<<< HEAD
# 🚀 Time_Warp IDE v1.2.0 - Stable Release

**Release Date:** October 11, 2025  
**Status:** Stable ✅  
**Previous Releases:** v1.0 and v1.1 removed due to critical bugs

## 🛠️ What's Fixed

This release addresses all critical issues from the previous buggy releases:

### ✅ Code Editor Theme Issue - RESOLVED
- **Problem**: Multi-tab editor wasn't inheriting the main UI theme
- **Solution**: Fixed theme application timing and added explicit theme calls
- **Result**: Code editor now consistently applies your selected theme

### ✅ Turtle Graphics Issue - RESOLVED  
- **Problem**: Logo turtle graphics commands weren't displaying results
- **Solution**: Fixed canvas connection between interpreter and graphics display
- **Result**: Turtle graphics now work perfectly with proper coordinate centering

### ✅ Package Structure - ENHANCED
- **Improvement**: Professional package structure with proper imports
- **Enhancement**: Fixed VS Code debugging integration
- **Result**: Clean development environment and better maintainability

## 🎯 Key Features Verified Working

- ✅ **Multi-Language Support**: BASIC, PILOT, Logo, Python, JavaScript, Perl
- ✅ **Turtle Graphics**: Logo commands draw correctly with proper centering
- ✅ **Multi-Tab Editor**: Professional code editor with syntax highlighting
- ✅ **Theme System**: 8 beautiful themes (4 dark, 4 light) apply consistently
- ✅ **Enhanced Graphics**: Zoom, export, grid overlay for turtle graphics
- ✅ **File Management**: Load, save, and manage multiple code files
- ✅ **VS Code Integration**: Full debugging support with F5 launch

## 🚀 Quick Start

```bash
# Download and run
git clone https://github.com/James-HoneyBadger/Time_Warp.git
cd Time_Warp
python3 timewarp.py
```

## 📋 System Requirements

- **Python**: 3.7 or higher
- **GUI**: tkinter (included with most Python installations)
- **Optional**: PIL/Pillow for enhanced image features
- **Platform**: Windows, macOS, Linux

## 🎮 Try These Examples

### Logo Turtle Graphics
```logo
forward 100
right 90
forward 100
right 90
forward 100
right 90
forward 100
```

### BASIC Programming
```basic
10 PRINT "Hello from Time_Warp!"
20 FOR I = 1 TO 5
30 PRINT "Count: "; I
40 NEXT I
50 END
```

### PILOT Educational Language
```pilot
T: Welcome to Time_Warp IDE!
A: What's your name?
Y: #name
T: Hello, #name! Let's learn programming.
```

## 🔍 What We Tested

- ✅ Theme application across all UI components
- ✅ Turtle graphics coordinate system and display
- ✅ Multi-tab editor functionality and theming
- ✅ All programming language executors
- ✅ File operations and project management
- ✅ VS Code debugging workflow
- ✅ Cross-platform compatibility

## 🐛 Known Issues

None currently identified. All major issues from v1.0 and v1.1 have been resolved.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/James-HoneyBadger/Time_Warp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/James-HoneyBadger/Time_Warp/discussions)
- **Documentation**: Check the repository README and wiki

## 🙏 Note About Previous Releases

Versions 1.0 and 1.1 have been removed from releases due to critical bugs that affected core functionality. Version 1.2.0 represents a stable, thoroughly tested release that resolves all identified issues.

---

**Happy Coding!** ⏰  
*Journey through code across time and spac
=======
# Time Warp IDE

A modern, educational programming environment built in Rust using the egui framework.

## Features

- **Multi-Language Support**: Execute code in three unified educational programming languages:
  - **TW BASIC**: Unified GW BASIC + PILOT + Logo with interactive input and turtle graphics
  - **TW Pascal**: Turbo Pascal-style structured programming
  - **TW Prolog**: Turbo Prolog-style logic programming

- **Interactive Input**: Support for user input in all languages via the unified Output & Graphics canvas
- **Turtle Graphics**: Visual programming with Logo-style turtle graphics integrated into the output canvas
- **Code Editor**: Full-featured editor with:
  - Line numbers
  - Find/Replace functionality
  - Syntax checking
  - Undo/Redo support

- **Unified Interface**: Combined text output and graphics in a single interactive canvas
- **Educational Focus**: Designed for teaching programming concepts with clear error messages and visual feedback

## Building and Running

### Prerequisites
- Rust 1.70 or later
- System dependencies for egui (varies by platform)

### Build
```bash
cargo build --release
```

### Run
```bash
cargo run
```

## Supported Languages

### TW BASIC
A unified educational language combining GW BASIC, PILOT, and Logo features.

**Features:**
- GW BASIC: Variables, arithmetic, PRINT statements, INPUT
- PILOT: Interactive questions (T:) and answers (A:)
- Logo: Turtle graphics commands (FORWARD, RIGHT, etc.)
- Both modern free-form and traditional line-numbered styles

Example:
```
LET X = 42
PRINT "Hello, TW BASIC!"
T: What is your name?
A: NAME$
PRINT "Hello, "; NAME$

FORWARD 100
RIGHT 90
FORWARD 50
```

### TW Pascal
Turbo Pascal-style structured programming with procedures, functions, and control structures.

Example:
```
program Hello;
var
  name: string;
begin
  writeln('What is your name?');
  readln(name);
  writeln('Hello, ', name);
end.
```

### TW Prolog
Turbo Prolog-style logic programming with domains, predicates, facts, and rules.

Example:
```
domains
  person = symbol
  color = symbol

predicates
  person(person)
  likes(person, color)

clauses
  person(john).
  person(mary).
  likes(john, blue).
  likes(mary, red).

goal
  likes(Person, Color),
  write(Person, " likes ", Color), nl.
```

## Project Structure

```
Time_Warp/
├── Cargo.toml              # Rust project configuration
├── src/
│   └── main.rs            # Main IDE implementation
├── examples/              # Sample programs for all languages
│   ├── tw_basic_sample.twb
│   ├── tw_basic_game.twb
│   ├── tw_pascal_sample.twp
│   ├── tw_pascal_advanced.twp
│   ├── tw_prolog_sample.tpr
│   └── tw_prolog_advanced.tpr
├── docs/
│   └── SAMPLE_PROGRAMS_README.md  # Detailed examples guide
├── .github/
│   └── copilot-instructions.md    # Development guidelines
└── README.md             # This file
```

## Sample Programs

See `docs/SAMPLE_PROGRAMS_README.md` for comprehensive examples demonstrating all language features. Sample programs are available in the `examples/` directory:

- **TW BASIC**: `examples/tw_basic_sample.twb`, `examples/tw_basic_game.twb`
- **TW Pascal**: `examples/tw_pascal_sample.twp`, `examples/tw_pascal_advanced.twp`
- **TW Prolog**: `examples/tw_prolog_sample.tpr`, `examples/tw_prolog_advanced.tpr`

## Architecture

The IDE is built using:
- **egui**: Immediate mode GUI framework
- **eframe**: App framework for egui
- **rfd**: Native file dialogs

The interpreter is implemented as a native Rust module with separate execution logic for each supported language, featuring a unified interactive canvas for text output, user input, and turtle graphics.

## File Extensions
- `.twb` - TW BASIC programs
- `.twp` - TW Pascal programs
- `.tpr` - TW Prolog programs

## Contributing

This is an educational project focused on teaching programming concepts through multiple language paradigms.

## License

Educational use encouraged.
>>>>>>> 066f2538e86bb3d8413c1ab261082a1d003dc877
