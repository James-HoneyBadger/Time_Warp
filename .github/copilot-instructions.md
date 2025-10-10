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

### Hardware/IoT Extensions
Advanced features in `core/hardware/` and `core/iot/` for:
- Raspberry Pi GPIO control
- Sensor data visualization
- Arduino integration
- Smart home device management

## Code Style and Conventions

- Use descriptive docstrings for all classes and complex methods
- Error messages prefixed with emoji indicators (`❌`, `ℹ️`, `🎨`, `🚀`)
- Graceful degradation for optional dependencies (PIL, external hardware)
- Consistent indentation and modern Python practices
- Type-safe variable management in language executors

## Testing Strategy

Tests focus on:
- Individual language executor functionality
- Theme system persistence
- File loading/saving operations
- Multi-language integration scenarios
- UI component interactions

When adding features, ensure compatibility across all supported languages and maintain the educational focus of the platform.