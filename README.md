# KryptoMF_Ai Bot Core -In Developement! May have Bugs... still testing

##  Currently have tested working- 
#### 1- backtesting
#### 2- paper trading - Binance.US
#### 3- live trading - Advanced DCA - Binance.US 


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
- ✅ **Trailing Orders** - Exchange-native trailing stop orders (Binance/Binance.US)
- ✅ **Pending Order Tracking** - Prevents multiple simultaneous buy orders while waiting for trailing orders to fill
- ✅ **Technical Indicators** - RSI, MACD, EMA, Stochastic RSI, MFI, Price Drop, Price Rising
- ✅ **Indicator Agreement** - Configurable threshold (e.g., 60%) of indicators must agree before buying
- ✅ **Fully Configurable Indicators** - All indicator parameters (periods, thresholds, etc.) configurable from YAML
- ✅ **RSI Rising Check** - Wait for momentum reversal before buying (optional)
- ✅ **MACD Rising Check** - Confirm upward momentum before entry (optional)
- ✅ **1-Minute Candles** - Uses 1m timeframe for responsive indicator calculations

### Trading Fees & Profit Management
- ✅ **Fee-Aware Calculations** - Accounts for maker and taker fees in all profit calculations
- ✅ **Accurate Profit Targets** - Calculates exact sell price needed for target profit after fees
- ✅ **Multiple Order Types** - Market, limit, stop, trailing market, trailing limit, trailing stop
- ✅ **Configurable Trailing** - Set trailing percentages for buys and sells (e.g., 0.25% for 0.5-1% profit targets)
- ✅ **Transparent Logging** - Shows all fees, target prices, and expected profits

### Reliability & State Management
- ✅ **State Persistence** - Saves bot state to disk after every trade (no data loss on crashes)
- ✅ **Pending Buy Order Tracking** - Prevents multiple simultaneous buy orders while waiting for fills
- ✅ **Pending Sell Order Tracking** - Tracks sell orders within each purchase object with status tracking
- ✅ **Comprehensive Purchase Records** - Stores complete buy/sell order info, fees, timestamps, profit
- ✅ **Historical Trade Logging** - Completed trades saved to JSONL files for review and analysis
- ✅ **Automatic State Discovery** - Finds latest state file matching exchange + symbol + strategy
- ✅ **State File Cleanup** - Keeps only N most recent state files, auto-deletes old ones
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

The bot automatically accounts for both buy and sell fees when calculating target sell prices using **configured fee percentages** (not actual order fees):

```
Example: Buy at $690.98 with 0.4% fees, 1% profit target
1. Buy cost: $5.53
2. Buy fee (0.4%): $5.53 × 0.004 = $0.022
3. Sell fee estimate (0.4%): $5.53 × 0.004 = $0.022
4. Total fees: $0.044
5. Base with fees: ($5.53 + $0.044) / amount = $696.80 per unit
6. With profit + buffer: $696.80 × (1 + 0.01 + 0.002) = $705.16
Result: Sell at $705.16 for exactly 1% profit after all fees (2.05% above buy price)
```

**Key Features:**
- ✅ Uses configured maker/taker fee percentages (not order response fees)
- ✅ Accounts for both buy and sell fees in advance
- ✅ Adds 0.2% safety buffer to ensure profit target is met
- ✅ Recalculates fees when DCA is applied to reduce cost basis

### Order Types

Choose from multiple order types for buying and selling:

- **Market Orders** - Execute immediately at current price (higher taker fees)
- **Limit Orders** - Set your price, wait for fill (lower maker fees)
- **Trailing Market/Limit** - Follow price movement with percentage offset
- **Trailing Stop** - Protect profits by trailing price upward

### Trailing Orders Configuration

The bot supports exchange-native trailing stop orders on Binance/Binance.US:

```yaml
# Trailing buy orders (trails down to buy at lower price)
buy_order_type: trailing_market  # or trailing_limit
trailing_buy_percent: 0.3  # 0.3% trailing distance

# Trailing sell orders (trails up to sell at higher price)
sell_order_type: trailing_market  # or trailing_limit
trailing_sell_percent: 0.3  # 0.3% trailing distance
```

**How Trailing Orders Work:**
- **Buy Orders**: Use `STOP_LOSS_LIMIT` type, trail price DOWN to buy at lower price
- **Sell Orders**: Use `TAKE_PROFIT_LIMIT` type, trail price UP to sell at higher price
- **Pending Order Tracking**: Bot tracks pending trailing orders to prevent placing multiple simultaneous orders
- **Automatic Fill Detection**: When order fills, bot automatically places corresponding sell order

### Indicator Configuration

All indicators are fully configurable with custom periods and thresholds:

```yaml
strategy_params:
  indicator_agreement: 0.6  # 60% of indicators must agree before buying

  indicators:
    price_drop:
      enabled: false
      drop_percent: 1.0
      lookback_candles: 24

    rising_price:
      enabled: true  # Only buy when price is rising

    rsi:
      enabled: true
      period: 14
      oversold: 35
      overbought: 55
      check_rising: true  # Wait for RSI to reverse before buying

    stoch_rsi:
      enabled: true
      period: 14
      smoothing: 3
      oversold: 33
      overbought: 80

    ema:
      enabled: true
      length: 25  # Buy when price is below EMA

    macd:
      enabled: true
      fast: 12
      slow: 26
      signal: 9
      check_rising: true  # Wait for MACD to turn up

    mfi:
      enabled: true
      period: 14
      oversold: 25
```

**Indicator Agreement**: Set the percentage of enabled indicators that must agree before placing a buy order. For example, with `indicator_agreement: 0.6` and 5 indicators enabled, at least 3 must give buy signals.

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
Buy #1: 1 BTC @ $50,000 (cost: $50,000)
Buy #2: 1 BTC @ $48,000 (cost: $48,000)
Sell #2: 1 BTC @ $49,000 (profit: $1,000)

After min profit (1% = $480), remaining profit ($520) applied to Buy #1:
Buy #1 new cost: $50,000 - $520 = $49,480
Buy #1 new sell price: Recalculated with new cost + fees + profit target

If Buy #1 had a trailing sell order, it's automatically cancelled and replaced with new price
```

**DCA Logic:**
- ✅ **First purchase never applies DCA** - No previous purchase to apply to
- ✅ **Subsequent purchases apply DCA** - Profit from purchase #2+ reduces cost of previous purchase
- ✅ **Avoids double-counting** - DCA already counted in previous sale is subtracted from total profit
- ✅ **Trailing order management** - Automatically cancels and replaces trailing sell orders when DCA is applied

**Progressive Step-Down Example (1% profit target):**
```
Purchase 1: $50,000 (no requirement)
Purchase 2: $49,500 or lower (1.0% drop required)
Purchase 3: $48,758 or lower (1.5% drop from #2)
Purchase 4: $47,657 or lower (2.25% drop from #3)
Purchase 5: $46,270 or lower (3.375% drop from #4, capped at 5% max)
...
Purchase 10: Covers ~15-20% price range
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

**Current Version:** 0.4.1 (Beta)
**Last Updated:** 2025-11-17

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
- 📋 Cooldown period after price drop (prevent buying immediately after sharp drops)
- 📋 WebSocket support for real-time data (waiting for multibot plugin)
- 📋 Advanced order types (OCO, trailing stop-limit)
- 📋 Portfolio rebalancing strategies
- 📋 Machine learning signal integration

## ⚠️ Disclaimer

This software is for educational purposes. Cryptocurrency trading carries significant risk. Only trade with money you can afford to lose. This is not financial advice.

---

**Made with ❤️ by the KryptoMF_Ai Team**
