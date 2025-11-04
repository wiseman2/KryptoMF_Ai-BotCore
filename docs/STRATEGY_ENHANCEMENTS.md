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
- **Profit Application Logic**: When a purchase is sold at a profit, the excess profit (after minimum profit threshold) is applied to the previous purchase
- **Cost Basis Reduction**: Lowers the average cost of earlier purchases, making them easier to sell at profit
- **Indicator-Based Buying**: Uses configurable technical indicators instead of time-based intervals
- **Configurable Parameters**:
  - `min_profit_percent`: Minimum profit before applying DCA (default: 0.5%)
  - `dca_pool_percent`: Percentage of excess profit to apply (default: 100%)
  - `max_purchases`: Maximum number of active purchases (default: -1 for unlimited)

### Example
```
Buy #1: 1 BTC @ $50,000 (cost: $50,000)
Buy #2: 1 BTC @ $48,000 (cost: $48,000)
Sell #2: 1 BTC @ $49,000 (profit: $1,000)

After min profit (0.5% = $240), remaining profit ($760) applied to Buy #1:
Buy #1 new cost: $50,000 - $760 = $49,240
Buy #1 new sell price: $49,732 (instead of $50,500)
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
- **CCXT Exchange** (`ccxt_exchange.py`): Implemented Binance/Binance.US trailing order support

### Supported Exchanges
- Binance
- Binance.US
- Binance USD-M Futures
- Binance COIN-M Futures

### Key Features
- **Exchange-Native Orders**: Places trailing orders directly on the exchange
- **Protection Against Failures**: Orders persist through power outages, internet issues, computer crashes
- **Configurable Trailing Percent**: Adjustable trailing percentage per order
- **Fallback Support**: Raises clear error if exchange doesn't support trailing orders

### Usage Example
```python
# Check if exchange supports trailing orders
if exchange.supports_trailing_orders():
    # Place trailing sell order
    order = exchange.place_trailing_order(
        symbol='BTC/USD',
        side='sell',
        amount=0.1,
        trailing_percent=1.0  # 1% trailing
    )
```

### Based On
- `reference/oldCryptoProject/KryptoMFG/BuyAndSell.py` lines 484-516 (trailing order implementation)

### Important Notes
⚠️ **ALWAYS place trailing sell orders immediately after buy orders complete**
- This protects your position even if the bot crashes
- Exchange-placed orders are more reliable than bot-managed orders
- User's original practice: "as soon as I made a buy, I would immediately place the trailing sell on binance_us"

---

## 5. Technical Indicators Module (`indicators.py`)

### Purpose
Provides reusable technical analysis indicators for all strategies.

### Indicators Implemented
- **RSI** (Relative Strength Index): Oversold/overbought detection
- **Stochastic RSI**: More sensitive momentum indicator
- **EMA** (Exponential Moving Average): Trend detection
- **MACD** (Moving Average Convergence Divergence): Trend and momentum
- **MFI** (Money Flow Index): Volume-weighted momentum
- **Price Drop Detection**: Percentage drop over lookback period
- **Price Rising Detection**: Recent price momentum

### Library Used
- `ta` (Technical Analysis library) - NOT pandas_ta

### Usage Example
```python
from plugins.indicators import TechnicalIndicators

# Check if RSI is oversold
if TechnicalIndicators.is_rsi_oversold(df, period=14, oversold_level=30):
    print("RSI is oversold - potential buy signal")

# Get MACD values
macd, signal, histogram = TechnicalIndicators.get_macd(df)

# Check if price has dropped
if TechnicalIndicators.has_price_dropped(df, lookback=24, drop_percent=1.0):
    print("Price has dropped 1% in last 24 candles")
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

