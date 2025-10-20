# Time_Warp IDE - Modular Architecture Documentation

## 🧩 Core Architecture Components

Time_Warp IDE features a clean, educational modular architecture designed for multi-language programming education with integrated turtle graphics.

## 🎯 **Central Components**

### **Main Application Entry Points**
- **`Time_Warp.py`** - Primary GUI application with Tkinter interface
- **`timewarp.py`** - Alternative entry point
- **`Time_Warp_II.py`** - Secondary application version

### **Unified Canvas System** (`unified_canvas.py`)
- **Single Display Surface**: Unified canvas for text and graphics rendering
- **GW BASIC Mode Emulation**: Screen mode 11 (1024×768, 256 colors)
- **Text Rendering**: Grid-based text input/output (25 rows × 80 columns)
- **Graphics Integration**: Turtle graphics and vector drawing capabilities
- **Input Handling**: Interactive prompts and keyboard input system

### **Core Interpreter Engine** (`core/interpreter.py`)
- **Multi-Language Execution**: Central execution engine for all supported languages
- **Language Detection**: Automatic command routing to appropriate language executors
- **Variable Management**: Unified variable system with `*VAR*` interpolation
- **Turtle Graphics Integration**: Built-in turtle graphics state management
- **Error Handling**: Educational error messages and debugging support

### **Language Executors** (`core/languages/`)
Each language has a dedicated executor class implementing the `execute_command()` method:

- **`time_warp.py`** - Time Warp unified educational language
  - Combines PILOT, BASIC, and Logo features
  - Variable interpolation with `*VAR*` syntax
  - Modern programming constructs

- **`pilot.py`** - PILOT (Programmed Inquiry Learning Or Teaching)
  - Educational language for computer-assisted instruction
  - Pattern matching with `M:` commands
  - Conditional branching with `Y:`/`N:` commands

- **`basic.py`** - BASIC (Beginner's All-purpose Symbolic Instruction Code)
  - Classic line-numbered programming
  - Traditional BASIC commands (PRINT, LET, GOTO, FOR/NEXT)
  - Mathematical operations and string handling

- **`logo.py`** - Logo programming language
  - Turtle graphics focused
  - Procedural programming with procedures
  - List processing capabilities

- **`pascal.py`** - Pascal structured programming
  - Strong typing and structured programming
  - Standard Pascal syntax and constructs
  - Educational focus on programming principles

- **`prolog.py`** - Prolog logic programming
  - Declarative programming paradigm
  - Facts, rules, and queries
  - Backtracking and unification

### **Plugin System** (`plugins/`)
- **Extensible Architecture**: Plugin framework for custom functionality
- **Sample Plugin**: Complete plugin template in `plugins/sample_plugin/`
- **Manifest System**: JSON-based plugin metadata and configuration
- **API Integration**: Hooks into core interpreter and UI systems

## 🏗️ **Architecture Design Principles**

### Educational-First Design

- **Progressive Complexity** - Languages from simple (PILOT) to advanced (Prolog)
- **Visual Learning** - Integrated turtle graphics for immediate feedback
- **Unified Interface** - Single canvas for all text and graphics operations
- **Clear Error Messages** - Educational error reporting and debugging

### Clean Modular Design

- **Separation of Concerns** - GUI, interpreter, and language logic separated
- **Single Responsibility** - Each module has a focused, clear purpose
- **Unified Canvas** - Single rendering surface eliminates mode complexity
- **Language Agnostic** - Core engine works with any language executor

### Extensibility and Maintenance

- **Plugin Architecture** - Easy addition of new features without core changes
- **Language Addition** - Simple process to add new language support
- **Test Integration** - Comprehensive testing at multiple levels
- **Documentation Focus** - Extensive documentation for maintenance

## 📊 **Technical Specifications**

### Language Support Matrix

| Language | Interactive | Compilation | Turtle Graphics | Examples |
|----------|-------------|-------------|-----------------|----------|
| **Time Warp** | ✅ | ✅ | ✅ | 15+ programs |
| **PILOT** | ✅ | ✅ | ✅ | 12+ programs |
| **BASIC** | ✅ | ✅ | ✅ | 10+ programs |
| **Logo** | ✅ | ✅ | ✅ | 8+ programs |
| **Pascal** | ✅ | ✅ | ✅ | 5+ programs |
| **Prolog** | ✅ | ✅ | ✅ | 3+ programs |

### Component Statistics

- **Core Python Files**: ~15 main application and engine files
- **Language Executors**: 6 dedicated executor classes
- **Test Files**: 20+ comprehensive test modules
- **Example Programs**: 50+ educational demonstrations
- **Documentation Files**: 30+ guides and references
- **Plugin Examples**: 1 complete plugin template

## 🔄 **System Integration**

### Interpreter-UI Communication

- **Command Execution**: Commands executed through `Time_WarpInterpreter.execute()`
- **Results Display**: Output shown via unified canvas text/graphics methods
- **Error Handling**: Centralized through interpreter's error display system
- **Input Prompts**: Handled through `UnifiedCanvas.prompt_input()` with callback system

### Turtle Graphics Integration

- **Unified Access**: All languages access turtle graphics through `self.interpreter.ide_unified_canvas`
- **State Management**: Graphics state managed in unified canvas with screen awareness
- **Automatic Setup**: Canvas clearing and setup handled automatically per execution
- **Cross-Language**: Compatible with existing turtle graphics commands across all languages

### Screen Mode Management

- **Single Mode**: Mode 11 only - Unified Canvas (1024×768, 256 colors)
- **Text Grid**: 25 rows × 80 columns for input/output
- **Graphics**: Full 1024×768 pixel canvas with 256 colors
- **Turtle Graphics**: Integrated with unified canvas for all languages

## 🚀 **Development Workflow**

### Adding a New Language

1. **Create Executor**: Add new executor class in `core/languages/newlang.py`
2. **Implement Interface**: Implement `execute_command()` method following existing patterns
3. **Register Language**: Add import and mapping in `core/interpreter.py`
4. **Add Syntax**: Update command detection logic for the new language
5. **Create Examples**: Add example programs in `examples/` directory
6. **Update Documentation**: Add language guide in `docs/languages/`

### Plugin Development

1. **Create Plugin**: Use `plugins/sample_plugin/` as template
2. **Implement Plugin Class**: Create class with `initialize()` method
3. **Define Manifest**: Create `manifest.json` with plugin metadata
4. **Add Functionality**: Implement desired features using plugin API
5. **Test Integration**: Verify plugin loads and functions correctly

### Testing Strategy

- **Unit Tests**: Individual component testing
- **Integration Tests**: Full system verification
- **Language Tests**: Each language executor validation
- **Graphics Tests**: Turtle graphics and canvas functionality
- **Plugin Tests**: Plugin system verification

## 🎯 **Key Integration Points**

### Command Processing Flow

1. **User Input** → Unified Canvas → Interpreter
2. **Language Detection** → Route to appropriate executor
3. **Command Execution** → Language-specific processing
4. **Result Handling** → Display via unified canvas
5. **Graphics Updates** → Turtle state management

### Variable System

- **Unified Storage**: All languages share the same variable system
- **Interpolation**: `*VAR*` syntax works across all languages
- **Type Handling**: Automatic type conversion and validation
- **Persistence**: Variables maintained across command executions

### Error Handling

- **Educational Messages**: Clear, helpful error descriptions
- **Language Context**: Errors include language-specific guidance
- **Recovery**: Graceful error handling with continuation options
- **Debugging**: Built-in debugging and breakpoint support

This modular architecture provides a solid foundation for educational programming while maintaining clean, maintainable code and extensive customization capabilities.