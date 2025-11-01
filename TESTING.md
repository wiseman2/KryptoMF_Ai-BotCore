## Testing Guide

Comprehensive testing guide for KryptoMF Bot.

## 📋 Test Coverage

We maintain high test coverage to ensure reliability:

- **Bot Instance**: Core bot functionality, lifecycle management
- **Grid Trading Strategy**: Grid placement, order fills, state management
- **DCA Strategy**: Purchase timing, price limits, statistics
- **CCXT Exchange**: Connection, orders, market data, paper trading
- **Utilities**: Logging, secret redaction

## 🚀 Running Tests

### Quick Start

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
python run_tests.py
```

### Using Pytest Directly

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_bot_instance.py

# Run specific test
pytest tests/test_bot_instance.py::TestBotInstance::test_bot_creation

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Test Output

```
================================ test session starts =================================
platform win32 -- Python 3.11.0, pytest-7.4.0, pluggy-1.3.0
rootdir: F:\Pycharm ExtraDriveSpace\KryptoMf_Ai\Public\KryptoMF_Ai-BotCore
plugins: cov-4.1.0, asyncio-0.21.0, mock-3.11.0
collected 45 items

tests/test_bot_instance.py ............                                        [ 26%]
tests/test_ccxt_exchange.py .............                                      [ 55%]
tests/test_dca_strategy.py ..........                                          [ 77%]
tests/test_grid_strategy.py ..........                                         [100%]

================================ 45 passed in 2.34s ==================================
```

## 📊 Coverage Report

After running tests with coverage, open `htmlcov/index.html` in your browser to see detailed coverage:

```bash
# Generate coverage report
pytest tests/ --cov=src --cov-report=html

# Open in browser (Windows)
start htmlcov/index.html

# Open in browser (Mac)
open htmlcov/index.html

# Open in browser (Linux)
xdg-open htmlcov/index.html
```

### Coverage Goals

- **Overall**: > 80%
- **Core modules**: > 90%
- **Strategies**: > 85%
- **Exchange connectors**: > 80%

## 🧪 Test Structure

```
tests/
├── __init__.py
├── conftest.py                 # Shared fixtures
├── test_bot_instance.py        # Bot instance tests
├── test_grid_strategy.py       # Grid trading tests
├── test_dca_strategy.py        # DCA strategy tests
├── test_ccxt_exchange.py       # Exchange connector tests
└── test_utils.py               # Utility tests (future)
```

## 🔧 Writing Tests

### Test Template

```python
"""
Tests for MyModule

Description of what this module does.
"""

import pytest
from unittest.mock import Mock, patch
from my_module import MyClass


class TestMyClass:
    """Test MyClass."""
    
    def test_creation(self):
        """Test object creation."""
        obj = MyClass()
        assert obj is not None
    
    def test_method(self):
        """Test a method."""
        obj = MyClass()
        result = obj.my_method()
        assert result == expected_value
    
    @patch('my_module.external_dependency')
    def test_with_mock(self, mock_dep):
        """Test with mocked dependency."""
        mock_dep.return_value = 'mocked'
        obj = MyClass()
        result = obj.method_using_dependency()
        assert result == 'expected'
```

### Using Fixtures

```python
def test_with_fixture(bot_config, mock_exchange):
    """Test using shared fixtures."""
    bot = BotInstance(bot_config)
    bot.exchange = mock_exchange
    # ... test code
```

### Mocking

```python
from unittest.mock import Mock, patch, MagicMock

# Mock an object
mock_obj = Mock()
mock_obj.method.return_value = 'value'

# Mock a class
@patch('module.ClassName')
def test_something(mock_class):
    mock_instance = Mock()
    mock_class.return_value = mock_instance
    # ... test code

# Mock multiple calls
mock_obj.method.side_effect = ['first', 'second', 'third']
```

## 🎯 Test Categories

### Unit Tests

Test individual components in isolation:

```bash
pytest tests/test_grid_strategy.py
```

### Integration Tests

Test components working together:

```bash
pytest tests/test_bot_instance.py
```

### Paper Trading Tests

Test with paper trading mode:

```bash
# All tests use paper trading by default
pytest tests/
```

## 🐛 Debugging Tests

### Run with Debug Output

```bash
# Show print statements
pytest tests/ -s

# Show full tracebacks
pytest tests/ --tb=long

# Stop on first failure
pytest tests/ -x

# Drop into debugger on failure
pytest tests/ --pdb
```

### VS Code Debugging

Add to `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Pytest",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": [
                "tests/",
                "-v"
            ],
            "console": "integratedTerminal"
        }
    ]
}
```

### PyCharm Debugging

1. Right-click on test file
2. Select "Debug 'pytest in test_...'"

## 📝 Test Checklist

Before committing code, ensure:

- [ ] All tests pass
- [ ] New code has tests
- [ ] Coverage hasn't decreased
- [ ] No print statements in tests (use logging)
- [ ] Tests are independent (can run in any order)
- [ ] Mocks are used for external dependencies
- [ ] Test names are descriptive

## 🔄 Continuous Integration

Tests run automatically on:

- Every commit (local pre-commit hook)
- Every pull request (GitHub Actions)
- Every merge to main (GitHub Actions)

### GitHub Actions Workflow

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements-dev.txt
      - run: pytest tests/ --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v3
```

## 🎨 Test Best Practices

### DO

✅ Test one thing per test
✅ Use descriptive test names
✅ Use fixtures for common setup
✅ Mock external dependencies
✅ Test edge cases
✅ Test error conditions
✅ Keep tests fast

### DON'T

❌ Test implementation details
❌ Make tests depend on each other
❌ Use real API calls
❌ Hardcode values (use fixtures)
❌ Skip tests without good reason
❌ Leave commented-out code

## 📚 Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [unittest.mock Guide](https://docs.python.org/3/library/unittest.mock.html)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

## 🆘 Troubleshooting

### Import Errors

```bash
# Make sure src is in path
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"

# Or use pytest with src in path (conftest.py handles this)
pytest tests/
```

### Fixture Not Found

```bash
# Make sure conftest.py is in tests/ directory
ls tests/conftest.py
```

### Tests Hanging

```bash
# Run with timeout
pytest tests/ --timeout=10
```

### Flaky Tests

```bash
# Run multiple times
pytest tests/ --count=10
```

## 📈 Improving Coverage

### Find Uncovered Lines

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

### Coverage by File

```bash
pytest tests/ --cov=src --cov-report=html
# Open htmlcov/index.html
```

### Add Tests for Uncovered Code

1. Identify uncovered lines in coverage report
2. Write tests to cover those lines
3. Run tests again to verify coverage increased

## 🎯 Next Steps

- [ ] Add integration tests with real exchanges (testnet)
- [ ] Add performance tests
- [ ] Add stress tests (many bots)
- [ ] Add security tests
- [ ] Set up automated testing in CI/CD

