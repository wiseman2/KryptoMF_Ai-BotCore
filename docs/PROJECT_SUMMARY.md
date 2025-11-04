# KryptoMF_Ai Bot Core - Project Summary

## 📋 Overview

**KryptoMF_Ai Bot Core** is a fully functional, open-source cryptocurrency trading bot engine that runs from the command line. It's the core component of the KryptoMF_Ai ecosystem, providing all the essential trading functionality.

## 🎯 Project Goals

### Primary Objectives
1. **Fully Functional Free Version** - Complete trading bot that works without any paid components
2. **Open Source & Auditable** - All security-critical code is open for community review
3. **Advanced Trading Strategies** - Indicator-based strategies, not just time-based automation
4. **Exchange-Native Features** - Leverage exchange capabilities (trailing orders, etc.) when available
5. **Plugin Architecture** - Easy to extend with custom strategies, exchanges, and indicators
6. **Community-Driven** - Enable community contributions for exchanges, strategies, and indicators

### Business Model Context

This is the **open-source core** of a dual-licensing model:

- **Open Source Core (Free)** - This repository - Fully functional CLI bot
- **Premium Trading Bot Application (Paid)** - Separate repository - Multi-bot management with visual interface

The open-source core is intentionally feature-complete to provide real value to the community while the premium Trading Bot Application adds convenience features for non-technical users.

## ✨ Key Features

### Advanced Trading Strategies

#### 1. Advanced DCA (Dollar Cost Averaging)
Based on the original KryptoMFG multibot implementation, this strategy applies profit from subsequent sales to reduce the cost basis of previous purchases.

**How it works:**
- Buy #1: 1 BTC @ $50,000 (cost: $50,000)
- Buy #2: 1 BTC @ $48,000 (cost: $48,000)
- Sell #2: 1 BTC @ $49,000 (profit: $1,000)
- After min profit threshold (0.5% = $240), remaining profit ($760) is applied to Buy #1
- Buy #1 new cost: $49,240 (instead of $50,000)
- Buy #1 new sell price: $49,732 (instead of $50,500)

This makes earlier purchases easier to sell at profit and allows for continuous accumulation.

**Configuration:**
- `min_profit_percent`: Minimum profit before applying DCA (default: 0.5%)
- `dca_pool_percent`: Percentage of excess profit to apply (default: 100%)
- `max_purchases`: Maximum number of active purchases (default: -1 for unlimited)

#### 2. Enhanced DCA with Indicators
Instead of time-based buying, this strategy uses technical indicators to identify optimal entry points.

**Features:**
- **Price Drop Requirement**: Must see a price drop before considering a buy
- **Indicator Validation**: Uses RSI, Stochastic RSI, EMA, MACD, MFI
- **Majority Voting**: Requires at least 50% of enabled indicators to agree
- **Configurable**: Select which indicators to use and adjust thresholds

**No more blind buying** - The bot waits for favorable market conditions based on your selected indicators.

#### 3. Grid Trading with Indicator Validation
Traditional grid trading places buy/sell orders at fixed intervals. This enhanced version validates orders with technical indicators before placement.

**Features:**
- **Smart Grid Placement**: Grid orders validated with indicators
- **Prevents Blind Buying**: Won't place buy orders in unfavorable conditions
- **Configurable Validation**: Enable/disable indicator checks for buys and sells separately
- **Indicator Support**: RSI, MACD, EMA validation

#### 4. Exchange-Native Trailing Orders
For exchanges that support it (Binance/Binance.US), trailing orders are placed directly on the exchange.

**Why this matters:**
- ✅ Orders persist through power outages
- ✅ Orders persist through internet issues
- ✅ Orders persist through computer crashes
- ✅ More reliable than bot-managed trailing

**Supported Exchanges:**
- Binance
- Binance.US
- Binance USD-M Futures
- Binance COIN-M Futures

**Best Practice:** Always place trailing sell orders immediately after buy orders complete to protect your position.

### Technical Indicators Module

Reusable technical analysis indicators for all strategies:

- **RSI** (Relative Strength Index) - Oversold/overbought detection
- **Stochastic RSI** - More sensitive momentum indicator
- **EMA** (Exponential Moving Average) - Trend detection
- **MACD** (Moving Average Convergence Divergence) - Trend and momentum
- **MFI** (Money Flow Index) - Volume-weighted momentum
- **Price Drop Detection** - Percentage drop over lookback period
- **Price Rising Detection** - Recent price momentum

**Library:** Uses `ta` (Technical Analysis library) for reliable, well-tested implementations.

### Security Features

All security-critical code is open source for community audit:

1. **API Key Storage**
   - OS-native keychain integration (macOS Keychain, Windows DPAPI, Linux Secret Service)
   - Encrypted fallback storage
   - Keys NEVER transmitted to any server
   - Local-only access

2. **Order Signing**
   - HMAC/EdDSA/ECDSA signing
   - Timestamp/nonce for replay protection
   - Signature validation
   - No secrets logged

3. **Secrets Handling**
   - Automatic redaction in logs
   - Secure I/O boundaries
   - Memory clearing after use

### Plugin System

Easy to extend with custom functionality:

- **Exchange Plugins** - Add support for new exchanges
- **Strategy Plugins** - Create custom trading strategies
- **Indicator Plugins** - Add new technical indicators
- **Signal Plugins** - Integrate external signals (webhooks, TradingView, etc.)

## 🏗️ Architecture

### Repository Structure

```
KryptoMF_Ai-BotCore/
├── src/
│   ├── core/                    # Core bot engine
│   ├── security/                # Key storage, signing (auditable)
│   ├── plugins/                 # Plugin system
│   │   ├── base/                # Base plugin classes
│   │   ├── exchanges/           # Exchange connectors
│   │   ├── strategies/          # Trading strategies
│   │   │   ├── dca.py           # Enhanced DCA
│   │   │   ├── advanced_dca.py  # Advanced DCA with profit application
│   │   │   └── grid_trading.py  # Grid trading with indicators
│   │   └── indicators.py        # Technical indicators module
│   ├── trading/                 # Order execution
│   ├── data/                    # Market data
│   └── utils/                   # Utilities
├── config/                      # Configuration files
│   ├── example_config.yaml      # Basic configuration example
│   └── strategy_config_example.yaml  # Comprehensive strategy configuration
├── tests/                       # Unit tests
├── docs/                        # Documentation
├── cli.py                       # CLI entry point
├── main.py                      # Main entry point
├── README.md                    # Main documentation
├── QUICKSTART.md                # Quick start guide
├── STRATEGY_ENHANCEMENTS.md     # Strategy documentation
├── BUILD.md                     # Build guide
├── CONTRIBUTING.md              # Contribution guide
└── TESTING.md                   # Testing guide
```

### Design Principles

1. **Separation of Concerns**
   - Core engine handles bot logic
   - Plugins handle specific functionality
   - Clean API boundaries

2. **Event-Driven**
   - Plugins communicate via event bus
   - Loose coupling between components

3. **Configuration-Driven**
   - YAML/JSON configuration files
   - Interactive CLI prompts (if no config)
   - Sensible defaults

4. **Plugin-Based**
   - Easy to add new exchanges
   - Easy to add new strategies
   - Easy to add new indicators

## 📚 Documentation

### User Documentation
- **[README.md](../README.md)** - Main documentation and feature overview
- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[STRATEGY_ENHANCEMENTS.md](STRATEGY_ENHANCEMENTS.md)** - Detailed strategy documentation
- **[config/strategy_config_example.yaml](../config/strategy_config_example.yaml)** - Configuration template

### Developer Documentation
- **[BUILD.md](BUILD.md)** - How to build standalone executables
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute
- **[TESTING.md](TESTING.md)** - How to run and write tests

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

### Configuration

```yaml
# config/bot_config.yaml
exchange: binance_us
symbol: BTC/USD
strategy: advanced_dca
strategy_params:
  amount_usd: 100
  min_profit_percent: 0.5
  dca_pool_percent: 100
  max_purchases: -1  # -1 = unlimited (default), or set a specific limit
  indicators:
    rsi:
      enabled: true
      oversold: 35
    ema:
      enabled: true
      length: 25
```

See [STRATEGY_ENHANCEMENTS.md](STRATEGY_ENHANCEMENTS.md) for comprehensive configuration options.

## 🔑 Key Improvements Over Original Bots

### From KryptoMFG
**Retained:**
- ✅ Advanced DCA with profit application logic
- ✅ Technical indicator integration
- ✅ Real-time WebSocket data
- ✅ Multi-coin support

**Improved:**
- ✅ **Modular Design** - Plugin system for easy additions
- ✅ **Configurable Indicators** - Select which indicators to use
- ✅ **Exchange-Native Trailing** - Uses exchange features when available
- ✅ **Better Documentation** - Comprehensive guides and examples
- ✅ **Open Source** - Community can audit and contribute

### From FlexGrid
**Retained:**
- ✅ Basic grid trading mechanics
- ✅ Exchange API integration via ccxt

**Improved:**
- ✅ **Indicator Validation** - No more blind grid trading
- ✅ **Advanced Strategies** - DCA with profit application
- ✅ **Plugin System** - Extensible architecture
- ✅ **Better Configuration** - YAML-based with examples

## 🔗 Related Projects

This is part of the **KryptoMF_Ai Ecosystem**:

1. **KryptoMF_Ai-BotCore** (This Repository)
   - Open-source CLI trading bot engine
   - Fully functional
   - MIT License

2. **KryptoMF_Ai-BotDashboard**
   - Premium Trading Bot Application for multi-bot management
   - Visual configuration wizards
   - Real-time charts and dashboards
   - Proprietary License

3. **KryptoMF_Ai Web Platform**
   - AI signal subscription service
   - LSTM-based price prediction
   - Community forum
   - Signal distribution

## 📝 License

MIT License - Free to use, modify, and distribute.

## ⚠️ Disclaimer

This software is for educational purposes. Cryptocurrency trading carries significant risk. Only trade with money you can afford to lose. This is not financial advice.

---

**Status**: 🚀 Active Development
**Version**: 0.2.0-alpha
**License**: MIT (Open Source)
**Last Updated**: 2025-11-01

