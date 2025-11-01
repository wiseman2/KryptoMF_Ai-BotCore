# KryptoMF_Ai Bot Core- Still in Developement! Not Functional

## 🆓 Open Source Trading Bot Engine

The **KryptoMF_Ai Bot Core** is a fully functional, open-source cryptocurrency trading bot engine. Run it from your code editor, configure via YAML files, and monitor via console logs - **no GUI needed**.

## ✨ Features

### Core Functionality
- ✅ **Fully functional CLI bot** - Works standalone without any GUI
- ✅ **Run from code editor** - PyCharm, VS Code, or any Python environment
- ✅ **Simple configuration** - YAML/JSON files or interactive prompts
- ✅ **Console monitoring** - Clear print statements showing all activity
- ✅ **All exchange connectors** - Binance.US, Coinbase, Kraken, and more
- ✅ **Security-critical code** - Key storage and order signing (auditable)
- ✅ **Plugin system** - Create and share your own plugins

### Advanced Trading Strategies
- ✅ **Enhanced Grid Trading** - Indicator-validated grid orders (no blind buying)
- ✅ **Advanced DCA** - Profit application from subsequent sales to reduce cost basis
- ✅ **Enhanced DCA** - Indicator-based buying instead of time-based intervals
- ✅ **Trailing Orders** - Exchange-native trailing orders (Binance/Binance.US)
- ✅ **Technical Indicators** - RSI, MACD, EMA, Stochastic RSI, MFI, and more
- ✅ **Configurable Everything** - Select indicators, adjust thresholds, customize strategies

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/KryptoMF_Ai-BotCore.git
cd KryptoMF_Ai-BotCore

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run CLI bot
python cli.py
```

### First Run (Interactive Setup)

```
Welcome to KryptoMF Bot!
No configuration found. Let's set up your bot.

Which exchange? (binance_us/coinbase/kraken): binance_us
Enter API key: ****
Enter API secret: ****
Which coin pair? (e.g., BTC/USD): BTC/USD
Which strategy? (grid/dca/momentum): grid
Grid spacing (%): 2.5
Number of grid levels: 10
Position size (USD): 100

Configuration saved to config/bot_config.yaml
Starting bot...
```

### Using Config File

```yaml
# config/bot_config.yaml
exchange: binance_us
symbol: BTC/USD
strategy: grid_trading
strategy_params:
  grid_spacing: 2.5
  grid_levels: 10
  position_size: 100
risk:
  max_position_size: 1000
  stop_loss_percent: 5
```

```bash
# Run with config file
python cli.py --config config/bot_config.yaml

# Paper trading mode
python cli.py --config config/bot_config.yaml --paper-trading
```

## 📖 Documentation

### Getting Started
- **[Quick Start Guide](QUICKSTART.md)** - Get up and running in 5 minutes
- **[Strategy Enhancements](STRATEGY_ENHANCEMENTS.md)** - Detailed guide to advanced DCA, enhanced strategies, and trailing orders
- **[Configuration Example](config/strategy_config_example.yaml)** - Comprehensive configuration template with all options

### Development
- **[Build Guide](BUILD.md)** - How to build standalone executables
- **[Contributing](CONTRIBUTING.md)** - How to contribute to the project
- **[Testing Guide](TESTING.md)** - How to run tests and write new ones

### Key Features Documentation

#### Advanced DCA Strategy
The advanced DCA strategy applies profit from subsequent sales to reduce the cost basis of previous purchases, making them easier to sell at profit. See [STRATEGY_ENHANCEMENTS.md](STRATEGY_ENHANCEMENTS.md#1-advanced-dca-strategy-advanced_dcapy) for details.

**Example:**
```
Buy #1: 1 BTC @ $50,000
Buy #2: 1 BTC @ $48,000
Sell #2: 1 BTC @ $49,000 (profit: $1,000)

After applying profit to Buy #1:
Buy #1 new cost: $49,240 (reduced from $50,000)
```

#### Enhanced DCA with Indicators
Instead of time-based buying, the enhanced DCA uses technical indicators (RSI, MACD, EMA, etc.) to identify optimal entry points. See [STRATEGY_ENHANCEMENTS.md](STRATEGY_ENHANCEMENTS.md#2-enhanced-dca-strategy-dcapy) for configuration.

#### Grid Trading with Indicator Validation
Grid orders are validated with technical indicators before placement to prevent blind buying in unfavorable market conditions. See [STRATEGY_ENHANCEMENTS.md](STRATEGY_ENHANCEMENTS.md#3-grid-trading-strategy-grid_tradingpy) for details.

#### Exchange-Native Trailing Orders
For exchanges that support it (Binance/Binance.US), trailing orders are placed directly on the exchange to protect against power outages, internet issues, and computer crashes. See [STRATEGY_ENHANCEMENTS.md](STRATEGY_ENHANCEMENTS.md#4-trailing-order-support) for implementation details.

**⚠️ Important:** Always place trailing sell orders immediately after buy orders to protect your position even if the bot crashes.

## 🔗 Related Projects

This is part of the **KryptoMF_Ai Ecosystem**:

- **[KryptoMF_Ai-BotCore](https://github.com/yourusername/KryptoMF_Ai-BotCore)** (This Repository) - Open-source CLI trading bot engine
- **[KryptoMF_Ai-BotDashboard](https://github.com/yourusername/KryptoMF_Ai-BotDashboard)** - Premium GUI for multi-bot management
- **[KryptoMF_Ai Web Platform](https://kryptomultiflexai.com)** - AI signal subscription service

## 📝 License

MIT License - Free to use, modify, and distribute.

## ⚠️ Disclaimer

This software is for educational purposes. Cryptocurrency trading carries significant risk. Only trade with money you can afford to lose. This is not financial advice.

