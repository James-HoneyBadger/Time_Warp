# Time_Warp IDE 1.1 - Project Structure (Organized)

## 📁 Directory Organization

### Root Directory (Essential Files Only)
```
Time_Warp/
├── timewarp.py              # Main application entry point
├── README.md                # Project documentation
├── CHANGELOG.md             # Version history
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Modern Python project configuration
├── pytest.ini             # Testing configuration
├── Time_Warp.code-workspace # VS Code workspace configuration
├── .gitignore              # Git ignore patterns
├── .pre-commit-config.yaml # Pre-commit hooks configuration
└── .venv/                  # Virtual environment (auto-created)
```

### Main Application Package
```
src/timewarp/
├── __init__.py             # Package initialization
├── main.py                 # Main application (formerly Time_Warp.py)
├── core/                   # Core framework
│   ├── interpreter.py      # Central execution engine
│   ├── languages/          # Language-specific executors
│   │   ├── pilot.py        # PILOT language support
│   │   ├── basic.py        # BASIC language support
│   │   ├── logo.py         # Logo turtle graphics
│   │   ├── python_executor.py # Python execution
│   │   ├── javascript_executor.py # JavaScript support
│   │   └── perl.py         # Perl language support
│   ├── features/           # IDE feature implementations
│   │   ├── tutorial_system.py # Interactive tutorials
│   │   ├── ai_assistant.py # Code assistance
│   │   └── gamification.py # Achievement system
│   ├── audio/              # Audio system
│   ├── hardware/           # Hardware integration
│   ├── iot/                # IoT device support
│   ├── networking/         # Collaboration features
│   ├── optimizations/      # Performance enhancements
│   └── utilities/          # Helper utilities
├── gui/                    # User interface components
│   ├── components/         # Reusable UI components
│   │   └── multi_tab_editor.py # Multi-tab code editor
│   ├── dialogs/            # Dialog windows
│   └── themes/             # UI theme definitions
├── utils/                  # Tools & utilities (formerly tools/)
│   ├── theme.py            # Theme management system
│   ├── performance_bench.py # Performance benchmarking
│   └── tool_manager.py     # Tool coordination
└── games/                  # Game engine
    ├── engine/             # 2D game engine
    └── samples/            # Sample games
```

### Plugin Architecture
```
plugins/
├── __init__.py             # Plugin system initialization
├── sample_plugin/          # Example plugin implementation
└── plugins/                # Additional plugins directory
```

### Development & Testing
```
scripts/                    # Development scripts
├── README.md               # Scripts documentation
├── prepare_release.sh      # Release preparation
├── run_all_tests.py        # Master test runner
├── run_tests.py            # Basic test runner
├── run_tests_ci.py         # CI/CD test runner
├── setup.py                # Installation script
├── install_dependencies.py # Dependency installer
├── launch.py               # Python launcher
├── launch_Time_Warp.sh     # Shell launcher
├── launch_Time_Warp.bat    # Windows launcher
├── start.sh                # Quick start script
├── build/                  # Build-related scripts
└── development/            # Development utilities

tests/                      # Test suite organization
├── README.md               # Testing documentation
├── unit/                   # Unit tests
├── integration/            # Integration tests
├── fixtures/               # Test data and fixtures
├── verification/           # Verification test suite
├── sample_outputs/         # Test output samples
├── test_results/           # Test execution results
├── tests/                  # Additional test modules
├── test_*.py               # Individual test modules
├── theme_test.py           # Theme testing
└── verify_working.py       # Working verification
```

### Documentation (Organized)
```
docs/                       # Documentation files
├── PROJECT_STRUCTURE.md    # This file - project organization
├── README_v11.md           # Version 1.1 features
├── DIRECTORY_STRUCTURE.md  # Directory organization guide
├── MODULAR_ARCHITECTURE.md # Architecture documentation
├── GITHUB_INTEGRATION.md   # GitHub integration guide
├── VERSION_1_1_ROADMAP.md  # Development roadmap
├── LICENSE                 # MIT license
├── compiler.md             # Compiler documentation
├── user-guide/             # End-user documentation
├── developer-guide/        # Contributing and development docs
├── api/                    # API reference documentation
├── languages/              # Language-specific guides
├── development/            # Development documentation
├── guides/                 # General guides
├── reports/                # Project and development reports
└── releases/               # Release documentation
```

### Example Programs
```
examples/                   # Sample programs and tutorials
├── README.md               # Examples documentation
├── PROGRAMS_INDEX.md       # Program index and descriptions
├── BASIC/                  # BASIC language examples
├── Logo/                   # Logo turtle graphics examples
├── PILOT/                  # PILOT educational examples
├── Python/                 # Python scripting examples
├── basic/                  # Additional BASIC examples
├── logo/                   # Additional Logo examples
├── pilot/                  # Additional PILOT examples
├── games/                  # Game development examples
├── sample_*.py             # Sample program files
└── analysis_results.json   # Program analysis results
```

### Marketing & Community
```
marketing/                  # Marketing materials and outreach
├── README.md               # Marketing documentation
├── marketing_summary.md    # Marketing strategy summary
├── graphics/               # Marketing graphics and assets
├── social_media/           # Social media content
├── devto_article.md        # Dev.to article content
├── educational_outreach_email.txt # Educational outreach
└── REDDIT_SIDEPROJECT_ANNOUNCEMENT.md # Reddit announcement
```

### Release Management
```
release/                    # Release management
└── v1.1/                   # Version 1.1 release files
```

### Configuration & Metadata
```
.github/                    # GitHub workflows & templates
.vscode/                    # VS Code configuration
.gitignore                  # Git ignore patterns
.pre-commit-config.yaml     # Pre-commit hooks
.Time_Warp/                 # Application data directory
└── .venv/                  # Python virtual environment
```

## 🎯 Key Files

### Primary Entry Points
- `timewarp.py` - Main application entry point
- `src/timewarp/main.py` - Core application module (formerly Time_Warp.py)
- `scripts/launch.py` - Cross-platform launcher

### Configuration
- `Time_Warp.code-workspace` - VS Code workspace settings
- `pyproject.toml` - Modern Python project configuration
- `requirements.txt` - Runtime dependencies
- `pytest.ini` - Test configuration

### Testing
- `tests/verification/` - Master verification suite
- `tests/unit/` - Unit test modules
- `tests/integration/` - Integration test modules
- `scripts/run_all_tests.py` - Master test runner

## 🚀 Usage

### Direct Execution
```bash
python timewarp.py          # Main entry point
python -m src.timewarp.main # Module execution
```

### Via Scripts
```bash
python scripts/launch.py   # Cross-platform launcher
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