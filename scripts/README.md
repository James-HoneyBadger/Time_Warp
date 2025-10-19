# Development Scripts

This directory contains development utilities and setup scripts.

## 📝 Scripts

- `install_dependencies.py` - Automatic dependency installer
- `integration_tests.py` - Full integration test suite
- `run_tests.py` - Standard test runner
- `run_tests_production.py` - Production-ready test runner
- `setup_dev.sh` - Development environment setup

## 🚀 Usage

```bash
# Set up development environment
./setup_dev.sh

# Install dependencies
python install_dependencies.py

# Run tests
python run_tests.py

# Run production tests
python run_tests_production.py

# Run integration tests
python integration_tests.py
```

## 🛠️ Development Workflow

1. **Initial Setup**: Run `setup_dev.sh`
2. **Install Dependencies**: Run `install_dependencies.py`
3. **Development**: Make changes to code
4. **Testing**: Run `run_tests.py` for quick tests
5. **Integration**: Run `integration_tests.py` for full testing
6. **Production**: Run `run_tests_production.py` before releases