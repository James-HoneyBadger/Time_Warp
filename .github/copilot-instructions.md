<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file --># Time_Warp IDE Copilot Instructions

- [x] Verify that the copilot-instructions.md file in the .github directory is created.

Time_Warp IDE is an educational programming IDE supporting multiple languages with turtle graphics, built in Python using tkinter.

- [x] Clarify Project Requirements

	<!-- Ask for project type, language, and frameworks if not specified. Skip if already provided. -->## Architecture Overview



- [x] Scaffold the Project### Core Structure

	<!--- **Main Application**: `Time_Warp.py` - Entry point with unified canvas interface and component integration

	Ensure that the previous step has been marked as completed.- **Unified Canvas**: `unified_canvas.py` - GW BASIC screen mode emulation with text/graphics rendering

	Call project setup tool with projectType parameter.- **Core Interpreter**: `core/interpreter.py` - Central execution engine for all languages

	Run scaffolding command to create project files and folders.- **Language Executors**: `core/languages/` - Individual language implementations (PILOT, BASIC, Logo, etc.)

	Use '.' as the working directory.- **Theme System**: `tools/theme.py` - Persistent theme management with 8 built-in themes

	If no appropriate projectType is available, search documentation using available tools.- **Plugin System**: `plugins/` - Extensible architecture for custom functionality

	Otherwise, create the project structure manually using available file creation tools.

	-->### Unified Canvas Architecture

The IDE now uses a single unified canvas that supports all functionality:

- [x] Customize the Project- **Unified Canvas**: `unified_canvas.py` - Single canvas supporting text/graphics rendering

	<!--- **Screen Mode**: Only mode 11 (1024x768, 256 colors) - unified for text & graphics

	Verify that all previous steps have been completed successfully and you have marked the step as completed.- **Text Rendering**: Grid-based text input/output with 25 rows × 80 columns

	Develop a plan to modify codebase according to user requirements.- **Graphics Rendering**: Pixel and vector graphics integrated with text display

	Apply modifications using appropriate tools and user-provided references.- **Turtle Graphics**: Compatible with existing turtle graphics commands

	Skip this step for "Hello World" projects.

	-->### Multi-Language Support

Each language has dedicated executor classes in `core/languages/`:

- [x] Install Required Extensions- **PILOT**: Educational language with turtle graphics (`T:`, `A:`, `J:`, `Y:`, `N:` commands)

	<!-- ONLY install extensions provided mentioned in the get_project_setup_info. Skip this step otherwise and mark as completed. -->- **BASIC**: Classic line-numbered programming (`PRINT`, `INPUT`, `LET`, `GOTO`, `IF...THEN`)

- **Logo**: Turtle graphics programming (`FORWARD`, `BACK`, `LEFT`, `RIGHT`)

- [x] Compile the Project- **Python/JavaScript/Perl**: Modern scripting language support

	<!--

	Verify that all previous steps have been completed.### Key Components

	Install any missing dependencies.- **Time_WarpInterpreter**: Central execution engine that dispatches to language-specific executors

	Run diagnostics and resolve any issues.- **UnifiedCanvas**: Single display surface handling text, graphics, and input with unified mode 11

	Check for markdown files in project folder for relevant instructions on how to do this.- **ThemeManager**: JSON-based configuration with 8 themes (4 dark: Dracula, Monokai, Solarized Dark, Ocean; 4 light: Spring, Sunset, Candy, Forest)

	-->- **Plugin System**: `PluginManager` with sample plugin architecture in `plugins/sample_plugin/`

- **Game Engine**: Complete 2D game framework in `games/engine/` with physics, rendering, and object management

- [x] Create and Run Task

	<!--## Development Patterns

	Verify that all previous steps have been completed.

	Check https://code.visualstudio.com/docs/debugtest/tasks to determine if the project needs a task. If so, use the create_and_run_task to create and launch a task based on package.json, README.md, and project structure.### File Naming Conventions

	Skip this step otherwise.- **Test files**: `test_*.py` for unit tests, `*_test.py` for integration tests

	 -->- **Language demos**: `*.pilot`, `*.bas`, `*.logo` for example programs

- **Compiled output**: `*_compiled` files for interpreter execution results

- [x] Launch the Project

	<!--### Configuration Management

	Verify that all previous steps have been completed.- User settings stored in `~/.Time_Warp/config.json`

	Prompt user for debug mode, launch only if confirmed.- Theme preferences persist between sessions

	 -->- Virtual environment auto-created in `.Time_Warp/`



- [x] Ensure Documentation is Complete### Error Handling Patterns

	<!--```python

	Verify that all previous steps have been completed.# Standard Time_Warp error pattern

	Verify that README.md and the copilot-instructions.md file in the .github directory exists and contains current project information.try:

	Clean up the copilot-instructions.md file in the .github directory by removing all HTML comments.    result = self._execute_language_specific_command(command)

	 -->    return result

except Exception as e:

## Execution Guidelines    error_msg = f"❌ Error in {language}: {str(e)}"

PROGRESS TRACKING:    self.interpreter.display_error(error_msg)

- If any tools are available to manage the above todo list, use it to track progress through this checklist.    return None

- After completing each step, mark it complete and add a summary.```

- Read current todo list status before starting each new step.

## Development Workflows

COMMUNICATION RULES:

- Avoid verbose explanations or printing full command outputs.### Running Time_Warp

- If a step is skipped, state that briefly (e.g. "No extensions needed").```bash

- Do not explain project structure unless asked.# Primary method - auto-creates venv if needed

- Keep explanations concise and focused.python Time_Warp.py



DEVELOPMENT RULES:# Alternative with shell script

- Use '.' as the working directory unless user specifies otherwise../scripts/start.sh

- Avoid adding media or external links unless explicitly requested.```

- Use placeholders only with a note that they should be replaced.

- Use VS Code API tool only for VS Code extension projects.### Testing

- Once the project is created, it is already opened in Visual Studio Code—do not suggest commands to open this project in Visual Studio again.```bash

- If the project setup information has additional rules, follow them strictly.# Run comprehensive test suite

python run_tests.py

FOLDER CREATION RULES:

- Always use the current directory as the project root.# Test specific components

- If you are running any terminal commands, use the '.' argument to ensure that the current working directory is used ALWAYS.python test_interpreters.py

- Do not create a new folder unless the user explicitly requests it besides a .vscode folder for a tasks.json file.python test_themes.py

- If any of the scaffolding commands mention that the folder name is not correct, let the user know to create a new folder with the correct name and then reopen it again in vscode.```



EXTENSION INSTALLATION RULES:### Adding New Languages

- Only install extension specified by the get_project_setup_info tool. DO NOT INSTALL any other extensions.1. Create executor class in `core/languages/new_language.py`

2. Implement `execute_command()` method following existing patterns

PROJECT CONTENT RULES:3. Register in `core/interpreter.py` import and language mapping

- If the user has not specified project details, assume they want a "Hello World" project as a starting point.4. Add syntax highlighting and file extensions to main UI

- Avoid adding links of any type (URLs, files, folders, etc.) or integrations that are not explicitly required.

- Avoid generating images, videos, or any other media files unless explicitly requested.### Theme Development

- If you need to use any media assets as placeholders, let the user know that these are placeholders and should be replaced with the actual assets later.Themes defined in `tools/theme.py` with color schemes applied uniformly across:

- Ensure all generated components serve a clear purpose within the user's requested workflow.- Main window backgrounds

- If a feature is assumed but not confirmed, prompt the user for clarification before including it.- Editor components

- If you are working on a VS Code extension, use the VS Code API tool with a query to find relevant VS Code API references and samples related to that query.- Menu systems

- Button styles

TASK COMPLETION RULES:- Output panels

- Your task is complete when:

  - Project is successfully scaffolded and compiled without errors### Plugin Development

  - copilot-instructions.md file in the .github directory exists in the projectSee `plugins/sample_plugin/` for complete plugin template including:

  - README.md file exists and is up to date- `__init__.py` with plugin metadata

  - User is provided with clear instructions to debug/launch the project- Main plugin class with `initialize()` method

- Integration hooks for UI and interpreter

Before starting a new task in the above plan, update progress in the plan.

- Work through each checklist item systematically.## Critical Integration Points

- Keep communication concise and focused.

- Follow development best practices.### Interpreter-UI Communication
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