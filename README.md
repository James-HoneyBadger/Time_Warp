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

## Sample Programs

See `SAMPLE_PROGRAMS_README.md` for comprehensive examples demonstrating all language features.

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