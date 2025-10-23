# Time Warp IDE

A modern, educational programming environment built in Rust using the egui framework.

## Features

- **TW BASIC Support**: Execute code in TW BASIC - a unified educational programming language combining GW BASIC, PILOT, and Logo features
- **Interactive Input**: Support for user input via the unified Output & Graphics canvas
- **General Prompt System**: Programmatic user input with callback-based API for plugins and extensions
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
INPUT "What is your name? "; NAME$
PRINT "Hello, "; NAME$

FORWARD 100
RIGHT 90
FORWARD 50
```

## Project Structure

```
Time_Warp/
├── Cargo.toml              # Rust project configuration
├── src/
│   └── main.rs            # Main IDE implementation
├── examples/              # Sample TW BASIC programs
│   ├── tw_basic_sample.twb
│   └── tw_basic_game.twb
├── docs/
│   └── SAMPLE_PROGRAMS_README.md  # Detailed examples guide
├── .github/
│   └── copilot-instructions.md    # Development guidelines
└── README.md             # This file
```

## Sample Programs

See `docs/SAMPLE_PROGRAMS_README.md` for comprehensive examples demonstrating TW BASIC features. Sample programs are available in the `examples/` directory:

**Example Files:**
- **TW BASIC**: `examples/tw_basic_sample.twb`, `examples/tw_basic_game.twb`, `examples/prompt_demo.twb`

## Prompt API

The IDE provides a general-purpose prompt system for programmatic user interaction:

```rust
// Example usage in Rust code
app.prompt_user("Enter your name:", |name| {
    println!("Hello, {}!", name);
    // Process the input here
});
```

**Features:**
- Modal dialog with custom message
- Callback-based response handling
- Submit on Enter key or button click
- Cancel option to abort input
- Status bar shows "💬 Awaiting Response" during prompts

**Use Cases:**
- Configuration input
- File name/path entry
- Interactive debugging
- Plugin/extension user interaction

## Architecture

The IDE is built using:
- **egui**: Immediate mode GUI framework
- **eframe**: App framework for egui
- **rfd**: Native file dialogs

The interpreter is implemented as a native Rust module with execution logic for TW BASIC, featuring a unified interactive canvas for text output, user input, and turtle graphics.

## File Extensions
- `.twb` - TW BASIC programs

## Contributing

This is an educational project focused on teaching programming concepts through multiple language paradigms.

### Development Guidelines

The `.github/copilot-instructions.md` file contains workspace-specific instructions for GitHub Copilot, including architecture overview, development workflows, and coding conventions. Contributors should review this file for consistent development practices.

## License

Educational use encouraged.