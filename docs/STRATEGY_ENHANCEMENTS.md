# Strategy Enhancements - Implementation Summary

This document summarizes the enhancements made to the KryptoMF Bot Core trading strategies based on the original KryptoMFG multibot implementation.

## Overview

The following enhancements have been implemented:

1. **Advanced DCA Strategy with Profit Application** ✅
2. **Enhanced Main DCA Strategy with Indicator-Based Decisions** ✅
3. **Grid Strategy with Indicator Integration** ✅
4. **Trailing Order Support** ✅
5. **Technical Indicators Module** ✅
6. **Configuration Schema** ✅

---

## 1. Advanced DCA Strategy (`advanced_dca.py`)

### Purpose
Implements the advanced DCA logic from the original multibot where profit from selling a subsequent purchase is applied to reduce the cost basis of previous purchases.

### Key Features
- **Profit Application Logic**: When purchase #2+ is sold at a profit, the excess profit (after minimum profit threshold) is applied to the previous purchase
- **First Purchase Exception**: Purchase #1 never applies DCA (no previous purchase to apply to)
- **Cost Basis Reduction**: Lowers the average cost of earlier purchases, making them easier to sell at profit
- **Fee-Aware Calculations**: Uses configured maker/taker fee percentages (not order response fees) for accurate profit calculations
- **Trailing Order Management**: Automatically cancels and replaces trailing sell orders when DCA is applied
- **Double-Counting Prevention**: Subtracts previously applied DCA from profit stats to avoid counting the same profit twice
- **Indicator-Based Buying**: Uses configurable technical indicators instead of time-based intervals
- **Progressive Step-Down**: Requires progressively lower prices for each additional purchase to prevent clustering
- **Pending Buy Order Tracking**: Prevents multiple simultaneous buy orders while waiting for trailing orders to fill
- **Comprehensive Purchase Records**: Stores complete buy/sell order info, fees, timestamps, profit, DCA applied
- **Historical Trade Logging**: Completed trades saved to JSONL files for review and analysis
- **Configurable Parameters**:
  - `min_profit_percent`: Minimum profit before applying DCA (default: 0.5%, or uses `profit_target` from root config)
  - `dca_pool_percent`: Percentage of excess profit to apply (default: 100%)
  - `max_purchases`: Maximum number of active purchases (default: -1 for unlimited)
  - `indicator_agreement`: Percentage of indicators that must agree (default: 0.6 = 60%)
  - `step_down_multiplier`: Multiplier for progressive step-down (default: 1.5)
  - `max_step_down`: Maximum step-down percentage (default: 5.0%)

### Example
```
Buy #1: 1 BEC @ $50,000 (cost: $50,000)
Buy #2: 1 BTC @ $48,000 (cost: $48,000)
Sell #2: 1 BTC @ $49,000 (profit: $1,000)

After min profit (1% = $480), remaining profit ($520) applied to Buy #1:
Buy #1 new cost: $50,000 - $520 = $49,480
Buy #1 fees recalculated: $49,480 × 0.004 × 2 = $0.396
Buy #1 new sell price: (($49,480 + $0.396) / 1) × 1.012 = $50,115

If Buy #1 had a trailing sell order:
- Old trailing order cancelled
- New trailing order placed at $50,115
```

### DCA Profit Tracking
```
Purchase #1 sells: Profit = $1,000, DCA applied = $0 (first purchase)
  → Add $1,000 to total_profit

Purchase #2 sells: Profit = $1,200, DCA applied to it = $520
  → Add $1,200 - $520 = $680 to total_profit (avoid double-counting)
  → Apply $680 × pool% to Purchase #3

Total profit = $1,000 + $680 = $1,680 ✓ (correct)
Without fix = $1,000 + $1,200 = $2,200 ✗ (double-counted $520)
```

### Based On
- `reference/oldCryptoProject/KryptoMFG/multibot.py` lines 836-876 (`sold_order` function)
- `reference/oldCryptoProject/KryptoMFG/costAveraging.py` lines 4-16 (`dca_add` function)

---

## 2. Enhanced DCA Strategy (`dca.py`)

### Changes Made
- **Removed**: Time-based interval triggers
- **Added**: Indicator-based buy decisions
- **Added**: Price drop detection (required before buying)
- **Added**: Configurable indicator selection

### Key Features
- **Price Drop Requirement**: Must see a price drop of X% before considering a buy
- **Indicator Validation**: Uses RSI, Stochastic RSI, EMA, MACD, MFI to validate entry points
- **Minimum Interval**: Prevents overtrading with configurable minimum hours between purchases
- **Majority Voting**: Requires at least 50% of enabled indicators to agree before buying

### Configuration Example
```yaml
dca:
  amount_usd: 100
  min_interval_hours: 1
  price_drop_percent: 1.0  # Required
  indicators:
    rsi:
      enabled: true
      oversold: 35
    ema:
      enabled: true
      length: 25
```

---

## 3. Grid Trading Strategy (`grid_trading.py`)

### Changes Made
- **Added**: Indicator validation for buy orders
- **Added**: Indicator validation for sell orders (optional)
- **Added**: Configurable indicator thresholds

### Key Features
- **Smart Grid Placement**: Grid orders are validated with indicators before placement
- **Prevents Blind Buying**: Won't place buy orders in unfavorable market conditions
- **Configurable Validation**: Can enable/disable indicator checks for buys and sells separately
- **Indicator Support**: RSI, MACD, EMA validation

### Configuration Example
```yaml
grid_trading:
  grid_spacing: 2.5
  grid_levels: 10
  use_indicators_for_buy: true
  use_indicators_for_sell: false
  buy_indicators:
    rsi:
      enabled: true
      oversold: 40
```

---

## 4. Trailing Order Support

### Implementation
- **Base Plugin** (`exchange_plugin.py`): Added `place_trailing_order()` and `supports_trailing_orders()` methods
- **CCXT Exchange** (`ccxt_exchange.py`): Implemented Binance/Binance.US trailing order support using correct API format

### Supported Exchanges
- Binance
- Binance.US
- Binance USD-M Futures
- Binance COIN-M Futures

### Binance/Binance.US API Format
The bot uses the correct Binance US API format for trailing orders:

**Buy Orders (Trailing Down):**
- Order Type: `STOP_LOSS_LIMIT`
- Parameter: `trailingDelta` in basis points (BIPS) where 100 BIPS = 1%
- Behavior: Trails price DOWN to buy at a lower price

**Sell Orders (Trailing Up):**
- Order Type: `TAKE_PROFIT_LIMIT`
- Parameter: `trailingDelta` in basis points (BIPS)
- Behavior: Trails price UP to sell at a higher price

**Example:**
```python
# 0.3% trailing buy order
trailing_delta_bips = int(0.3 * 100)  # = 30 BIPS

order = exchange.create_order(
    symbol='ZEC/USDT',
    type='STOP_LOSS_LIMIT',
    side='buy',
    amount=0.01,
    price=700.00,  # Limit price
    params={
        'stopPrice': 700.00,  # Activation price
        'trailingDelta': 30,  # 0.3% in BIPS
        'timeInForce': 'GTC'
    }
)
```

### Pending Order Tracking
The bot now tracks pending buy orders to prevent placing multiple simultaneous orders:

**How It Works:**
1. When a trailing buy order is placed, `on_buy_order_placed()` is called
2. Order ID is added to `pending_buy_orders` list
3. Strategy returns 'hold' signal while pending orders exist
4. When order fills, `on_order_filled()` removes it from pending list
5. Bot can then place next order if signals align

**State Persistence:**
- Pending buy orders are saved to state file
- Restored on bot restart
- Prevents duplicate orders after crashes

### Key Features
- **Exchange-Native Orders**: Places trailing orders directly on the exchange
- **Protection Against Failures**: Orders persist through power outages, internet issues, computer crashes
- **Pending Order Prevention**: Tracks pending buy orders to prevent multiple simultaneous orders
- **Configurable Trailing Percent**: Adjustable trailing percentage per order (converted to BIPS)
- **Automatic Fill Detection**: Bot monitors orders and triggers sell placement when buy fills
- **State Persistence**: Pending orders survive bot restarts

### Configuration Example
```yaml
buy_order_type: trailing_market  # or trailing_limit
trailing_buy_percent: 0.3  # 0.3% trailing distance (30 BIPS)

sell_order_type: trailing_market  # or trailing_limit
trailing_sell_percent: 0.3  # 0.3% trailing distance (30 BIPS)
```

### Based On
- `reference/oldCryptoProject/KryptoMFG/BuyAndSell.py` lines 484-516 (trailing order implementation)
- `reference/binance_us_orders.txt` - Binance US API documentation
- `reference/ccxt_trailing_orders.txt` - CCXT trailing order documentation

### Important Notes
⚠️ **ALWAYS place trailing sell orders immediately after buy orders complete**
- This protects your position even if the bot crashes
- Exchange-placed orders are more reliable than bot-managed orders
- User's original practice: "as soon as I made a buy, I would immediately place the trailing sell on binance_us"

⚠️ **Only ONE pending buy order at a time**
- Bot tracks pending buy orders to prevent placing multiple orders
- Strategy returns 'hold' signal while pending orders exist
- Prevents overtrading and duplicate positions

---

## 5. Technical Indicators Module (`indicators.py`)

### Purpose
Provides reusable technical analysis indicators for all strategies.

### Indicators Implemented
- **RSI** (Relative Strength Index): Oversold/overbought detection with optional rising check
- **Stochastic RSI**: More sensitive momentum indicator
- **EMA** (Exponential Moving Average): Trend detection (buy when price below EMA)
- **MACD** (Moving Average Convergence Divergence): Trend and momentum with optional rising check
- **MFI** (Money Flow Index): Volume-weighted momentum
- **Price Drop Detection**: Percentage drop over lookback period
- **Price Rising Detection**: Recent price momentum (checks last 3 candles)

### Fully Configurable Parameters
All indicator parameters are configurable from the YAML config file:

**RSI:**
- `period`: Calculation period (default: 14)
- `oversold`: Oversold threshold (default: 35)
- `overbought`: Overbought threshold (default: 55)
- `check_rising`: Wait for RSI to reverse upward (default: true)

**MACD:**
- `fast`: Fast EMA period (default: 12)
- `slow`: Slow EMA period (default: 26)
- `signal`: Signal line period (default: 9)
- `check_rising`: Wait for MACD to turn upward (default: true)

**Stochastic RSI:**
- `period`: RSI period (default: 14)
- `smoothing`: Smoothing period (default: 3)
- `oversold`: Oversold threshold (default: 33)
- `overbought`: Overbought threshold (default: 80)

**MFI:**
- `period`: Calculation period (default: 14)
- `oversold`: Oversold threshold (default: 25)

**EMA:**
- `length`: EMA period (default: 25)

**Price Drop:**
- `drop_percent`: Required drop percentage (default: 1.0)
- `lookback_candles`: Lookback period (default: 24)

**Price Rising:**
- No parameters - checks if last 3 candles are rising

### Indicator Agreement
The strategy uses an `indicator_agreement` threshold to determine when to buy:

```yaml
indicator_agreement: 0.6  # 60% of enabled indicators must agree
```

**Example:**
- 5 indicators enabled
- 3 give buy signals, 2 give hold signals
- Agreement: 3/5 = 60% ✅ Buy signal generated
- If only 2 gave buy signals: 2/5 = 40% ❌ Hold

### Library Used
- `ta` (Technical Analysis library) - NOT pandas_ta

### Usage Example
```python
from plugins.indicators import TechnicalIndicators

# Check if RSI is oversold
if TechnicalIndicators.is_rsi_oversold(df, period=14, oversold_level=30):
    print("RSI is oversold - potential buy signal")

# Check if RSI is rising (momentum reversal)
if TechnicalIndicators.is_rsi_rising(df, period=14):
    print("RSI is rising - downtrend may be reversing")

# Get MACD values
macd, signal, histogram = TechnicalIndicators.get_macd(df, fast=12, slow=26, signal=9)

# Check if MACD is rising
if TechnicalIndicators.is_macd_rising(df, fast=12, slow=26, signal=9):
    print("MACD is rising - bullish momentum")

# Check if price has dropped
if TechnicalIndicators.has_price_dropped(df, lookback=24, drop_percent=1.0):
    print("Price has dropped 1% in last 24 candles")

# Check if price is rising
if TechnicalIndicators.is_price_rising(df):
    print("Price is rising in last 3 candles")
```

---

## 6. Configuration Schema (`strategy_config_example.yaml`)

### Purpose
Provides a comprehensive configuration template for all strategies with detailed documentation.

### Features
- **Strategy Selection**: Enable/disable individual strategies
- **Indicator Configuration**: Select which indicators to use and set thresholds
- **Risk Management**: Position sizing, daily trade limits
- **Exchange Settings**: Paper trading, trailing order preferences
- **Detailed Comments**: Explains each parameter and provides tips

### Key Sections
1. Advanced DCA Configuration
2. Enhanced DCA Configuration
3. Grid Trading Configuration
4. Exchange Settings
5. Risk Management
6. Indicator Defaults
7. Logging Configuration

---

## Installation

### 1. Install Dependencies
```bash
cd BotCore
pip install -r requirements.txt
```

### 2. Configure Strategy
```bash
cp config/strategy_config_example.yaml config/strategy_config.yaml
# Edit strategy_config.yaml with your preferences
```

### 3. Run Bot
```bash
python main.py --config config/strategy_config.yaml
```

---

## Migration from Original Bot

### Key Differences

| Original Bot | New Bot Core |
|--------------|--------------|
| Time-based DCA | Indicator-based DCA |
| Single DCA strategy | Two DCA strategies (basic + advanced) |
| Blind grid trading | Indicator-validated grid trading |
| Manual trailing implementation | Exchange-native trailing support |
| Hardcoded indicators | Configurable indicator selection |

### Porting Your Settings

1. **DCA Settings**: 
   - Old `interval_hours` → New `price_drop_percent` + indicators
   - Old `dcaPerc` → New `dca_pool_percent`
   - Old `minProfit` → New `min_profit_percent`

2. **Indicator Settings**:
   - Old hardcoded values → New YAML configuration
   - Old `RsiOverSold` → New `indicators.rsi.oversold`
   - Old `StochOversold` → New `indicators.stoch_rsi.oversold`

3. **Trailing Orders**:
   - Old manual implementation → New `exchange.place_trailing_order()`
   - Automatically uses exchange-native orders when available

---

## Testing

### Paper Trading
Always test with paper trading first:
```yaml
exchange:
  paper_trading: true
```

### Recommended Testing Steps
1. Enable paper trading
2. Start with one strategy (Enhanced DCA recommended)
3. Use conservative indicator thresholds
4. Monitor for 24-48 hours
5. Adjust parameters based on results
6. Gradually enable additional strategies

---

## Best Practices

### Indicator Selection
- **Don't use too many indicators** - 2-3 is optimal
- **Good combinations**:
  - RSI + EMA (trend + momentum)
  - RSI + MACD (momentum + trend confirmation)
  - RSI + MFI (price momentum + volume momentum)

### Strategy Selection
- **Advanced DCA**: Best for long-term accumulation with profit optimization
- **Enhanced DCA**: Simpler, good for regular buying with better timing
- **Grid Trading**: Best for range-bound, volatile markets

### Risk Management
- Start with small position sizes ($10-$50)
- Use `max_purchases` to limit exposure (default is -1 for unlimited, set a specific number if you want to be cautious)
- Set `max_daily_trades` to prevent overtrading (default is -1 for unlimited)
- Monitor performance daily for first week

### Trailing Orders
- Always enable when exchange supports it
- Use 1-2% trailing for volatile assets
- Use 0.5-1% trailing for stable assets
- Place trailing sell immediately after buy

---

## Troubleshooting

### "Indicators not aligned" - No trades executing
- **Cause**: Too many indicators enabled or thresholds too strict
- **Solution**: Reduce number of indicators or relax thresholds (e.g., RSI oversold 35 → 40)

### "Price has not dropped X%" - Missing opportunities
- **Cause**: `price_drop_percent` too high
- **Solution**: Lower to 0.5-1.0% for more frequent entries

### "Exchange doesn't support trailing orders"
- **Cause**: Using exchange without trailing order support
- **Solution**: Switch to Binance/Binance.US or implement bot-managed trailing

### Orders not placing
- **Cause**: Paper trading enabled or insufficient balance
- **Solution**: Check `paper_trading` setting and account balance

---

## Future Enhancements

### Planned Features
- [ ] Bot-managed trailing orders (fallback for exchanges without native support)
- [ ] Automatic sell order placement after buy (with trailing)
- [ ] Bollinger Bands indicator
- [ ] ATR (Average True Range) for volatility-based position sizing
- [ ] Backtesting framework
- [ ] Performance analytics dashboard
- [ ] Multi-symbol support
- [ ] Telegram notifications

---

## Support

For questions or issues:
1. Check the configuration example (`strategy_config_example.yaml`)
2. Review this documentation
3. Check the original bot reference files in `reference/oldCryptoProject/KryptoMFG/`
4. Review conversation history in `reference/conversations/`

---

## Credits

Based on the original KryptoMFG multibot implementation with enhancements for:
- Better indicator integration
- More flexible configuration
- Exchange-native trailing order support
- Improved profit application logic

