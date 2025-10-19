# Time_Warp IDE - Directory Structure (Updated)

## 📁 Current Project Organization

The Time_Warp IDE has been reorganized into a professional Python package structure:

```
Time_Warp/                             # Root project directory
├── 📄 timewarp.py                     # Main application entry point
├── 📄 README.md                       # Project documentation
├── 📄 CHANGELOG.md                    # Version history
├── 📄 requirements.txt                # Dependencies
├── 📄 pyproject.toml                  # Modern Python configuration
├── 📄 pytest.ini                     # Test configuration
├── 📄 Time_Warp.code-workspace        # VS Code workspace
├── 📄 .gitignore                      # Git ignore patterns
├── 📄 .pre-commit-config.yaml         # Code quality hooks
│
├── 📁 src/timewarp/                   # Main application package
│   ├── 📄 __init__.py                 # Package initialization
│   ├── 📄 main.py                     # Core application (formerly Time_Warp.py)
│   ├── 📁 core/                       # Core interpreter and language engines
│   │   ├── 📄 interpreter.py          # Central execution engine
│   │   ├── 📁 languages/              # Language-specific executors
│   │   │   ├── 📄 pilot.py            # PILOT language support
│   │   │   ├── 📄 basic.py            # BASIC language support
│   │   │   ├── 📄 logo.py             # Logo turtle graphics
│   │   │   ├── 📄 python_executor.py  # Python execution
│   │   │   └── 📄 javascript_executor.py # JavaScript support
│   │   ├── 📁 features/               # Advanced IDE features
│   │   ├── 📁 hardware/               # Hardware integration
│   │   ├── 📁 iot/                    # IoT device support
│   │   └── 📁 utilities/              # Core utility functions
│   ├── 📁 gui/                        # User interface components
│   │   ├── 📁 components/             # Reusable GUI components
│   │   └── 📁 dialogs/                # Dialog windows
│   ├── 📁 utils/                      # Tools & utilities (formerly tools/)
│   │   ├── 📄 theme.py                # Theme management (8 themes)
│   │   └── 📄 performance_bench.py    # Performance tools
│   └── 📁 games/                      # Game engine
│       ├── 📁 engine/                 # 2D game engine
│       └── 📁 samples/                # Sample games
│
├── 📁 tests/                          # Comprehensive test suite
│   ├── 📄 README.md                   # Testing documentation
│   ├── 📁 unit/                       # Unit tests
│   ├── 📁 integration/                # Integration tests
│   ├── 📁 fixtures/                   # Test data and fixtures
│   ├── 📁 verification/               # Verification test suite
│   ├── 📁 sample_outputs/             # Test output samples
│   └── 📁 test_results/               # Test execution results
│
├── 📁 docs/                           # Documentation
│   ├── 📄 PROJECT_STRUCTURE.md        # Project organization guide
│   ├── 📄 MODULAR_ARCHITECTURE.md     # Architecture documentation
│   ├── 📄 GITHUB_INTEGRATION.md       # GitHub integration guide
│   ├── 📄 compiler.md                 # Compiler documentation
│   ├── 📁 user-guide/                 # End-user documentation
│   ├── 📁 developer-guide/            # Contributing and development docs
│   ├── 📁 api/                        # API reference documentation
│   ├── 📁 languages/                  # Language-specific guides
│   ├── 📁 development/                # Development documentation
│   ├── 📁 guides/                     # General guides
│   ├── 📁 reports/                    # Project and development reports
│   └── 📁 releases/                   # Release documentation
│
├── 📁 examples/                       # Sample programs and tutorials
│   ├── 📄 README.md                   # Examples documentation
│   ├── 📄 PROGRAMS_INDEX.md           # Program index and descriptions
│   ├── 📁 BASIC/                      # BASIC language examples
│   ├── 📁 Logo/                       # Logo turtle graphics examples
│   ├── 📁 PILOT/                      # PILOT educational examples
│   ├── 📁 Python/                     # Python scripting examples
│   ├── 📁 basic/                      # Additional BASIC examples
│   ├── 📁 logo/                       # Additional Logo examples
│   ├── 📁 pilot/                      # Additional PILOT examples
│   └── 📁 games/                      # Game development examples
│
├── 📁 scripts/                        # Development and build scripts
│   ├── 📄 README.md                   # Scripts documentation
│   ├── 📄 prepare_release.sh          # Release preparation
│   ├── 📄 run_all_tests.py            # Master test runner
│   ├── 📄 install_dependencies.py     # Dependency installer
│   ├── 📄 launch.py                   # Cross-platform launcher
│   ├── 📄 start.sh                    # Quick start script
│   ├── 📁 build/                      # Build-related scripts
│   └── 📁 development/                # Development utilities
│
├── 📁 plugins/                        # Plugin system and extensions
│   ├── 📄 __init__.py                 # Plugin system initialization
│   ├── 📁 sample_plugin/              # Example plugin implementation
│   └── 📁 plugins/                    # Individual plugin implementations
│
├── 📁 marketing/                      # Marketing materials and outreach
│   ├── 📄 README.md                   # Marketing documentation
│   ├── 📄 marketing_summary.md        # Marketing strategy summary
│   ├── 📁 graphics/                   # Marketing graphics and assets
│   └── 📁 social_media/               # Social media content
│
├── 📁 release/                        # Release management
│   └── 📁 v1.1/                       # Version 1.1 release files
│
├── 📁 .github/                        # GitHub configuration
│   ├── 📄 copilot-instructions.md     # GitHub Copilot guide
│   └── 📁 workflows/                  # CI/CD automation workflows
│
├── 📁 .vscode/                        # VS Code configuration
├── 📁 .Time_Warp/                     # Application data directory
└── 📁 .venv/                          # Python virtual environment
```

## 🎯 Key Architecture Highlights

### Professional Python Package Structure
- **src/timewarp/** - Modern Python package layout following best practices
- **Proper entry points** - `timewarp.py` main entry, `src/timewarp/main.py` core app
- **Clean separation** - Core logic, GUI, utilities, and games properly separated

### Educational Focus
- **Multi-language support** - PILOT, BASIC, Logo, Python, JavaScript, Perl
- **Visual programming** - Turtle graphics for immediate feedback
- **Comprehensive examples** - 50+ sample programs across all languages
- **Progressive learning** - From simple to advanced concepts

### Professional Development
- **Modern configuration** - pyproject.toml, pytest.ini, pre-commit hooks
- **Comprehensive testing** - Unit, integration, and verification tests
- **Clean documentation** - Organized guides for users and developers
- **Plugin architecture** - Extensible system for custom functionality

### Project Management
- **Marketing ready** - Complete promotional materials and outreach
- **Release management** - Structured release process and documentation
- **CI/CD pipeline** - GitHub workflows for automation
- **Professional standards** - Code quality, testing, and documentation

## 📊 Project Statistics

| Category | Count | Description |
|----------|-------|-------------|
| **Languages Supported** | 6 | PILOT, BASIC, Logo, Python, JavaScript, Perl |
| **Built-in Themes** | 8 | 4 dark themes, 4 light themes |
| **Example Programs** | 50+ | Educational demonstrations |
| **Test Modules** | 30+ | Comprehensive test coverage |
| **Documentation Files** | 25+ | User and developer guides |
| **Plugin Examples** | 5+ | Extensible plugin architecture |

## 🚀 Usage Patterns

### Direct Execution
```bash
python timewarp.py          # Main entry point
python -m src.timewarp.main # Module execution
```

### Development Scripts
```bash
python scripts/launch.py   # Cross-platform launcher
./scripts/start.sh         # Quick start script
python scripts/run_all_tests.py # Test execution
```

### Package Installation
```bash
pip install -e .           # Development installation
pip install timewarp-ide  # Production installation (future)
```

## 🔧 Maintenance Guidelines

### Directory Organization Principles
1. **Single Responsibility** - Each directory has a clear, focused purpose
2. **Separation of Concerns** - Source code, tests, docs, and scripts separated
3. **Professional Standards** - Following Python package best practices
4. **Educational Focus** - All organization supports learning goals

### File Naming Conventions
- **Source files** - Clear, descriptive names following Python conventions
- **Test files** - `test_*.py` for unit tests, organized by category
- **Documentation** - Uppercase for main docs, lowercase for specific guides
- **Examples** - Language-specific directories with descriptive filenames

This clean, professional structure makes Time_Warp IDE maintainable, contributor-friendly, and ready for serious educational use and distribution.