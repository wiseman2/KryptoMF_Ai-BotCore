# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Install Dependencies

```bash
# Navigate to the bot directory
cd Public/KryptoMF_Ai-BotCore

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Bot (Interactive Setup)

```bash
python cli.py --paper-trading
```

The bot will prompt you for configuration:

```
============================================================
Welcome to KryptoMF Bot!
============================================================

No configuration found. Let's set up your bot.

Available exchanges:
  1. binance_us
  2. coinbase
  3. kraken

Select exchange (1-3): 1

⚠️  Your API keys will be stored securely in your OS keychain
⚠️  Make sure your API keys have TRADING permissions but NO WITHDRAWAL permissions

Enter API key: your_api_key_here
Enter API secret: your_api_secret_here

Which coin pair? (e.g., BTC/USD): BTC/USD

Available strategies:
  1. grid - Grid trading with DCA
  2. dca - Dollar cost averaging
  3. momentum - Momentum trading

Select strategy (1-3): 1

Grid spacing (%): 2.5
Number of grid levels: 10
Position size (USD): 100

Max position size (USD) [1000]: 1000
Stop loss (%) [5]: 5

Save this configuration? (y/n): y
✓ Configuration saved to config/bot_config.yaml

Starting bot...
```

### 3. Or Use a Config File

Create `config/bot_config.yaml`:

```yaml
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
paper_trading: true
```

Then run:

```bash
python cli.py --config config/bot_config.yaml
```

### 4. Watch the Bot Run

You'll see console output like this:

```
[2025-10-31 12:00:00] INFO - Initializing bot engine...
[2025-10-31 12:00:00] INFO - Exchange: binance_us
[2025-10-31 12:00:00] INFO - Symbol: BTC/USD
[2025-10-31 12:00:00] INFO - Strategy: grid_trading
[2025-10-31 12:00:00] INFO - Paper trading: True
[2025-10-31 12:00:01] INFO - Initializing exchange connector...
[2025-10-31 12:00:01] INFO - Connecting to binance_us...
[2025-10-31 12:00:02] INFO - ✓ Connected to binance_us
[2025-10-31 12:00:02] INFO - ✓ Loaded 500 markets
[2025-10-31 12:00:02] INFO - Initializing trading strategy...
[2025-10-31 12:00:02] INFO - Grid Trading Strategy initialized:
[2025-10-31 12:00:02] INFO -   Grid spacing: 2.5%
[2025-10-31 12:00:02] INFO -   Grid levels: 10
[2025-10-31 12:00:02] INFO -   Position size: $100
[2025-10-31 12:00:02] INFO - ✓ Bot engine initialized
============================================================
Bot started successfully!
============================================================
⚠️  PAPER TRADING MODE - No real orders will be placed

============================================================
Iteration #1
============================================================
[2025-10-31 12:00:03] INFO - Fetching market data for BTC/USD
[2025-10-31 12:00:03] INFO - Current price: $67,450.00
[2025-10-31 12:00:03] INFO - No active grid orders - placing initial grid
============================================================
Placing Grid Orders
============================================================
[2025-10-31 12:00:03] INFO -   BUY: 0.00148148 @ $67,450.00
[2025-10-31 12:00:03] INFO -   BUY: 0.00151976 @ $65,762.50
[2025-10-31 12:00:03] INFO -   BUY: 0.00155993 @ $64,118.44
...
[2025-10-31 12:00:03] INFO -   SELL: 0.00144444 @ $69,137.50
[2025-10-31 12:00:03] INFO -   SELL: 0.00140845 @ $70,866.19
============================================================
✓ Placed 20 grid orders
============================================================
[2025-10-31 12:00:03] INFO - Next check in 60 seconds...
```

### 5. Stop the Bot

Press `Ctrl+C` to stop the bot gracefully:

```
^C
[2025-10-31 12:05:00] INFO - Received shutdown signal
[2025-10-31 12:05:00] INFO - Stopping bot...
[2025-10-31 12:05:00] INFO - Strategy state: {'grid_orders': [...], 'current_price': 67450.0}
[2025-10-31 12:05:00] INFO - Disconnecting from binance_us
[2025-10-31 12:05:00] INFO - ✓ Disconnected
[2025-10-31 12:05:00] INFO - Bot stopped
[2025-10-31 12:05:00] INFO - Bot stopped successfully
```

## 📝 Configuration Options

### Exchange Options
- `binance_us` - Binance.US
- `coinbase` - Coinbase Pro
- `kraken` - Kraken

### Strategy Options

#### Grid Trading
```yaml
strategy: grid_trading
strategy_params:
  grid_spacing: 2.5      # % spacing between levels
  grid_levels: 10        # Number of levels
  position_size: 100     # USD per level
```

#### DCA (Dollar Cost Averaging)
```yaml
strategy: dca
strategy_params:
  interval_hours: 24     # Hours between purchases
  amount_usd: 100        # Amount per purchase
  max_price: 70000       # Optional: max price to buy
  min_price: 60000       # Optional: min price to buy
```

### Risk Management
```yaml
risk:
  max_position_size: 1000    # Maximum total position
  stop_loss_percent: 5       # Stop loss %
  take_profit_percent: 10    # Take profit % (optional)
```

## 🔒 Security

### API Key Storage
- API keys are stored in your OS keychain (macOS Keychain, Windows DPAPI, Linux Secret Service)
- Keys are NEVER logged or transmitted
- Keys are encrypted at rest

### API Key Permissions
⚠️ **IMPORTANT**: Your API keys should have:
- ✅ **TRADING** permissions (to place orders)
- ❌ **NO WITHDRAWAL** permissions (for security)

## 🐛 Troubleshooting

### "No module named 'ccxt'"
```bash
pip install -r requirements.txt
```

### "Exchange not supported"
Make sure you're using one of the supported exchanges:
- binance_us
- coinbase
- kraken

### "No API credentials found"
Run the interactive setup first:
```bash
python cli.py
```

Or add credentials to your config file.

## 📚 Next Steps

- Read the [full documentation](docs/)
- Check out [example strategies](examples/)
- Join the [community](https://github.com/yourusername/KryptoMF_Ai-BotCore/discussions)
- [Contribute](../CONTRIBUTING.md) to the project

## ⚠️ Disclaimer

This software is for educational purposes. Cryptocurrency trading carries significant risk. Only trade with money you can afford to lose. This is not financial advice.

