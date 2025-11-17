# Changelog

All notable changes to KryptoMF Bot Core will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.1] - 2025-11-17

### Fixed - Fee Calculation & DCA Logic

#### Critical Fee Calculation Fixes
- **Fee configuration reading** - Advanced DCA now reads `fees.maker` and `fees.taker` from config
- **Percentage-based fee calculation** - Uses configured fee percentages instead of order response fees
- **Accurate sell price calculation** - Calculates fees as `cost × fee_percentage` for both buy and sell
- **Fee recalculation on DCA** - When DCA is applied, fees are recalculated based on new reduced cost
- **Profit target priority** - Advanced DCA checks `strategy_params.min_profit_percent` first, then `profit_target` from root config
- **Safety buffer** - Adds 0.2% buffer to ensure profit target is met even with price fluctuations

**Before Fix:**
```
Buy at $690.98, sell at $692.84 = 0.27% increase (NOT ENOUGH to cover fees + profit!)
```

**After Fix:**
```
Buy at $690.98, sell at $705.16 = 2.05% increase (covers 0.8% fees + 1% profit + 0.2% buffer)
```

#### DCA Logic Fixes
- **First purchase exception** - Purchase #1 never applies DCA (no previous purchase to apply to)
- **Double-counting prevention** - Subtracts previously applied DCA from profit stats to avoid counting same profit twice
- **Trailing order management** - Automatically cancels and replaces trailing sell orders when DCA is applied
- **Accurate profit tracking** - Only counts net new profit in total_profit (excludes DCA already counted)

**DCA Profit Tracking Example:**
```
Purchase #1 sells: Profit = $1,000, DCA applied = $0 (first purchase)
  → Add $1,000 to total_profit

Purchase #2 sells: Profit = $1,200, DCA previously applied to it = $520
  → Add $1,200 - $520 = $680 to total_profit (avoid double-counting)
  → Apply $680 × pool% to Purchase #3

Total profit = $1,000 + $680 = $1,680 ✓ (correct)
Without fix = $1,000 + $1,200 = $2,200 ✗ (double-counted $520)
```

#### Win Rate Calculation Fix
- **Only completed trades** - Win rate now only counts trades where both buy AND sell orders are filled
- **Excludes open positions** - Open positions are not counted as wins or losses
- **Accurate statistics** - `total_trades = winning_trades + losing_trades` (calculated dynamically)

### Changed
- **Fee calculation method** - Now uses configured percentages instead of order response fees
- **DCA application logic** - Only applies starting from purchase #2
- **Profit statistics** - Accounts for previously applied DCA to avoid double-counting

## [0.4.0] - 2025-11-16

### Added - Trailing Orders & Pending Order Tracking

#### Binance/Binance.US Trailing Order Support
- **Exchange-native trailing orders** - Implemented correct Binance US API format for trailing orders
- **STOP_LOSS_LIMIT for buys** - Buy orders use `STOP_LOSS_LIMIT` type to trail price down
- **TAKE_PROFIT_LIMIT for sells** - Sell orders use `TAKE_PROFIT_LIMIT` type to trail price up
- **Trailing delta in BIPS** - Trailing distance specified in basis points (100 BIPS = 1%)
- **Automatic conversion** - Bot converts percentage (e.g., 0.3%) to BIPS (30) automatically
- **Activation price support** - Optional activation price for trailing orders
- **GTC time in force** - Orders use Good Till Cancel time in force

#### Pending Buy Order Tracking
- **Prevents multiple orders** - Tracks pending buy orders to prevent placing multiple simultaneous orders
- **on_buy_order_placed() method** - New strategy method called when order is placed but not filled
- **pending_buy_orders list** - Maintains list of pending buy order IDs
- **Hold signal while pending** - Strategy returns 'hold' signal while pending buy orders exist
- **Automatic removal on fill** - Order removed from pending list when it fills
- **State persistence** - Pending buy orders saved to state file and restored on restart
- **Crash protection** - Prevents duplicate orders after bot restarts

#### Comprehensive Purchase Records
- **Complete buy order info** - Stores order ID, price, amount, cost, fee, timestamp, complete order details
- **Complete sell order info** - Stores order ID, price, amount, fee, timestamp, complete order details
- **Purchase metadata** - Tracks cost basis, DCA applied, profit/loss for each purchase
- **Sell order status tracking** - Tracks sell order status within each purchase object
- **Historical trade logging** - Completed trades saved to JSONL files for review and analysis

#### Fully Configurable Indicators
- **All parameters configurable** - Every indicator parameter can be set in YAML config
- **RSI configuration** - Period, oversold/overbought levels, check_rising option
- **MACD configuration** - Fast, slow, signal periods, check_rising option
- **Stochastic RSI configuration** - Period, smoothing, oversold/overbought levels
- **MFI configuration** - Period, oversold level
- **EMA configuration** - Length/period
- **Price drop configuration** - Drop percentage, lookback candles
- **Price rising detection** - Checks if price is rising in last 3 candles
- **Indicator agreement threshold** - Configurable percentage of indicators that must agree (e.g., 0.6 = 60%)

#### 1-Minute Candles
- **Changed default timeframe** - Changed from 5-minute to 1-minute candles for more responsive indicators
- **Faster signal detection** - Indicators update every minute instead of every 5 minutes
- **More accurate trailing** - Better price tracking for trailing orders

### Changed - 2025-11-16

#### Advanced DCA Strategy
- **Pending buy order tracking** - Added `pending_buy_orders` list to track pending orders
- **Priority reordering** - Check for pending orders before checking max purchases
- **Indicator parameter reading** - Reads all indicator parameters from nested config structure
- **State persistence** - Saves and restores pending buy orders
- **Logging improvements** - Shows pending order count in status messages

#### Bot Instance
- **Order status handling** - Differentiates between filled orders (status='closed') and pending orders (status='open')
- **on_buy_order_placed() call** - Calls strategy method when order is placed but not filled
- **State save on pending** - Saves state immediately after placing pending order

#### CCXT Exchange
- **Trailing order implementation** - Complete rewrite to use correct Binance US API format
- **Parameter conversion** - Converts trailing percentage to BIPS automatically
- **Order type selection** - Uses correct order type based on side (buy vs sell)
- **Default timeframe** - Changed from '5m' to '1m' for market data fetching

### Fixed - 2025-11-16

#### Multiple Trailing Buy Orders
- **Root cause** - Bot was placing multiple trailing buy orders without waiting for previous orders to fill
- **Solution** - Implemented pending buy order tracking to prevent multiple simultaneous orders
- **State persistence** - Pending orders survive bot restarts

#### Binance US API Errors
- **Too many parameters** - Fixed by using correct Binance US API format
- **Missing stopLossOrTakeProfit** - Fixed by using correct order types (STOP_LOSS_LIMIT/TAKE_PROFIT_LIMIT)
- **Wrong parameter names** - Changed from callbackRate to trailingDelta
- **Wrong units** - Changed from percentage to basis points (BIPS)

### Documentation - 2025-11-16

#### Updated Documentation
- **README.md** - Updated with trailing order details, indicator configuration, pending order tracking
- **STRATEGY_ENHANCEMENTS.md** - Added detailed trailing order implementation, pending order tracking, indicator configuration
- **STATE_PERSISTENCE_AND_RELIABILITY.md** - Added pending order tracking section, updated state persistence details
- **CHANGELOG.md** - This comprehensive update

## [0.3.1] - 2025-11-03

### Fixed
- **Connectivity check for paper trading** - Changed connectivity check from exchange API calls to simple socket ping to Google DNS (8.8.8.8:53)
  - Fixes "API-key format invalid" error in paper trading mode
  - No API keys required for connectivity check
  - Works for both live and paper trading modes
  - Both modes need internet to fetch market data (current or historical)

## [0.3.0] - 2025-11-03

### Added - State Persistence & Reliability

#### State Persistence System
- **JSON-based state persistence** - Bot state saved to `data/bot_state_{bot_id}.json` after every trade
- **Atomic writes** - State files written atomically (temp file + rename) to prevent corruption
- **Auto-save** - Periodic state saves every 60 seconds (configurable)
- **Immediate save** - State saved immediately after each buy/sell order fills
- **State restoration** - Automatic state recovery on bot initialization
- **Pending sell order tracking** - Full tracking of pending sell orders with purchase info
- **Trailing state persistence** - Bot-managed trailing state saved and restored
- **Connectivity status tracking** - Tracks connectivity failures and last successful connection

#### Connectivity Monitoring
- **Periodic connectivity checks** - Checks internet connectivity every 2 minutes (configurable)
- **Simple socket ping** - Uses socket connection to Google DNS (8.8.8.8:53) - no API keys required
- **Works for all modes** - Paper trading and live trading both need internet for market data
- **Failure tracking** - Counts consecutive connectivity failures
- **Exponential backoff** - Waits longer between retries after failures (30s, 60s, 120s, 240s, max 300s)
- **Trailing state reset** - Automatically resets trailing state after 2+ connectivity failures
- **Graceful degradation** - Bot continues running with backoff instead of crashing

#### Trailing State Management
- **Full trailing state tracking** - Tracks status (inactive, waiting, active, triggered)
- **Direction tracking** - Separate logic for trailing up (sells) and trailing down (buys)
- **Activation price** - Waits for price to reach activation level before starting to trail
- **Watermark management** - Tracks highest price (sell) or lowest price (buy) while trailing
- **Trigger detection** - Automatically detects when trailing percentage threshold is met
- **State persistence** - Trailing state saved and restored across bot restarts
- **Automatic reset** - Resets trailing after connectivity loss or order fill
- **Implemented for all strategies** - DCA and Advanced DCA both support trailing state

#### Smart Indicator Checks
- **Price movement threshold** - Only checks indicators if price moved ≥0.5% from last purchase
- **OHLCV data caching** - Caches OHLCV data for 5 minutes to reduce API calls
- **Cache TTL** - Configurable cache time-to-live (default 300 seconds)
- **Smart skip logic** - Skips indicator calculations when price hasn't moved enough
- **80% API reduction** - Reduces API calls from 1,440/day to 288/day
- **Configurable optimization** - Can enable/disable smart checks and adjust thresholds

### Added - 2025-11-03

#### Trading Fees & Profit Management
- **Fee-aware profit calculations** - All profit calculations now account for both maker and taker fees
- **Configurable trading fees** - Set maker and taker fee percentages in configuration
- **Accurate sell price calculation** - Bot calculates exact sell price needed to achieve target profit after all fees
- **Fee transparency** - Purchase logs now show buy fee, sell fee, target sell price, and expected profit
- **Helper methods** - Added `calculate_sell_price_with_fees()` and `calculate_actual_profit_percent()` to TechnicalIndicators class

#### Order Types & Trailing
- **Multiple order types** - Support for market, limit, stop, trailing market, trailing limit, and trailing stop orders
- **Configurable buy order type** - Choose order type for buy orders (market, limit, trailing market, trailing limit)
- **Configurable sell order type** - Choose order type for sell orders (market, limit, trailing market, trailing limit, trailing stop)
- **Trailing buy percentage** - Set trailing percentage for buy orders (e.g., 0.25%)
- **Trailing sell percentage** - Set trailing percentage for sell orders (e.g., 0.25% for 0.5-1% profit targets)
- **Interactive configuration** - Setup wizard asks for order types and trailing percentages

#### Technical Indicators
- **RSI rising check** - Optional check to wait for RSI momentum reversal before buying
- **Configurable RSI rising** - User can enable/disable RSI rising check per their preference
- **Enhanced RSI method** - Added `is_rsi_rising()` method to check RSI trend over multiple periods
- **Indicator-based configuration** - All indicators now use configured values instead of hardcoded settings
- **Flexible indicator setup** - Each indicator can be individually configured with custom periods and thresholds

#### Documentation
- **Documentation index** - Created `docs/README.md` linking all documentation together
- **Fees and profit guide** - Comprehensive guide explaining fee calculations, order types, and RSI rising check
- **Updated main README** - Added sections on trading fees, profit calculation, and new features
- **Example configuration** - Updated test config with all new features
- **Changelog** - This file to track all changes

### Changed - 2025-11-03

#### Bot Instance
- **State persistence integration** - Bot instance now saves/loads state automatically
- **Connectivity monitoring** - Main loop now includes periodic connectivity checks
- **Exponential backoff** - Exception handler uses exponential backoff on failures
- **Trailing state reset** - Calls strategy's `reset_trailing()` method after connectivity failures

#### DCA Strategy
- **Fee integration** - DCA strategy now reads fees from config and uses them in calculations
- **Profit target integration** - DCA strategy uses configured profit target instead of hardcoded values
- **Indicator configuration** - DCA strategy reads indicator settings from config instead of using hardcoded values
- **Enhanced logging** - Purchase logs now show comprehensive fee and profit information
- **State tracking** - Added `last_purchase_price` to strategy state for accurate sell price calculation
- **Pending sell orders** - Tracks pending sell order details in strategy state
- **Trailing state** - Added trailing state management with watermark tracking
- **Smart checks** - Added OHLCV caching and price movement threshold checking

#### Advanced DCA Strategy
- **Sell order tracking** - Purchase records now include sell order status
- **Trailing state** - Added same trailing state management as DCA strategy
- **State persistence** - Trailing state saved and restored with strategy state

#### CCXT Exchange Plugin
- **Connectivity check** - Added `check_connectivity()` method for internet verification

#### Configuration Manager
- **Step 6: Trading Fees** - Interactive setup now asks for maker and taker fees
- **Step 7: Profit Target** - Interactive setup now asks for minimum profit percentage
- **Step 8: Order Types** - Interactive setup now asks for buy/sell order types and trailing percentages
- **Step 9: Risk Management** - Renumbered from Step 8
- **Step 10: Trading Mode** - Renumbered from Step 9
- **RSI configuration** - Added "check_rising" option to RSI indicator configuration

#### Documentation
- **Related Projects** - Updated description of KryptoMF_Ai-BotDashboard to reflect it as complete trading bot system
- **Removed GUI references** - Changed from "Premium GUI" to "Complete KryptoMF_AI Trading Bot"
- **Added clarification** - Noted that BotCore is fully functional standalone, BotDashboard adds web interface
- **New documentation** - Added STATE_PERSISTENCE_AND_RELIABILITY.md with comprehensive guide
- **Updated README** - Added reliability features section and documentation links
- **Updated IMPLEMENTATION_GAPS** - Marked all critical gaps as resolved

### Fixed - 2025-11-03

#### Import Errors
- **Module import error** - Fixed `ModuleNotFoundError: No module named 'cli.status_display'`
- **Created __init__.py files** - Added `src/cli/__init__.py` and `src/backtesting/__init__.py`
- **Fixed import paths** - Changed imports from `cli.` to `src.cli.` in `cli.py`

#### Exchange Integration
- **Exchange ID mapping** - Fixed `Exchange binance_us not supported by ccxt` error
- **Added EXCHANGE_ID_MAP** - Maps user-friendly names to ccxt exchange IDs
- **Binance.US support** - Maps `binance_us` to `binanceus` for ccxt compatibility

### Technical Details

#### New Configuration Fields (v0.3.0)

```yaml
# State persistence
state_dir: data              # Directory to save bot state files
auto_save: true              # Enable auto-save
save_interval: 60            # Auto-save every 60 seconds

# Connectivity monitoring
connectivity_check_interval: 120  # Check connectivity every 2 minutes
max_connectivity_failures: 2      # Reset trailing state after this many failures

# Smart indicator checks (optimization)
smart_indicator_checks: true      # Skip indicator checks when not needed
min_price_change_percent: 0.5     # Only check indicators if price moved this much
indicator_cache_ttl: 300          # Cache OHLCV data for 5 minutes
```

#### Configuration Fields (v0.2.0)

```yaml
# Trading fees
fees:
  maker: 0.1  # Maker fee percentage
  taker: 0.1  # Taker fee percentage

# Profit target
profit_target: 1.0  # Minimum profit percentage after fees

# Order types
buy_order_type: limit  # market, limit, trailing_market, trailing_limit
sell_order_type: trailing_market  # market, limit, trailing_market, trailing_limit, trailing_stop

# Trailing percentages
trailing_buy_percent: 0.25  # Only if buy order type is trailing
trailing_sell_percent: 0.25  # Only if sell order type is trailing

# Indicator configuration
strategy_params:
  indicators:
    rsi:
      enabled: true
      period: 14
      oversold: 30
      overbought: 70
      check_rising: true  # NEW: Optional RSI rising check
```

#### New Methods (v0.3.0)

**BotInstance class:**
- `_save_state()` - Save bot state to disk with atomic writes
- `_load_state()` - Load bot state from disk on initialization
- `_auto_save_if_needed()` - Auto-save state if interval has passed
- `_check_connectivity()` - Check internet connectivity to exchange
- `_reset_trailing_state()` - Reset trailing state after connectivity loss

**CCXTExchange class:**
- `check_connectivity()` - Verify exchange is reachable

**DCAStrategy class:**
- `_get_ohlcv_data(market_data)` - Get OHLCV data with caching
- `start_trailing(direction, activation_price, trailing_percent)` - Start trailing for buy or sell
- `update_trailing(current_price)` - Update trailing state with current price
- `reset_trailing()` - Reset trailing state

**AdvancedDCAStrategy class:**
- `start_trailing(direction, activation_price, trailing_percent)` - Start trailing for buy or sell
- `update_trailing(current_price)` - Update trailing state with current price
- `reset_trailing()` - Reset trailing state

#### New Methods (v0.2.0)

**TechnicalIndicators class:**
- `is_rsi_rising(df, period=14, lookback=3)` - Check if RSI is rising over multiple periods
- `calculate_sell_price_with_fees(buy_price, buy_fee_percent, sell_fee_percent, profit_target_percent)` - Calculate sell price for target profit
- `calculate_actual_profit_percent(buy_price, sell_price, buy_fee_percent, sell_fee_percent)` - Verify actual profit after fees

**DCAStrategy class:**
- `get_sell_price()` - Get target sell price for current position accounting for fees

#### Modified Methods (v0.3.0)

**BotInstance.__init__:**
- Added state persistence variables
- Added connectivity tracking variables

**BotInstance.initialize:**
- Calls `_load_state()` to restore previous state

**BotInstance.stop:**
- Calls `_save_state()` to save final state

**BotInstance._execute_buy:**
- Saves state immediately after order fills

**BotInstance._execute_sell:**
- Saves state immediately after order fills

**BotInstance main loop:**
- Added periodic connectivity checks
- Added auto-save calls
- Added exponential backoff on failures

**DCAStrategy.__init__:**
- Added smart indicator check variables
- Added OHLCV cache variables
- Added trailing state dictionary

**DCAStrategy.analyze:**
- Added price movement threshold check
- Uses `_get_ohlcv_data()` for cached data

**DCAStrategy.get_state:**
- Now includes `pending_sell_order` and `trailing_state`

**DCAStrategy.restore_state:**
- Restores `pending_sell_order` and `trailing_state`

**DCAStrategy.on_order_filled:**
- Tracks pending sell order details
- Updates sell order status when filled

**AdvancedDCAStrategy.__init__:**
- Added trailing state dictionary

**AdvancedDCAStrategy.get_state:**
- Now includes `trailing_state`

**AdvancedDCAStrategy.restore_state:**
- Restores `trailing_state`

**AdvancedDCAStrategy._handle_buy_filled:**
- Tracks sell order status in purchase record

**AdvancedDCAStrategy._handle_sell_filled:**
- Updates sell order status when filled

#### Modified Methods (v0.2.0)

**DCAStrategy.__init__:**
- Now reads `fees` from config
- Now reads `profit_target` from config
- Now reads indicator configuration from `strategy_params.indicators`
- Supports configurable periods and thresholds for all indicators

**DCAStrategy.analyze:**
- Uses configured indicator periods and thresholds
- Implements RSI rising check when enabled
- Provides detailed buy signal reasons including RSI trend

**DCAStrategy.on_order_filled:**
- Calculates target sell price with fees
- Logs comprehensive fee and profit information
- Tracks last purchase price for sell calculations

#### Files Modified (v0.3.0)

- `tempBotCore/src/core/bot_instance.py` - Added state persistence, connectivity monitoring, trailing reset
- `tempBotCore/src/plugins/strategies/dca.py` - Added trailing state, smart checks, OHLCV caching, pending sell tracking
- `tempBotCore/src/plugins/strategies/advanced_dca.py` - Added trailing state, sell order tracking
- `tempBotCore/src/plugins/exchanges/ccxt_exchange.py` - Added connectivity check method
- `tempBotCore/config/test_dca_config.yaml` - Added state persistence, connectivity, and smart check options
- `tempBotCore/README.md` - Added reliability features section and documentation links
- `tempBotCore/docs/IMPLEMENTATION_GAPS.md` - Updated status to show all gaps resolved

#### Files Created (v0.3.0)

- `tempBotCore/docs/STATE_PERSISTENCE_AND_RELIABILITY.md` - Comprehensive guide to new reliability features

#### Files Modified (v0.2.0)

- `tempBotCore/src/core/config_manager.py` - Added fee, profit, order type, and trailing configuration
- `tempBotCore/src/plugins/strategies/dca.py` - Integrated fees, profit target, and indicator configuration
- `tempBotCore/src/plugins/indicators.py` - Added RSI rising check and fee calculation methods
- `tempBotCore/src/plugins/exchanges/ccxt_exchange.py` - Added exchange ID mapping
- `tempBotCore/cli.py` - Fixed import paths
- `tempBotCore/README.md` - Added new features documentation and updated related projects
- `tempBotCore/config/test_dca_config.yaml` - Updated with all new configuration options

#### Files Created (v0.2.0)

- `tempBotCore/src/cli/__init__.py` - Makes cli a proper Python package
- `tempBotCore/src/backtesting/__init__.py` - Makes backtesting a proper Python package
- `tempBotCore/docs/README.md` - Documentation index linking all guides
- `tempBotCore/docs/FEES_AND_PROFIT_CALCULATION.md` - Comprehensive fee and profit guide
- `tempBotCore/CHANGELOG.md` - This changelog file

### Migration Guide (v0.3.0)

If you have existing configuration files, add these new fields for reliability features:

```yaml
# State persistence (optional, has defaults)
state_dir: data              # Default: data
auto_save: true              # Default: true
save_interval: 60            # Default: 60

# Connectivity monitoring (optional, has defaults)
connectivity_check_interval: 120  # Default: 120
max_connectivity_failures: 2      # Default: 2

# Smart indicator checks (optional, has defaults)
smart_indicator_checks: true      # Default: true
min_price_change_percent: 0.5     # Default: 0.5
indicator_cache_ttl: 300          # Default: 300
```

**Note:** All new fields are optional and have sensible defaults. Existing configs will work without changes.

### Migration Guide (v0.2.0)

If you have existing configuration files, add these new fields:

```yaml
# Add trading fees
fees:
  maker: 0.1  # Check your exchange's fee schedule
  taker: 0.1

# Add profit target
profit_target: 1.0  # Your desired profit percentage

# Add order types (optional, defaults to limit/trailing_market)
buy_order_type: limit
sell_order_type: trailing_market
trailing_sell_percent: 0.25

# Update indicator configuration to include check_rising
strategy_params:
  indicators:
    rsi:
      enabled: true
      period: 14
      oversold: 30
      overbought: 70
      check_rising: true  # Add this line
```

### Breaking Changes

None. All new features are backward compatible with default values.

### Deprecations

None.

---

## [0.1.0] - 2025-11-02

### Initial Features

- Interactive CLI bot with real-time status display
- Keyboard controls (pause, resume, status, quit)
- Multiple exchange support via ccxt
- OS keychain integration for secure credential storage
- DCA and Grid trading strategies
- Technical indicators (RSI, MACD, EMA, Stochastic RSI, MFI)
- Backtesting framework with historical data
- Paper trading mode
- Configuration validation
- Plugin system

---

**Legend:**
- `Added` - New features
- `Changed` - Changes to existing functionality
- `Deprecated` - Soon-to-be removed features
- `Removed` - Removed features
- `Fixed` - Bug fixes
- `Security` - Security improvements

