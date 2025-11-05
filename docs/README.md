# KryptoMF Bot Core Documentation

Welcome to the KryptoMF Bot Core documentation! This directory contains comprehensive guides for using and understanding the trading bot.

## 📚 Documentation Index

### Getting Started
- **[Main README](../README.md)** - Project overview, installation, and quick start guide
- **[Quick Start Guide](QUICKSTART.md)** - Get up and running in 5 minutes
- **[Security Guide](SECURITY.md)** - Security best practices, credential management, and secure deployment

### Trading Features
- **[Strategy Enhancements](STRATEGY_ENHANCEMENTS.md)** - Detailed guide to advanced DCA, enhanced strategies, and trailing orders
- **[Fees and Profit Calculation](FEES_AND_PROFIT_CALCULATION.md)** - Understanding trading fees, profit calculations, and order types
- **[State Persistence & Reliability](STATE_PERSISTENCE_AND_RELIABILITY.md)** - State saving, connectivity monitoring, trailing management
- **[Backtesting Guide](BACKTESTING.md)** - How to backtest strategies with historical data

### Development & Reference
- **[CHANGELOG](CHANGELOG.md)** - Version history and migration guides
- **[Build Guide](BUILD.md)** - How to build standalone executables
- **[Contributing](CONTRIBUTING.md)** - How to contribute to the project
- **[Testing Guide](TESTING.md)** - How to run tests and write new ones
- **[Project Summary](PROJECT_SUMMARY.md)** - Comprehensive project overview

### Configuration
- **[Example Configurations](../config/)** - Sample configuration files for different strategies
  - `bot_config.yaml` - Basic configuration template
  - `test_dca_config.yaml` - DCA strategy with all features enabled

### API Reference
- **[Strategy Development](STRATEGY_DEVELOPMENT.md)** *(Coming soon)* - How to create custom trading strategies
- **[Exchange Integration](EXCHANGE_INTEGRATION.md)** *(Coming soon)* - Adding support for new exchanges

---

## 🎯 Quick Links by Topic

### For New Users
1. Start with the [Main README](../README.md) to install and set up the bot
2. Follow the [Quick Start Guide](QUICKSTART.md) to get running in 5 minutes
3. Read [Security Guide](SECURITY.md) to understand credential management
4. Review [Fees and Profit Calculation](FEES_AND_PROFIT_CALCULATION.md) to configure trading parameters
5. Try [Backtesting](BACKTESTING.md) before live trading

### For Traders
- **Strategy Configuration**: [Strategy Enhancements](STRATEGY_ENHANCEMENTS.md)
- **Understanding Fees**: [Fees and Profit Calculation](FEES_AND_PROFIT_CALCULATION.md)
- **Reliability Features**: [State Persistence & Reliability](STATE_PERSISTENCE_AND_RELIABILITY.md)
- **Testing Strategies**: [Backtesting Guide](BACKTESTING.md)
- **Security Best Practices**: [Security Guide](SECURITY.md)

### For Developers
- **Project Structure**: See [Main README](../README.md#project-structure)
- **Contributing**: [Contributing Guide](CONTRIBUTING.md)
- **Building**: [Build Guide](BUILD.md)
- **Testing**: [Testing Guide](TESTING.md)
- **Security**: [Security Guide](SECURITY.md)

---

## 📖 Document Summaries

### [Main README](../README.md)
The main project documentation covering:
- What KryptoMF Bot Core is
- Installation instructions
- Quick start guide
- Feature overview
- Project structure
- License information

### [Security Guide](SECURITY.md)
Comprehensive security documentation including:
- Secure credential storage using OS keychain
- API key management
- Passphrase support for exchanges
- Secrets redaction in logs
- Security best practices
- Threat model and mitigations

### [Fees and Profit Calculation](FEES_AND_PROFIT_CALCULATION.md)
Detailed guide on trading economics:
- Why fees matter
- Maker vs taker fees
- Profit calculation formulas
- Order types (market, limit, trailing)
- RSI rising check explanation
- Real-world examples
- Troubleshooting common issues

### [Backtesting Guide](BACKTESTING.md)
How to test strategies with historical data:
- Interactive setup with guided prompts
- Configurable parameters (balance, amount, profit %)
- Real-time progress with active trade metrics
- Fetching and caching historical data
- Running backtest simulations
- Analyzing results and performance metrics
- Session logging for review and sharing
- Data caching and management

### [Strategy Enhancements](STRATEGY_ENHANCEMENTS.md)
Detailed guide to advanced trading strategies:
- Advanced DCA with profit application
- Enhanced DCA with indicator-based decisions
- Grid trading with indicator validation
- Trailing order support
- Technical indicators configuration

### [State Persistence & Reliability](STATE_PERSISTENCE_AND_RELIABILITY.md)
Enterprise-grade reliability features:
- State persistence and recovery
- Connectivity monitoring
- Trailing state management
- Smart indicator checks
- Configuration reference
- Troubleshooting guide

### [CHANGELOG](CHANGELOG.md)
Version history and migration guides:
- All changes by version
- New features and improvements
- Breaking changes
- Migration instructions
- Configuration updates

---

## 🔗 Related Projects

### KryptoMF_AI Trading Bot
The complete KryptoMF_AI Trading Bot system includes:
- **KryptoMF_Ai-BotCore** (this project) - Core trading engine and CLI
- **KryptoMF_Ai-BotDashboard** - Web-based dashboard, monitoring, and advanced features

The BotDashboard provides:
- Real-time portfolio monitoring
- Advanced charting and analytics
- Multi-bot management
- Historical performance tracking
- Web-based configuration interface
- Alert and notification system

**Note**: KryptoMF_Ai-BotCore is a fully functional standalone trading bot. The BotDashboard adds a web interface and advanced monitoring capabilities but is not required for trading operations.

---

## 📝 Documentation Standards

All documentation in this project follows these standards:

### Formatting
- Use Markdown format
- Include table of contents for long documents
- Use code blocks with syntax highlighting
- Include examples for complex concepts

### Content
- Start with a clear purpose statement
- Provide step-by-step instructions
- Include real-world examples
- Add troubleshooting sections
- Link to related documentation

### Maintenance
- Keep documentation in sync with code
- Update examples when features change
- Add new guides as features are added
- Archive outdated information

---

## 🤝 Contributing to Documentation

We welcome documentation improvements! When contributing:

1. **Accuracy** - Ensure all information is correct and tested
2. **Clarity** - Write for users of all skill levels
3. **Examples** - Include practical, working examples
4. **Links** - Cross-reference related documentation
5. **Updates** - Keep existing docs current when adding features

See the [Contributing section](../README.md#contributing) in the main README for more details.

---

## 📄 License

This documentation is part of the KryptoMF Bot Core project and is licensed under the **Polyform Noncommercial License 1.0.0**.

**Key Points:**
- ✅ Free for personal use
- ✅ Free for educational use
- ✅ Free for research
- ❌ Commercial use requires separate license

See [LICENSE](../LICENSE) for full details.

---

## 💬 Getting Help

If you need help:

1. **Check the docs** - Most questions are answered here
2. **Search issues** - Someone may have had the same question
3. **Ask questions** - Open a GitHub issue with the `question` label
4. **Report bugs** - Open a GitHub issue with the `bug` label

---

## 🗺️ Documentation Roadmap

Upcoming documentation:

- [ ] Strategy Development Guide
- [ ] Exchange Integration Guide
- [ ] Advanced Configuration Guide
- [ ] Performance Tuning Guide
- [ ] Deployment Guide
- [ ] API Reference
- [ ] Troubleshooting Guide
- [ ] FAQ

---

**Last Updated**: 2025-11-03

For the latest documentation, visit the [GitHub repository](https://github.com/yourusername/KryptoMF_Ai-BotCore).

