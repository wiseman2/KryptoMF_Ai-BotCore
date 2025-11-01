# KryptoMF_Ai Bot Core - Still  in Developement! Not Functional

## 🆓 Open Source Trading Bot Engine

The **KryptoMF_Ai Bot Core** is a fully functional, open-source cryptocurrency trading bot engine. Run it from your code editor, configure via YAML files, and monitor via console logs - **no GUI needed**.

## ✨ Features

- ✅ **Fully functional CLI bot** - Works just like FlexGrid
- ✅ **Run from code editor** - PyCharm, VS Code, or any Python environment
- ✅ **Simple configuration** - YAML/JSON files or interactive prompts
- ✅ **Console monitoring** - Clear print statements showing all activity
- ✅ **All exchange connectors** - Binance.US, Coinbase, Kraken, and more
- ✅ **Basic strategies** - Grid trading, DCA, momentum
- ✅ **Technical indicators** - MACD, RSI, EMA, Bollinger Bands
- ✅ **Backtesting framework** - Test strategies on historical data
- ✅ **Security-critical code** - Key storage and order signing (auditable)
- ✅ **Plugin system** - Create and share your own plugins

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

See the [docs/](docs/) directory for detailed documentation.

## 📝 License

MIT License - Free to use, modify, and distribute.

## ⚠️ Disclaimer

This software is for educational purposes. Cryptocurrency trading carries significant risk. Only trade with money you can afford to lose. This is not financial advice.

