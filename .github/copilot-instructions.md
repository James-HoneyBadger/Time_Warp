<<<<<<< HEAD
# Time_Warp IDE Copilot Instructions

Time_Warp IDE is an educational programming IDE supporting multiple languages with turtle graphics, built in Python using tkinter.

## Architecture Overview

### Core Structure
- **Main Application**: `Time_Warp.py` - Entry point with comprehensive UI and component integration
- **Core Interpreter**: `core/interpreter.py` - Central execution engine for all languages
- **Language Executors**: `core/languages/` - Individual language implementations (PILOT, BASIC, Logo, etc.)
- **Theme System**: `tools/theme.py` - Persistent theme management with 8 built-in themes
- **Plugin System**: `plugins/` - Extensible architecture for custom functionality

### Multi-Language Support
Each language has dedicated executor classes in `core/languages/`:
- **PILOT**: Educational language with turtle graphics (`T:`, `A:`, `J:`, `Y:`, `N:` commands)
- **BASIC**: Classic line-numbered programming (`PRINT`, `INPUT`, `LET`, `GOTO`, `IF...THEN`)
- **Logo**: Turtle graphics programming (`FORWARD`, `BACK`, `LEFT`, `RIGHT`)
- **Python/JavaScript/Perl**: Modern scripting language support

### Key Components
- **Time_WarpInterpreter**: Central execution engine that dispatches to language-specific executors
- **ThemeManager**: JSON-based configuration with 8 themes (4 dark: Dracula, Monokai, Solarized Dark, Ocean; 4 light: Spring, Sunset, Candy, Forest)
- **Plugin System**: `PluginManager` with sample plugin architecture in `plugins/sample_plugin/`
- **Game Engine**: Complete 2D game framework in `games/engine/` with physics, rendering, and object management

## Development Patterns

### File Naming Conventions
- **Test files**: `test_*.py` for unit tests, `*_test.py` for integration tests
- **Language demos**: `*.pilot`, `*.bas`, `*.logo` for example programs
- **Compiled output**: `*_compiled` files for interpreter execution results

### Configuration Management
- User settings stored in `~/.Time_Warp/config.json`
- Theme preferences persist between sessions
- Virtual environment auto-created in `.Time_Warp/`

### Error Handling Patterns
```python
# Standard Time_Warp error pattern
try:
    result = self._execute_language_specific_command(command)
    return result
except Exception as e:
    error_msg = f"❌ Error in {language}: {str(e)}"
    self.interpreter.display_error(error_msg)
    return None
```

## Development Workflows

### Running Time_Warp
```bash
# Primary method - auto-creates venv if needed
python Time_Warp.py

# Alternative with shell script
./scripts/start.sh
```

### Testing
```bash
# Run comprehensive test suite
python run_tests.py

# Test specific components
python test_interpreters.py
python test_themes.py
```

### Adding New Languages
1. Create executor class in `core/languages/new_language.py`
2. Implement `execute_command()` method following existing patterns
3. Register in `core/interpreter.py` import and language mapping
4. Add syntax highlighting and file extensions to main UI

### Theme Development
Themes defined in `tools/theme.py` with color schemes applied uniformly across:
- Main window backgrounds
- Editor components
- Menu systems
- Button styles
- Output panels

### Plugin Development
See `plugins/sample_plugin/` for complete plugin template including:
- `__init__.py` with plugin metadata
- Main plugin class with `initialize()` method
- Integration hooks for UI and interpreter

## Critical Integration Points

### Interpreter-UI Communication
- Commands executed through `Time_WarpInterpreter.execute()` method
- Results displayed via `self.output_text.insert()` in main UI
- Error handling centralized through interpreter's error display system

### Turtle Graphics Integration
- Each language executor can access `self.interpreter.turtle_canvas`
- Graphics state managed in main application
- Canvas clearing and setup handled automatically per execution
=======
<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file --># Time_Warp IDE Copilot Instructions
>>>>>>> 1407509ac281ab1d8fb01ccc3e7fef1aada6ff9c

---

purpose: Workspace-specific instructions for Copilot in Time_Warp IDE project

last-updated: October 22, 2025

contact: James-HoneyBadger

---

Time_Warp IDE is an educational programming IDE supporting multiple languages with turtle graphics, built in Rust using egui and eframe.

## Architecture Overview

### Core Structure

- **Main Application**: `src/main.rs` - Entry point with unified canvas interface and component integration
- **Unified Canvas**: Integrated in `src/main.rs` - GW BASIC screen mode emulation with text/graphics rendering using egui
- **Core Interpreter**: `src/main.rs` - Central execution engine for all languages (currently stubbed)
- **Language Executors**: Planned in `src/main.rs` or separate modules - Individual language implementations (PILOT, BASIC, Logo, etc.)
- **Theme System**: Integrated in `src/main.rs` - Theme management with egui theming
- **Plugin System**: Not yet implemented - Extensible architecture for custom functionality

### Unified Canvas Architecture

The IDE uses egui for rendering:

- **Unified Canvas**: egui-based canvas supporting text/graphics rendering
- **Text Rendering**: Text input/output with egui widgets
- **Graphics Rendering**: Pixel and vector graphics integrated with text display using egui painter
- **Turtle Graphics**: Compatible with existing turtle graphics commands (implemented with zoom/pan)

### Multi-Language Support

Each language will have dedicated executor classes in `src/`:

- **PILOT**: Educational language with turtle graphics (`T:`, `A:`, `J:`, `Y:`, `N:` commands)
- **BASIC**: Classic line-numbered programming (`PRINT`, `INPUT`, `LET`, `GOTO`, `IF...THEN`)
- **Logo**: Turtle graphics programming (`FORWARD`, `BACK`, `LEFT`, `RIGHT`)
- **Python/JavaScript/Perl**: Modern scripting language support

### Key Components

- **TimeWarpApp**: Main egui app struct containing all state and UI logic
- **TurtleState**: Struct managing turtle graphics position, angle, and drawing state
- **UI Components**: Menu bar, status bar, code editor, canvas, and turtle controls
- **Theme Support**: egui theming for light/dark modes
- **File I/O**: rfd crate for cross-platform file dialogs

### File Naming Conventions

- **Source files**: `src/*.rs` for Rust source code
- **Test files**: `tests/*.rs` for unit tests
- **Compiled output**: `target/debug/time-warp-ide` for executable
- **Examples**: `examples/*.twb`, `examples/*.twp`, `examples/*.tpr` for sample programs

### Configuration Management

- User settings stored in application state (future: config file)
- Theme preferences persist between sessions
- Virtual environment not needed (compiled binary)

### Error Handling Patterns

```rust
// Standard Time_Warp error pattern
match self.execute_command(command) {
    Ok(result) => {
        // Handle success
    }
    Err(e) => {
        self.status_message = format!("Error: {}", e);
    }
}
```

### Execution Guidelines

PROGRESS TRACKING:
- If any tools are available to manage the above todo list, use it to track progress through this checklist.
- After completing each step, mark it complete and add a summary.
- Read current todo list status before starting each new step.

## Development Workflows

COMMUNICATION RULES:
- Avoid verbose explanations or printing full command outputs.
- If a step is skipped, state that briefly (e.g. "No extensions needed").
- Do not explain project structure unless asked.
- Keep explanations concise and focused.

### Running Time_Warp

```bash
# Build and run
cargo run

# Build release
cargo build --release
```

DEVELOPMENT RULES:
- Use '.' as the working directory unless user specifies otherwise.
- Avoid adding media or external links unless explicitly requested.
- Use placeholders only with a note that they should be replaced.
- Use VS Code API tool only for VS Code extension projects.

## Editing Guidelines

- Use `replace_string_in_file` for precise edits, providing 3-5 lines of context before and after.
- For `apply_patch`, ensure minimal diffs, preserve indentation, and do not reformat unrelated code.
- Best practices: keep changes minimal, avoid adding external links unless requested.

### Testing

```bash
# Run tests
cargo test

# Run specific test
cargo test test_name
```

FOLDER CREATION RULES:
- Always use the current directory as the project root.
- Do not create a new folder unless the user explicitly requests it besides a .vscode folder for a tasks.json file.
- If any of the scaffolding commands mention that the folder name is not correct, let the user know to create a new folder with the correct name and then reopen it again in vscode.

EXTENSION INSTALLATION RULES:
- Only install extension specified by the get_project_setup_info tool. DO NOT INSTALL any other extensions.

### Adding New Languages

1. Create executor module in `src/languages/new_language.rs`
2. Implement `execute_command()` method following existing patterns
3. Register in `src/main.rs` import and language mapping
4. Add syntax highlighting and file extensions to main UI

PROJECT CONTENT RULES:
- If the user has not specified project details, assume they want a "Hello World" project as a starting point.
- Avoid adding links of any type (URLs, files, folders, etc.) or integrations that are not explicitly required.
- Avoid generating images, videos, or any other media files unless explicitly requested.
- If you need to use any media assets as placeholders, let the user know that these are placeholders and should be replaced with the actual assets later.
- Ensure all generated components serve a clear purpose within the user's requested workflow.
- If a feature is assumed but not confirmed, prompt the user for clarification before including it.

### Theme Development

Themes defined using egui's theming system:
- Main window backgrounds
- Editor components
- Menu systems
- Button styles
- Output panels

TASK COMPLETION RULES:
- Your task is complete when:
  - Project compiles without errors (`cargo build`)
  - Executable runs successfully (`cargo run`)
  - copilot-instructions.md file in the .github directory exists in the project
  - README.md file exists and is up to date
  - User is provided with clear instructions to debug/launch the project

### Plugin Development

Not yet implemented - future extensible architecture.

Before starting a new task in the above plan, update progress in the plan.

- Work through each checklist item systematically.

## Critical Integration Points

- Keep communication concise and focused.
- Follow development best practices.

### Interpreter-UI Communication
- Commands executed through `TimeWarpApp::execute_command()` method
- Results displayed via egui widgets and canvas
- Error handling centralized through status messages
- Input prompts handled through egui text input widgets

### Turtle Graphics Integration
- Turtle state managed in `TurtleState` struct
- Graphics rendered using egui painter with zoom/pan support
- Canvas clearing and setup handled automatically per execution
- Compatible with existing turtle graphics commands

### Screen Mode Management
- **Single Mode**: Graphics mode with text overlay
- **Text Grid**: Text input/output with egui text widgets
- **Graphics**: Full canvas with 2D drawing using egui painter
- **Turtle Graphics**: Integrated with canvas

### Hardware/IoT Extensions
Future features for:
- Raspberry Pi GPIO control
- Sensor data visualization
- Arduino integration
- Smart home device management

## Code Style and Conventions

- Use descriptive docstrings for all structs and functions
- Error messages prefixed with emoji indicators (`❌`, `ℹ️`, `🎨`, `🚀`)
- Graceful degradation for optional dependencies
- Consistent Rust formatting (`cargo fmt`)
- Type-safe variable management

## Testing Strategy

Tests focus on:
- Individual language executor functionality
- UI component interactions
- File loading/saving operations
- Turtle graphics rendering
- Multi-language integration scenarios

When adding features, ensure compatibility across all supported languages and maintain the educational focus of the platform.

### File Naming Conventions

- **Test files**: `test_*.py` for unit tests, `*_test.py` for integration tests
- **Language demos**: `*.pilot`, `*.bas`, `*.logo` for example programs
- **Compiled output**: `*_compiled` files for interpreter execution results

### Configuration Management

- User settings stored in application state (future: config file)
- Theme preferences persist between sessions
- Virtual environment not needed (compiled binary)

### Error Handling Patterns

```rust
// Standard Time_Warp error pattern
match self.execute_command(command) {
    Ok(result) => {
        // Handle success
    }
    Err(e) => {
        self.status_message = format!("Error: {}", e);
    }
}
```

### Execution Guidelines

PROGRESS TRACKING:
- If any tools are available to manage the above todo list, use it to track progress through this checklist.
- After completing each step, mark it complete and add a summary.
- Read current todo list status before starting each new step.

## Development Workflows

COMMUNICATION RULES:
- Avoid verbose explanations or printing full command outputs.
- If a step is skipped, state that briefly (e.g. "No extensions needed").
- Do not explain project structure unless asked.
- Keep explanations concise and focused.

### Running Time_Warp

```bash
# Build and run
cargo run

# Build release
cargo build --release
```

DEVELOPMENT RULES:
- Use '.' as the working directory unless user specifies otherwise.
- Avoid adding media or external links unless explicitly requested.
- Use placeholders only with a note that they should be replaced.
- Use VS Code API tool only for VS Code extension projects.

## Editing Guidelines

- Use `replace_string_in_file` for precise edits, providing 3-5 lines of context before and after.
- For `apply_patch`, ensure minimal diffs, preserve indentation, and do not reformat unrelated code.
- Best practices: keep changes minimal, avoid adding external links unless requested.

### Testing

```bash
# Run tests
cargo test

# Run specific test
cargo test test_name
```

FOLDER CREATION RULES:
- Always use the current directory as the project root.
- Do not create a new folder unless the user explicitly requests it besides a .vscode folder for a tasks.json file.
- If any of the scaffolding commands mention that the folder name is not correct, let the user know to create a new folder with the correct name and then reopen it again in vscode.

EXTENSION INSTALLATION RULES:
- Only install extension specified by the get_project_setup_info tool. DO NOT INSTALL any other extensions.

### Adding New Languages

1. Create executor module in `src/languages/new_language.rs`
2. Implement `execute_command()` method following existing patterns
3. Register in `src/main.rs` import and language mapping
4. Add syntax highlighting and file extensions to main UI

PROJECT CONTENT RULES:
- If the user has not specified project details, assume they want a "Hello World" project as a starting point.
- Avoid adding links of any type (URLs, files, folders, etc.) or integrations that are not explicitly required.
- Avoid generating images, videos, or any other media files unless explicitly requested.
- If you need to use any media assets as placeholders, let the user know that these are placeholders and should be replaced with the actual assets later.
- Ensure all generated components serve a clear purpose within the user's requested workflow.
- If a feature is assumed but not confirmed, prompt the user for clarification before including it.

### Theme Development

Themes defined in `tools/theme.py` with color schemes applied uniformly across:
- Main window backgrounds
- Editor components
- Menu systems
- Button styles
- Output panels

TASK COMPLETION RULES:
- Your task is complete when:
  - Project is successfully scaffolded and compiled without errors
  - copilot-instructions.md file in the .github directory exists in the project
  - README.md file exists and is up to date
  - User is provided with clear instructions to debug/launch the project

### Plugin Development

See `plugins/sample_plugin/` for complete plugin template including:
- `__init__.py` with plugin metadata
- Main plugin class with `initialize()` method
- Integration hooks for UI and interpreter

Before starting a new task in the above plan, update progress in the plan.

- Work through each checklist item systematically.

## Critical Integration Points

- Keep communication concise and focused.
- Follow development best practices.

### Interpreter-UI Communication
- Commands executed through `Time_WarpInterpreter.execute()` method
- Results displayed via unified canvas text/graphics rendering methods
- Error handling centralized through interpreter's error display system
- Input prompts handled through `UnifiedCanvas.prompt_input()` with callback system

### Turtle Graphics Integration
- Each language executor can access `self.interpreter.ide_unified_canvas`
- Graphics state managed in unified canvas with screen mode awareness
- Canvas clearing and setup handled automatically per execution
- Compatible with existing turtle graphics commands

### Screen Mode Management
- **Single Mode**: Mode 11 only - Unified Canvas (1024×768, 256 colors)
- **Text Grid**: 25 rows × 80 columns for input/output
- **Graphics**: Full 1024×768 pixel canvas with 256 colors
- **Turtle Graphics**: Integrated with unified canvas
>>>>>>> 066f2538e86bb3d8413c1ab261082a1d003dc877

### Hardware/IoT Extensions
Advanced features in `core/hardware/` and `core/iot/` for:
- Raspberry Pi GPIO control
- Sensor data visualization
- Arduino integration
- Smart home device management

## Code Style and Conventions

- Use descriptive docstrings for all structs and functions
- Error messages prefixed with emoji indicators (`❌`, `ℹ️`, `🎨`, `🚀`)
- Graceful degradation for optional dependencies
- Consistent Rust formatting (`cargo fmt`)
- Type-safe variable management

## Testing Strategy

Tests focus on:
- Individual language executor functionality
- Theme system persistence
- File loading/saving operations
- Multi-language integration scenarios
- UI component interactions

When adding features, ensure compatibility across all supported languages and maintain the educational focus of the platform.