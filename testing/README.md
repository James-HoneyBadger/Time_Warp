# Testing Directory

This directory contains all testing-related files and results.

## 📁 Structure

- `tests/` - Unit tests and test files
- `test_results/` - Test output and reports  
- `test_samples/` - Test data and sample files
- `test_requirements.txt` - Testing dependencies

## 🧪 Test Categories

### Unit Tests (`tests/`)
- Individual component tests
- Language-specific tests
- Feature validation tests
- Integration tests

### Test Results (`test_results/`)
- Test reports and logs
- Coverage reports
- Performance benchmarks
- CI/CD outputs

### Test Samples (`test_samples/`)
- Sample programs for testing
- Test data files
- Reference outputs
- Edge case examples

## 🚀 Running Tests

```bash
# From project root
python scripts/run_tests.py

# Production testing
python scripts/run_tests_production.py

# Integration tests
python scripts/integration_tests.py

# Install test dependencies
pip install -r testing/test_requirements.txt
```

## 📊 Test Coverage

All major components are tested:
- Core interpreter functionality
- Language compilers (BASIC, PILOT, Logo)
- GUI components
- Plugin system
- Game engine
- Hardware integration