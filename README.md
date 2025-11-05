# KryptoMF_Ai Bot Core -In Developement! May have Bugs... still testing

## 🆓 Open Source Trading Bot Engine

The **KryptoMF_Ai Bot Core** is a fully functional, open-source cryptocurrency trading bot engine. Run it from your code editor, configure via YAML files, and monitor via console logs - **no GUI needed**.

## ✨ Features

### Core Functionality
- ✅ **Fully functional CLI bot** - Works standalone without any GUI
- ✅ **Interactive status display** - Real-time positions, P&L, and trade statistics
- ✅ **Keyboard controls** - Pause, resume, status refresh, emergency stop
- ✅ **Run from code editor** - PyCharm, VS Code, or any Python environment
- ✅ **Simple configuration** - YAML/JSON files or interactive setup wizard
- ✅ **Configuration validation** - Helpful error messages and suggestions
- ✅ **All exchange connectors** - Binance.US, Coinbase Pro, Kraken, KuCoin, and more
- ✅ **Passphrase support** - Full support for Coinbase Pro, KuCoin, OKX
- ✅ **Security-critical code** - Key storage and order signing (100% auditable)
- ✅ **Plugin system** - Create and share your own plugins

### Security Features (100% Open Source)
- ✅ **OS Keychain Integration** - macOS Keychain, Windows DPAPI, Linux Secret Service
- ✅ **Encrypted Fallback Storage** - Fernet encryption for systems without keychain
- ✅ **Order Signing** - HMAC-SHA256, EdDSA with replay protection
- ✅ **Automatic Secrets Redaction** - Never logs API keys, secrets, or signatures
- ✅ **Multi-exchange Support** - Binance, Coinbase Pro, Kraken, KuCoin, and more
- ✅ **Passphrase Support** - Secure storage for exchanges requiring passphrases

### Advanced Trading Strategies
- ✅ **Enhanced Grid Trading** - Indicator-validated grid orders (no blind buying)
- ✅ **Advanced DCA** - Profit application from subsequent sales to reduce cost basis
- ✅ **Progressive Step-Down** - Each purchase requires progressively lower price (prevents clustering)
- ✅ **Enhanced DCA** - Indicator-based buying instead of time-based intervals
- ✅ **Trailing Orders** - Exchange-native trailing orders (Binance/Binance.US)
- ✅ **Technical Indicators** - RSI, MACD, EMA, Stochastic RSI, MFI, and more
- ✅ **RSI Rising Check** - Wait for momentum reversal before buying (optional)
- ✅ **Configurable Everything** - Select indicators, adjust thresholds, customize strategies

### Trading Fees & Profit Management
- ✅ **Fee-Aware Calculations** - Accounts for maker and taker fees in all profit calculations
- ✅ **Accurate Profit Targets** - Calculates exact sell price needed for target profit after fees
- ✅ **Multiple Order Types** - Market, limit, stop, trailing market, trailing limit, trailing stop
- ✅ **Configurable Trailing** - Set trailing percentages for buys and sells (e.g., 0.25% for 0.5-1% profit targets)
- ✅ **Transparent Logging** - Shows all fees, target prices, and expected profits

### Reliability & State Management (NEW!)
- ✅ **State Persistence** - Saves bot state to disk after every trade (no data loss on crashes)
- ✅ **Pending Order Tracking** - Tracks pending sell orders with purchase info for matching
- ✅ **Connectivity Monitoring** - Periodic internet checks with exponential backoff on failures
- ✅ **Trailing State Management** - Full bot-managed trailing with watermark tracking
- ✅ **Smart Indicator Checks** - Caches OHLCV data and skips checks when price hasn't moved
- ✅ **Automatic Recovery** - Resumes from saved state on restart, resets trailing after connectivity loss
- ✅ **80% API Reduction** - Smart caching reduces API calls by 80%

### Backtesting
- ✅ **Interactive Setup** - Guided prompts for coin pair, timeframe, and date range
- ✅ **Automatic Data Fetching** - Downloads historical data from exchanges via ccxt
- ✅ **Data Size Estimation** - Shows expected candles and MB before downloading
- ✅ **Local Caching** - Caches downloaded data to avoid re-downloading
- ✅ **Multiple Timeframes** - 1m, 5m, 15m, 1h, 4h, 1d support
- ✅ **Configurable Parameters** - Set initial balance, amount per trade, profit % for each backtest
- ✅ **Real-Time Metrics** - Shows cash, active trades, invested amount, unrealized P/L during backtest
- ✅ **Performance Metrics** - Win rate, profit factor, max drawdown, equity curve
- ✅ **Trade Analysis** - Detailed trade log with P&L for each trade
- ✅ **Visual Results** - ASCII equity curve and colored performance summary
- ✅ **Export Results** - Save backtest results to JSON for further analysis
- ✅ **Session Logging** - Every backtest saved to dedicated log file for review and sharing

### Logging & Monitoring
- ✅ **Session-Specific Logs** - Dedicated log file for each trading session (backtest/paper/live)
- ✅ **Dual Output** - Console (colored) + file (detailed with DEBUG level)
- ✅ **Automatic Rotation** - 10MB max per file, keeps 10 backups (100MB total history)
- ✅ **Organized Structure** - Separate folders for backtest/paper/live logs
- ✅ **Timestamped Files** - Easy to find specific sessions: `backtest_20251104_162530_BTC-USDT_advanced_dca.log`
- ✅ **Shareable Results** - Share log files to prove strategy performance
- ✅ **Debug Support** - Full DEBUG logging to files for troubleshooting

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

# Run backtest
python cli.py --config config/bot_config.yaml --backtest --backtest-data historical_data.csv

# Non-interactive mode (no status display)
python cli.py --config config/bot_config.yaml --no-interactive
```

### Interactive Controls

When running in interactive mode (default), you can control the bot with keyboard commands:

- **P** - Pause bot (stop trading but keep connection)
- **R** - Resume bot (continue trading)
- **S** - Show full status (refresh display)
- **Q** - Quit (stop bot and exit)
- **H** or **?** - Show help
- **Ctrl+C** - Emergency stop

The status display shows:
- Current bot status (running/paused/stopped)
- Real-time price and P&L
- Current positions
- Trade statistics (win rate, total trades)
- Uptime

## 💰 Trading Fees & Profit Calculation

The bot includes comprehensive fee management to ensure accurate profit calculations:

### Fee-Aware Profit Calculation

The bot automatically accounts for both buy and sell fees when calculating target sell prices:

```
Example: Buy BTC at $50,000 with 0.1% fees, 1% profit target
1. Buy cost with fee: $50,000 × 1.001 = $50,050
2. Add profit target: $50,050 × 1.01 = $50,550.50
3. Account for sell fee: $50,550.50 / 0.999 = $50,601.05
Result: Sell at $50,601.05 for exactly 1% profit after all fees
```

### Order Types

Choose from multiple order types for buying and selling:

- **Market Orders** - Execute immediately at current price (higher taker fees)
- **Limit Orders** - Set your price, wait for fill (lower maker fees)
- **Trailing Market/Limit** - Follow price movement with percentage offset
- **Trailing Stop** - Protect profits by trailing price upward

### Trailing Configuration

For small profit targets (0.5-1%), use tight trailing percentages:

```yaml
profit_target: 1.0  # 1% profit after fees
buy_order_type: limit
sell_order_type: trailing_market
trailing_sell_percent: 0.25  # Sell when price drops 0.25% from peak
```

### RSI Rising Check

Optionally wait for RSI momentum reversal before buying:

```yaml
indicators:
  rsi:
    enabled: true
    period: 14
    oversold: 30
    check_rising: true  # Wait for RSI to reverse before buying
```

This helps avoid "catching a falling knife" by ensuring the downtrend is reversing before entering a position.

See **[Fees and Profit Calculation Guide](docs/FEES_AND_PROFIT_CALCULATION.md)** for detailed explanations and examples.

## 📖 Documentation

### Getting Started
- **[Documentation Index](docs/README.md)** - Complete documentation index with all guides
- **[Quick Start Guide](docs/QUICKSTART.md)** - Get up and running in 5 minutes
- **[Strategy Enhancements](docs/STRATEGY_ENHANCEMENTS.md)** - Detailed guide to advanced DCA, enhanced strategies, and trailing orders
- **[Configuration Example](config/strategy_config_example.yaml)** - Comprehensive configuration template with all options

### Trading & Configuration
- **[Fees and Profit Calculation](docs/FEES_AND_PROFIT_CALCULATION.md)** - Understanding trading fees, profit calculations, RSI rising check, and order types
- **[Backtesting Guide](docs/BACKTESTING.md)** - How to backtest strategies with historical data
- **[Security Documentation](docs/SECURITY.md)** - Complete guide to credential storage, order signing, and security best practices

### Development
- **[Build Guide](docs/BUILD.md)** - How to build standalone executables
- **[Contributing](docs/CONTRIBUTING.md)** - How to contribute to the project
- **[Testing Guide](docs/TESTING.md)** - How to run tests and write new ones

## 🔐 Security

All security-critical code is **100% open source** for auditability:

### Credential Storage
- **OS Keychain** - Uses macOS Keychain, Windows DPAPI, or Linux Secret Service
- **Encrypted Fallback** - Fernet encryption for systems without keychain support
- **Never Plain Text** - Credentials are never stored in plain text
- **Passphrase Support** - Full support for exchanges requiring API passphrases

### Order Signing
- **HMAC-SHA256** - Standard signing for most exchanges (Binance, Kraken, etc.)
- **Coinbase Pro** - Specialized signing with CB-ACCESS headers
- **Replay Protection** - Timestamp/nonce prevents replay attacks
- **Signature Verification** - Constant-time comparison prevents timing attacks

### Secrets Redaction
- **Automatic Redaction** - All logs automatically redact sensitive data
- **Pattern Matching** - Detects API keys, secrets, tokens, signatures
- **Context-Aware** - Redacts based on key names and patterns
- **No Leakage** - Prevents accidental exposure in error messages

See **[Security Documentation](docs/SECURITY.md)** for complete details.

## 🧪 Backtesting

Test your strategies on historical data before risking real money!

### Interactive Backtesting (Recommended)

Simply run with `--backtest` and the bot will guide you through setup:

```bash
python cli.py --config config/bot_config.yaml --backtest
```

You'll be prompted to select:
1. **Trading Pair** - BTC/USDT (default), BTC/USD, ETH/USD, etc.
2. **Timeframe** - 1m, 5m, 15m, 1h (default), 4h, 1d
3. **Date Range** - Quick options (1 month, 3 months, 6 months, 1 year) or custom dates
4. **Backtest Parameters** - Initial balance, amount per trade, min profit % (uses config defaults)
5. **Data Size Estimate** - Shows expected candles and download size in MB

The bot will automatically:
- ✅ Download historical data from your configured exchange
- ✅ Cache data locally (no re-downloading)
- ✅ Show download progress
- ✅ Run backtest and display results

### Example Interactive Session

```
═══════════════════════════════════════════════════════════════════
                        BACKTEST DATA SETUP
═══════════════════════════════════════════════════════════════════

Step 1: Select Trading Pair
Examples: BTC/USD, ETH/USD, BTC/USDT, ETH/BTC
Enter trading pair (default: BTC/USDT): BTC/USD

Step 2: Select Timeframe
Available timeframes:
  1m     - 1 minute
  5m     - 5 minutes
  15m    - 15 minutes
  1h     - 1 hour
  4h     - 4 hours
  1d     - 1 day
Enter timeframe (default: 1h): 1h

Step 3: Select Date Range
Quick options:
  1 - Last 1 month
  2 - Last 3 months
  3 - Last 6 months
  4 - Last 1 year
  5 - Custom date range
Select option (1-5): 3

═══ DATA ESTIMATE ═══
Symbol:           BTC/USD
Timeframe:        1h (1 hour)
Date Range:       2024-05-02 to 2024-11-02
Duration:         184 days
Expected Candles: ~4,416
Estimated Size:   ~0.42 MB

Proceed with download? (y/n): y

Downloading historical data...
Progress: 4,416 / ~4,416 candles (100.0%)
```

### Manual CSV File (Optional)

You can also provide your own CSV file:

```bash
python cli.py --config config/bot_config.yaml \
  --backtest \
  --backtest-data data/BTC-USD-1h.csv
```

CSV format: `timestamp`, `open`, `high`, `low`, `close`, `volume`

```csv
timestamp,open,high,low,close,volume
1704067200,42150.5,42380.2,42100.0,42250.8,1234.56
1704070800,42250.8,42450.0,42200.0,42380.5,2345.67
...
```

### Backtest Results

The backtest engine provides:
- **Real-Time Progress** - Shows cash, active trades, invested amount, unrealized P/L every 1000 candles
- **Performance Summary** - Total return, win rate, max drawdown
- **Trade Statistics** - Winning/losing trades, average profit/loss, buy/sell counts
- **Trade Log** - Detailed log of all trades with timestamps and P&L
- **Equity Curve** - ASCII visualization of account equity over time
- **JSON Export** - Save results for further analysis
- **Session Log File** - Complete backtest log saved to `logs/backtest/` for review and sharing

**Example Progress Output:**
```
[2025-11-04 16:25:35] INFO - Progress: 1.3% (1000/74233 candles) | Cash: $90.00 | Active Trades: 1 | Invested: $10.00 | Unrealized P/L: +$0.50 | Total P/L: +$0.50 (+0.50%)
[2025-11-04 16:25:40] INFO - Progress: 2.7% (2000/74233 candles) | Cash: $70.00 | Active Trades: 3 | Invested: $30.00 | Unrealized P/L: +$2.15 | Total P/L: +$2.15 (+2.15%)
```

### Data Caching

Downloaded data is automatically cached in `data/historical/` to avoid re-downloading:
- Cache files are named: `{exchange}_{symbol}_{timeframe}_{start}_{end}.csv`
- Reusing the same parameters loads from cache instantly
- Delete cache files to force re-download

### Key Features Documentation

#### Advanced DCA Strategy
The advanced DCA strategy applies profit from subsequent sales to reduce the cost basis of previous purchases, making them easier to sell at profit. It also includes **progressive step-down** logic to prevent buying at similar price levels. See [STRATEGY_ENHANCEMENTS.md](docs/STRATEGY_ENHANCEMENTS.md#1-advanced-dca-strategy-advanced_dcapy) for details.

**Profit Application Example:**
```
Buy #1: 1 BTC @ $50,000
Buy #2: 1 BTC @ $48,000
Sell #2: 1 BTC @ $49,000 (profit: $1,000)

After applying profit to Buy #1:
Buy #1 new cost: $49,240 (reduced from $50,000)
```

**Progressive Step-Down Example (0.5% profit target):**
```
Purchase 1: $50,000 (no requirement)
Purchase 2: $49,750 or lower (0.5% drop required)
Purchase 3: $49,377 or lower (0.75% drop from #2)
Purchase 4: $48,823 or lower (1.125% drop from #3)
Purchase 5: $48,000 or lower (1.6875% drop from #4)
...
Purchase 10: ~$42,500 or lower (covers ~15% range)
```

This prevents buying multiple times at similar prices and ensures you're dollar-cost averaging across a meaningful price range.

#### Enhanced DCA with Indicators
Instead of time-based buying, the enhanced DCA uses technical indicators (RSI, MACD, EMA, etc.) to identify optimal entry points. See [STRATEGY_ENHANCEMENTS.md](docs/STRATEGY_ENHANCEMENTS.md#2-enhanced-dca-strategy-dcapy) for configuration.

#### Grid Trading with Indicator Validation
Grid orders are validated with technical indicators before placement to prevent blind buying in unfavorable market conditions. See [STRATEGY_ENHANCEMENTS.md](docs/STRATEGY_ENHANCEMENTS.md#3-grid-trading-strategy-grid_tradingpy) for details.

#### Exchange-Native Trailing Orders
For exchanges that support it (Binance/Binance.US), trailing orders are placed directly on the exchange to protect against power outages, internet issues, and computer crashes. See [STRATEGY_ENHANCEMENTS.md](docs/STRATEGY_ENHANCEMENTS.md#4-trailing-order-support) for implementation details.

**⚠️ Important:** Always place trailing sell orders immediately after buy orders to protect your position even if the bot crashes.

## 🔗 Related Projects

This is part of the **KryptoMF_Ai Ecosystem**:

- **[KryptoMF_Ai-BotCore](https://github.com/yourusername/KryptoMF_Ai-BotCore)** (This Repository) - Open-source CLI trading bot engine
- **[KryptoMF_Ai-BotDashboard](https://github.com/yourusername/KryptoMF_Ai-BotDashboard)** - Complete KryptoMF_AI Trading Bot with web-based dashboard, real-time monitoring, advanced charting, multi-bot management, and enhanced features
- **[KryptoMF_Ai Web Platform](https://kryptomultiflexai.com)** - AI signal subscription service

**Note**: KryptoMF_Ai-BotCore is a fully functional standalone trading bot. The BotDashboard provides additional web interface and advanced monitoring capabilities but is not required for trading operations.

## 📝 Licensing

This project is licensed under the **Polyform Noncommercial License 1.0.0**.

### What This Means

✅ **You CAN:**
- Use, modify, and share the code for **free** (noncommercial use)
- Redistribute original or modified versions at **no charge**
- Use for personal projects, research, teaching, and open-source collaboration
- Use for hobby trading and free community tools
- Accept voluntary donations (if access isn't conditioned on payment)
- Fork and give it away for free

❌ **You CANNOT (without a commercial license):**
- Sell this software or access to it
- Bundle it in a paid product or service
- Offer it hosted as a paid service (SaaS)
- Use it inside a company to generate revenue or deliver paid services
- Charge for support that includes distributing the software
- Use it for internal business systems tied to revenue

### What Counts as Commercial?

**Allowed (Noncommercial):**
- Personal trading bot for your own use
- Research and educational projects
- Teaching and academic use
- Open-source collaboration
- Free redistributions with the license intact
- Hobby trading (not for a business)
- Free community tools and services

**Not Allowed (Commercial):**
- Running a paid trading bot service for clients
- Selling the software or modified versions
- Including it in a paid product or SaaS platform
- Using it in a company's trading operations
- Offering paid support/hosting that includes the software
- Embedding it in internal business systems for profit

### Need a Commercial License?

We offer **commercial licenses** for companies and paid products/services.

📧 **Contact:** kryptomfai@gmail.com
🌐 **Website:** https://kryptomfai.com | https://kryptomfai.net

### Attribution Requirements

When using or redistributing this software, you must:
- ✅ Keep the copyright notice
- ✅ Include this license text
- ✅ Note any changes you made
- ❌ Do NOT use our trademarks or brand names without permission

### Warranty

This software is provided **"AS IS"** without warranties or liability. See the [LICENSE](LICENSE) file for full details.

---

**Copyright (c) 2024-2025 KnottyBranch (Ken Wiseman)**

For the full license text, see the [LICENSE](LICENSE) file or visit:
https://polyformproject.org/licenses/noncommercial/1.0.0/

## 📊 CLI Commands Reference

```bash
# Basic usage
python cli.py                                    # Interactive setup
python cli.py --config <file>                    # Use config file
python cli.py --config <file> --paper-trading    # Paper trading mode
python cli.py --config <file> --no-interactive   # No status display

# Backtesting
python cli.py --config <file> --backtest --backtest-data <csv>
python cli.py --config <file> --backtest --backtest-data <csv> --backtest-start 2024-01-01 --backtest-end 2024-12-31

# Logging
python cli.py --config <file> --verbose          # Verbose logging
```

## 📚 Documentation

### Core Documentation
- **[README](README.md)** - This file, project overview and quick start
- **[CHANGELOG](docs/CHANGELOG.md)** - Version history and migration guides

### Feature Documentation
- **[State Persistence & Reliability](docs/STATE_PERSISTENCE_AND_RELIABILITY.md)** - State saving, connectivity monitoring, trailing management
- **[Fees & Profit Calculation](docs/FEES_AND_PROFIT_CALCULATION.md)** - Trading fee integration and profit calculations


### Configuration
- **[Example DCA Config](config/test_dca_config.yaml)** - Complete configuration example with all options

---

## 🛠️ Development Status

**Current Version:** 0.3.0 (Beta)
**Last Updated:** 2025-11-03

### Completed Features ✅
- ✅ Core bot engine with multi-exchange support
- ✅ Interactive CLI with status display and keyboard controls
- ✅ Configuration validation with helpful error messages
- ✅ Security features (keychain, order signing, secrets redaction)
- ✅ Advanced trading strategies (DCA, Grid, Indicators)
- ✅ Backtesting framework with performance metrics
- ✅ Passphrase support for Coinbase Pro, KuCoin, OKX
- ✅ **State persistence with automatic recovery**
- ✅ **Connectivity monitoring with exponential backoff**
- ✅ **Trailing state management for bot-managed trailing**
- ✅ **Smart indicator checks with OHLCV caching**

### In Progress 🚧
- 🚧 Comprehensive test suite
- 🚧 Additional strategy plugins
- 🚧 Performance optimizations

### Planned Features 📋
- 📋 WebSocket support for real-time data (waiting for multibot plugin)
- 📋 Advanced order types (OCO, trailing stop-limit)
- 📋 Portfolio rebalancing strategies
- 📋 Machine learning signal integration

## ⚠️ Disclaimer

This software is for educational purposes. Cryptocurrency trading carries significant risk. Only trade with money you can afford to lose. This is not financial advice.

---

**Made with ❤️ by the KryptoMF_Ai Team**
