# Time_Warp IDE 1.1 - Project Structure

## 📁 Directory Organization

### Root Directory
```
Time_Warp/
├── Time_Warp.py              # Main application entry point
├── time_warp -> Time_Warp.py  # Symbolic link for convenience
├── README.md                # Project documentation
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Modern Python project configuration
├── Time_Warp.code-workspace # VS Code workspace configuration
└── .gitignore              # Git ignore patterns
```

### Core Framework
```
core/
├── interpreter.py          # Central execution engine
├── languages/              # Language-specific executors
│   ├── pilot.py            # PILOT language support
│   ├── basic.py            # BASIC language support
│   ├── logo.py             # Logo turtle graphics
│   ├── python_executor.py  # Python execution
│   ├── javascript_executor.py # JavaScript support
│   └── perl.py             # Perl language support
├── features/               # IDE feature implementations
│   ├── tutorial_system.py  # Interactive tutorials
│   ├── ai_assistant.py     # Code assistance
│   └── gamification.py     # Achievement system
├── audio/                  # Audio system
├── hardware/               # Hardware integration
├── iot/                    # IoT device support
├── networking/             # Collaboration features
├── optimizations/          # Performance enhancements
└── utilities/              # Helper utilities
```

### User Interface
```
gui/
├── components/             # Reusable UI components
│   └── multi_tab_editor.py # Multi-tab code editor
├── dialogs/                # Dialog windows
└── themes/                 # UI theme definitions
```

### Tools & Utilities
```
tools/
├── theme.py                # Theme management system
├── performance_bench.py    # Performance benchmarking
└── tool_manager.py         # Tool coordination
```

### Compilation System
```
compilers/
├── pilot_compiler.py       # PILOT language compiler
├── basic_compiler.py       # BASIC language compiler
├── logo_compiler.py        # Logo language compiler
└── base.py                 # Base compiler functionality
```

### Game Engine
```
games/
├── engine/                 # 2D game engine
└── samples/                # Sample games
```

### Plugin Architecture
```
plugins/
├── sample_plugin/          # Example plugin
└── __init__.py             # Plugin system initialization
```

### Development & Testing
```
scripts/                    # Development scripts
├── run_all_tests.py        # Master test runner
├── run_tests.py            # Basic test runner
├── run_tests_ci.py         # CI/CD test runner
├── setup.py                # Installation script
├── launch.py               # Python launcher
├── launch_timewarp.sh      # Shell launcher
├── launch_timewarp.bat     # Windows launcher
└── start.sh                # Quick start script

tests/                      # Test suite
├── test_comprehensive.py   # Complete test coverage
├── sample_outputs/         # Test output samples
└── tests/                  # Additional test files
```

### Documentation
```
docs/                       # Documentation files
├── README_v11.md           # Version 1.1 features
├── DIRECTORY_STRUCTURE.md  # Project organization
├── CONTRIBUTING.md         # Contribution guidelines
└── LICENSE                 # MIT license
```

### Example Programs
```
examples/                   # Sample programs
├── pilot/                  # PILOT examples
├── basic/                  # BASIC examples
├── logo/                   # Logo examples
└── python/                 # Python examples
```

### Marketing & Community
```
marketing/                  # Marketing materials
├── social_media/           # Social media content
└── community/              # Community resources
```

### Build & Distribution
```
dist/                       # Distribution builds
build/                      # Build artifacts
archive/                    # Archived/deprecated files
.github/                    # GitHub workflows & templates
.vscode/                    # VS Code configuration
```

## 🎯 Key Files

### Primary Entry Points
- `Time_Warp.py` - Main GUI application
- `time_warp` - Symbolic link for terminal usage
- `scripts/launch.py` - Cross-platform launcher

### Configuration
- `Time_Warp.code-workspace` - VS Code workspace settings
- `pyproject.toml` - Modern Python project configuration
- `requirements.txt` - Runtime dependencies

### Testing
- `tests/test_comprehensive.py` - Complete test suite
- `scripts/run_all_tests.py` - Master test runner

## 🚀 Usage

### Direct Execution
```bash
python3 Time_Warp.py        # Direct execution
./time_warp                 # Via symbolic link
```

### Via Scripts
```bash
./scripts/launch.py        # Cross-platform launcher
./scripts/start.sh         # Quick start script
```

### VS Code Integration
- Use Ctrl+F5 or F5 to run/debug
- Pre-configured launch configurations
- Integrated terminal and task support

## 📊 Project Statistics

- **Languages Supported**: 6 (PILOT, BASIC, Logo, Python, JavaScript, Perl)
- **Themes Available**: 8 (4 dark, 4 light)
- **Test Coverage**: 23 comprehensive tests
- **Plugin System**: Extensible architecture
- **Total Files**: ~200+ organized files
- **Code Quality**: All tests passing ✅

This clean, organized structure makes Time_Warp IDE 1.1 professional, maintainable, and ready for production use.