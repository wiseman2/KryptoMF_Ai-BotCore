# Contributing to KryptoMF Bot Core

Thank you for your interest in contributing to the KryptoMF Bot Core! This is an open source project and we welcome contributions from the community.

## 🎯 What Can You Contribute?

### 1. Exchange Plugins
- Add support for new cryptocurrency exchanges
- Improve existing exchange connectors
- Add WebSocket support for real-time data

### 2. Trading Strategies
- Implement new trading strategies
- Improve existing strategies
- Add backtesting capabilities

### 3. Technical Indicators
- Add new technical indicators
- Optimize existing indicators
- Improve calculation accuracy

### 4. Core Improvements
- Bug fixes
- Performance improvements
- Code quality improvements
- Documentation improvements

### 5. Security Improvements
- Security audits
- Improve key storage
- Enhance order signing
- Add security tests

## 🚀 Getting Started

### 1. Fork the Repository

Fork the repository on GitHub and clone your fork:

```bash
git clone https://github.com/yourusername/KryptoMF_Ai-BotCore.git
cd KryptoMF_Ai-BotCore
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install development dependencies
pip install -r requirements-dev.txt
```

### 3. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 4. Make Your Changes

- Write clean, readable code
- Follow PEP 8 style guidelines
- Add docstrings to functions and classes
- Write tests for new features
- Update documentation as needed

### 5. Run Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run linting
black src/
flake8 src/
mypy src/
```

### 6. Commit Your Changes

```bash
git add .
git commit -m "Add feature: your feature description"
```

Use clear, descriptive commit messages:
- `Add feature: grid trading strategy`
- `Fix bug: order signing for Binance`
- `Improve: WebSocket reconnection logic`
- `Docs: update exchange plugin guide`

### 7. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## 📝 Code Style Guidelines

### Python Style
- Follow PEP 8
- Use type hints
- Write docstrings (Google style)
- Maximum line length: 100 characters
- Use `black` for formatting

### Example:

```python
def calculate_indicator(
    data: List[float],
    period: int = 14
) -> List[float]:
    """
    Calculate technical indicator.
    
    Args:
        data: Price data
        period: Calculation period
        
    Returns:
        Indicator values
    """
    # Implementation
    pass
```

## 🔒 Security Guidelines

### CRITICAL: Security-Critical Code

If you're working on security-critical code (key storage, order signing):

1. **Never log secrets** - Use the secure logger
2. **Never transmit secrets** - Keys stay local
3. **Use OS-native security** - Keychain, DPAPI, Secret Service
4. **Add security tests** - Verify no secret leakage
5. **Document security decisions** - Explain why you did it that way

### Example:

```python
# ❌ BAD - Logs API key
logger.info(f"Using API key: {api_key}")

# ✅ GOOD - Redacts API key
logger.info("Using API key: ****")
```

## 🧪 Testing Guidelines

### Write Tests For:
- New features
- Bug fixes
- Edge cases
- Security-critical code

### Test Structure:

```python
def test_feature_name():
    """Test description"""
    # Arrange
    input_data = [1, 2, 3]
    
    # Act
    result = function_to_test(input_data)
    
    # Assert
    assert result == expected_output
```

## 📚 Documentation Guidelines

### Update Documentation When:
- Adding new features
- Changing APIs
- Adding plugins
- Fixing bugs

### Documentation Locations:
- Code docstrings
- README.md
- docs/ directory
- Example configs

## 🤝 Community Guidelines

### Be Respectful
- Be kind and respectful to others
- Welcome newcomers
- Help others learn
- Give constructive feedback

### Communication Channels
- GitHub Issues: Bug reports and feature requests
- GitHub Discussions: Questions and ideas
- Discord: Community chat (coming soon)

## ⚖️ License

By contributing, you agree that:

1. **Your contributions are your own work** - You have the right to submit them
2. **You grant us a license** - To use your contributions under the project's license
3. **Your contributions are licensed** - Under the Polyform Noncommercial License 1.0.0
4. **We may dual-license** - We reserve the right to offer commercial licenses

### Important Notes

- **Noncommercial License** - This project uses Polyform Noncommercial, not MIT
- **Commercial Use** - Requires a separate commercial license from KnottyBranch
- **Your Rights** - You retain copyright to your contributions
- **Our Rights** - We can use contributions in both free and commercial versions

For more details, see the [LICENSE](LICENSE) file.

**Contact:** kryptomfai@gmail.com | https://kryptomfai.com

## ❓ Questions?

If you have questions, please:
1. Check existing documentation
2. Search GitHub Issues
3. Ask in GitHub Discussions
4. Join our Discord (coming soon)

Thank you for contributing! 🎉

