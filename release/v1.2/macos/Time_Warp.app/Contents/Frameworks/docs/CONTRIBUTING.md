# Contributing to Time_Warp IDE

Welcome to the Time_Warp IDE project! We're excited to have you contribute to this educational programming environment.

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- Git
- A GitHub account

### Setting Up Development Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Time_WarpIDE/Time_Warp.git
   cd Time_Warp
   ```

2. **Run the automated setup:**
   ```bash
   ./setup_dev.sh
   ```

3. **Manual setup (if needed):**
   ```bash
   # Create and activate virtual environment
   python3 -m venv .Time_Warp
   source .Time_Warp/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Install pre-commit hooks
   pre-commit install
   ```

## 🏗️ Project Structure

```
Time_Warp/
├── Time_Warp.py                 # Main application entry point
├── core/                       # Core interpreter and language engines
│   ├── interpreter.py          # Central execution engine
│   ├── languages/             # Language-specific executors
│   ├── editor/                # Enhanced code editor components
│   └── hardware/              # Hardware integration modules
├── tools/                     # Utility tools and theme management
├── plugins/                   # Plugin system and extensions
├── gui/                       # GUI components and dialogs
├── games/                     # Game engine and examples
├── examples/                  # Sample programs and demos
├── tests/                     # Test suites
└── .github/                   # GitHub workflows and templates
```

## 🧪 Development Workflow

### Running Time_Warp IDE
```bash
# Activate virtual environment
source .Time_Warp/bin/activate

# Run the IDE
python Time_Warp.py
```

### Testing
```bash
# Run all tests
python run_tests.py

# Run specific test categories
python -m pytest tests/ -v
```

### Code Quality
```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy Time_Warp.py core/

# Run pre-commit hooks manually
pre-commit run --all-files
```

## 📝 Coding Standards

### Code Style
- Use **Black** for code formatting (line length: 88)
- Follow **PEP 8** naming conventions
- Use **type hints** where appropriate
- Write **docstrings** for all public functions and classes

### File Organization
- **Test files**: `test_*.py` for unit tests, `*_test.py` for integration tests
- **Language demos**: Use appropriate extensions (`.pilot`, `.bas`, `.logo`)
- **Documentation**: Use Markdown for all documentation files

### Commit Messages
Follow conventional commit format:
```
type(scope): brief description

Detailed explanation of the changes made.

- List specific changes
- Include any breaking changes
- Reference issues if applicable
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## 🎯 Contributing Guidelines

### 1. Fork and Branch
- Fork the repository to your GitHub account
- Create a feature branch: `git checkout -b feature/your-feature-name`

### 2. Make Changes
- Follow the coding standards above
- Add tests for new functionality
- Update documentation if needed
- Ensure all tests pass

### 3. Submit Pull Request
- Push to your fork: `git push origin feature/your-feature-name`
- Create a pull request with a clear description
- Link any related issues
- Wait for review and feedback

### 4. Code Review Process
- All PRs require at least one review
- Address feedback promptly
- Keep PRs focused and reasonably sized
- Update your branch if requested

## 🐛 Bug Reports

When reporting bugs, please include:
- **OS and Python version**
- **Steps to reproduce**
- **Expected vs actual behavior**
- **Error messages or logs**
- **Screenshots if relevant**

Use the bug report template in `.github/ISSUE_TEMPLATE/`

## 💡 Feature Requests

For new features:
- Check existing issues first
- Provide clear use cases
- Consider implementation complexity
- Be open to discussion and alternatives

## 🏷️ Areas for Contribution

### High Priority
- **Language Support**: Add new programming languages
- **Educational Tools**: Learning assistants and tutorials  
- **Testing**: Improve test coverage and edge cases
- **Documentation**: User guides and API documentation

### Medium Priority
- **UI/UX**: Interface improvements and accessibility
- **Performance**: Optimization and profiling
- **Plugins**: New plugin development
- **Hardware Integration**: IoT and sensor support

### Good First Issues
Look for issues labeled `good-first-issue` or `help-wanted`

## 🔧 Development Tips

### Adding New Languages
1. Create executor class in `core/languages/new_language.py`
2. Implement required methods following existing patterns
3. Register in `core/interpreter.py`
4. Add syntax highlighting support
5. Create test programs and unit tests

### Plugin Development
- See `plugins/sample_plugin/` for template
- Follow plugin API conventions
- Include proper initialization and cleanup
- Add configuration options if needed

### Testing Best Practices
- Write tests for new features
- Test edge cases and error conditions
- Use meaningful test names
- Keep tests isolated and fast

## 📞 Getting Help

- **GitHub Discussions**: Ask questions and share ideas
- **Issues**: Report bugs or request features
- **Wiki**: Documentation and guides
- **Code Comments**: Inline documentation for complex logic

## 📄 License

By contributing to Time_Warp IDE, you agree that your contributions will be licensed under the same license as the project.

## 🙏 Recognition

Contributors are recognized in:
- GitHub contributors list
- Release notes for significant contributions
- Special mentions in documentation

Thank you for contributing to Time_Warp IDE! 🚀✨