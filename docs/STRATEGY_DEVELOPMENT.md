# Strategy Development Guide

This guide explains how to create custom trading strategies for KryptoMF_Ai-BotCore.

## Table of Contents
- [Quick Start](#quick-start)
- [Strategy Auto-Discovery](#strategy-auto-discovery)
- [Strategy Plugin Base Class](#strategy-plugin-base-class)
- [Required Methods](#required-methods)
- [Market Data Structure](#market-data-structure)
- [Using Technical Indicators](#using-technical-indicators)
- [Example Strategies](#example-strategies)
- [Testing Your Strategy](#testing-your-strategy)
- [Best Practices](#best-practices)

---

## Quick Start

Creating a new strategy is simple - just create a Python file in the `src/plugins/strategies/` directory:

### Step 1: Create Your Strategy File

```bash
# Create a new file in the strategies directory
touch src/plugins/strategies/my_strategy.py
```

### Step 2: Define Your Strategy Class

```python
# src/plugins/strategies/my_strategy.py
from plugins.base.strategy_plugin import StrategyPlugin
from utils.logger import get_logger

logger = get_logger(__name__)


class MyStrategy(StrategyPlugin):
    """
    My custom trading strategy.
    
    Parameters:
    - amount_usd: Amount to purchase each time (default: 100)
    - profit_target: Minimum profit percentage (default: 1.0)
    """
    
    def __init__(self, config):
        super().__init__(config)
        self.params = config.get('params', {})
        self.amount_usd = self.params.get('amount_usd', 100.0)
        self.profit_target = self.params.get('profit_target', 1.0)
    
    def analyze(self, market_data):
        """
        Analyze market data and return trading signal.
        
        Args:
            market_data: Dictionary containing market data
            
        Returns:
            Dictionary with 'action' ('buy', 'sell', or 'hold') and optional 'amount'
        """
        # Your strategy logic here
        current_price = market_data.get('last')
        
        # Example: Simple buy logic
        if self._should_buy(market_data):
            return {
                'action': 'buy',
                'amount': self.amount_usd / current_price,
                'reason': 'Buy signal triggered'
            }
        
        # Example: Simple sell logic
        if self._should_sell(market_data):
            return {
                'action': 'sell',
                'reason': 'Profit target reached'
            }
        
        return {'action': 'hold'}
    
    def _should_buy(self, market_data):
        """Your buy logic here."""
        # Implement your buy conditions
        return False
    
    def _should_sell(self, market_data):
        """Your sell logic here."""
        # Implement your sell conditions
        return False
```

### Step 3: Use Your Strategy

That's it! Your strategy is automatically discovered and available for use:

```yaml
# config/bot_config.yaml
strategy: my_strategy  # Use the filename (without .py)
strategy_params:
  amount_usd: 50.0
  profit_target: 1.5
```

Or select it in the interactive setup:
```bash
python cli.py
# Choose option 3: Create new configuration
# Your strategy will appear in the strategy list
```

---

## Strategy Auto-Discovery

**No manual registration required!** The bot automatically discovers all strategies in the `src/plugins/strategies/` directory.

### How It Works

1. **On startup**, the bot scans `src/plugins/strategies/` for all `.py` files
2. **Imports each file** and looks for classes that inherit from `StrategyPlugin`
3. **Registers the strategy** using the filename as the strategy name
4. **Makes it available** in configuration and interactive setup

### Naming Convention

- **Filename**: `my_strategy.py` → Strategy name: `my_strategy`
- **Class name**: Can be anything (e.g., `MyStrategy`, `MyCustomStrategy`)
- **Use in config**: `strategy: my_strategy` (uses filename, not class name)

### Example

```
src/plugins/strategies/
├── dca.py              → strategy: dca
├── advanced_dca.py     → strategy: advanced_dca
├── grid_trading.py     → strategy: grid_trading
└── my_strategy.py      → strategy: my_strategy
```

---

## Strategy Plugin Base Class

All strategies must inherit from `StrategyPlugin`:

```python
from plugins.base.strategy_plugin import StrategyPlugin

class MyStrategy(StrategyPlugin):
    pass
```

### Base Class Methods

The `StrategyPlugin` base class provides:

- `initialize(bot_instance)`: Called when strategy is loaded (optional to override)
- `analyze(market_data)`: **REQUIRED** - Your main strategy logic
- `on_order_filled(order)`: Called when an order is filled (optional)
- `on_order_cancelled(order)`: Called when an order is cancelled (optional)

---

## Required Methods

### `analyze(market_data)` - REQUIRED

This is the main method where your strategy logic lives.

**Parameters:**
- `market_data` (dict): Current market data (see structure below)

**Returns:**
- Dictionary with trading signal:
  ```python
  {
      'action': 'buy' | 'sell' | 'hold',
      'amount': float,  # Optional for buy, required for sell
      'reason': str     # Optional: explanation for logging
  }
  ```

**Example:**
```python
def analyze(self, market_data):
    current_price = market_data.get('last')
    
    if self._should_buy():
        return {
            'action': 'buy',
            'amount': 0.01,  # Amount in base currency (e.g., BTC)
            'reason': 'RSI oversold'
        }
    
    if self._should_sell():
        return {
            'action': 'sell',
            'reason': 'Profit target reached'
        }
    
    return {'action': 'hold'}
```

---

## Market Data Structure

The `market_data` dictionary passed to `analyze()` contains:

```python
{
    'symbol': 'BTC/USD',           # Trading pair
    'last': 67450.0,               # Last traded price
    'bid': 67449.5,                # Current bid price
    'ask': 67450.5,                # Current ask price
    'high': 68000.0,               # 24h high
    'low': 66500.0,                # 24h low
    'volume': 1234.56,             # 24h volume
    'timestamp': 1699123456789,    # Timestamp (milliseconds)
    'ohlcv': DataFrame             # Historical OHLCV data (pandas DataFrame)
}
```

### OHLCV DataFrame

The `ohlcv` key contains a pandas DataFrame with historical candle data:

```python
df = market_data.get('ohlcv')

# DataFrame columns:
# - timestamp: Unix timestamp (milliseconds)
# - open: Opening price
# - high: Highest price
# - low: Lowest price
# - close: Closing price
# - volume: Trading volume

# Example usage:
if df is not None and not df.empty:
    current_price = df['close'].iloc[-1]
    previous_price = df['close'].iloc[-2]
```

**Important Notes:**
- **Live/Paper Trading**: Contains ~100 candles (enough for indicator calculations)
- **Backtesting**: Contains rolling window of historical data
- **Last candle excluded**: The most recent incomplete candle is excluded
- **Can be None**: Check for None before using

---

## Using Technical Indicators

The bot includes a `TechnicalIndicators` helper class for common indicators:

```python
from plugins.indicators import TechnicalIndicators

class MyStrategy(StrategyPlugin):
    def analyze(self, market_data):
        df = market_data.get('ohlcv')
        
        if df is None or df.empty:
            return {'action': 'hold'}
        
        # Calculate RSI
        rsi = TechnicalIndicators.calculate_rsi(df, period=14)
        current_rsi = rsi.iloc[-1]
        
        # Calculate EMA
        ema = TechnicalIndicators.calculate_ema(df, period=25)
        current_ema = ema.iloc[-1]
        current_price = df['close'].iloc[-1]
        
        # Buy when RSI oversold and price below EMA
        if current_rsi < 30 and current_price < current_ema:
            return {'action': 'buy', 'amount': 0.01}
        
        return {'action': 'hold'}
```

### Available Indicators

See `src/plugins/indicators.py` for all available indicators:

- `calculate_rsi(df, period=14)` - Relative Strength Index
- `calculate_ema(df, period=25)` - Exponential Moving Average
- `calculate_macd(df, fast=12, slow=26, signal=9)` - MACD
- `calculate_stoch_rsi(df, period=14, smooth=3)` - Stochastic RSI
- `calculate_mfi(df, period=14)` - Money Flow Index
- And more...

---

## Example Strategies

### Example 1: Simple RSI Strategy

```python
from plugins.base.strategy_plugin import StrategyPlugin
from plugins.indicators import TechnicalIndicators

class SimpleRSIStrategy(StrategyPlugin):
    def __init__(self, config):
        super().__init__(config)
        self.params = config.get('params', {})
        self.rsi_oversold = self.params.get('rsi_oversold', 30)
        self.rsi_overbought = self.params.get('rsi_overbought', 70)
        self.amount_usd = self.params.get('amount_usd', 100)
    
    def analyze(self, market_data):
        df = market_data.get('ohlcv')
        if df is None or len(df) < 14:
            return {'action': 'hold'}
        
        rsi = TechnicalIndicators.calculate_rsi(df, period=14)
        current_rsi = rsi.iloc[-1]
        current_price = market_data.get('last')
        
        # Buy when oversold
        if current_rsi < self.rsi_oversold:
            return {
                'action': 'buy',
                'amount': self.amount_usd / current_price,
                'reason': f'RSI oversold: {current_rsi:.2f}'
            }
        
        # Sell when overbought
        if current_rsi > self.rsi_overbought:
            return {
                'action': 'sell',
                'reason': f'RSI overbought: {current_rsi:.2f}'
            }
        
        return {'action': 'hold'}
```

---

## Testing Your Strategy

### 1. Backtest Your Strategy

Test on historical data before risking real money:

```bash
python cli.py
# Select option 2: Run backtest
# Choose your strategy
# Select date range and symbol
```

### 2. Paper Trading

Test with live data but simulated trades:

```bash
python cli.py
# Select option 3: Create new configuration
# Enable paper trading: y
# Select your strategy
```

### 3. Live Trading

Only after thorough testing:

```bash
python cli.py
# Select option 3: Create new configuration
# Enable paper trading: n
# Enter API credentials
# Select your strategy
```

---

## Best Practices

### 1. **Always Check for Data**
```python
df = market_data.get('ohlcv')
if df is None or df.empty or len(df) < 50:
    return {'action': 'hold'}
```

### 2. **Use Logging**
```python
from utils.logger import get_logger
logger = get_logger(__name__)

logger.info(f"RSI: {current_rsi:.2f}")
logger.debug(f"Price: {current_price}")
```

### 3. **Make Parameters Configurable**
```python
def __init__(self, config):
    super().__init__(config)
    self.params = config.get('params', {})
    # Use .get() with defaults
    self.amount_usd = self.params.get('amount_usd', 100.0)
    self.rsi_period = self.params.get('rsi_period', 14)
```

### 4. **Document Your Strategy**
```python
class MyStrategy(StrategyPlugin):
    """
    Brief description of your strategy.
    
    Parameters:
    - param1: Description (default: value)
    - param2: Description (default: value)
    
    Strategy Logic:
    - Buy when: condition
    - Sell when: condition
    """
```

### 5. **Handle Edge Cases**
```python
# Check for sufficient data
if len(df) < self.longest_period:
    return {'action': 'hold'}

# Check for NaN values
if pd.isna(current_rsi):
    return {'action': 'hold'}

# Validate prices
if current_price <= 0:
    return {'action': 'hold'}
```

### 6. **Test Thoroughly**
- Backtest on multiple time periods
- Test in paper trading mode
- Start with small amounts in live trading
- Monitor logs for unexpected behavior

---

## Need Help?

- **Example Strategies**: See `src/plugins/strategies/dca.py` and `advanced_dca.py`
- **Base Class**: See `src/plugins/base/strategy_plugin.py`
- **Indicators**: See `src/plugins/indicators.py`
- **Issues**: Open an issue on GitHub

Happy trading! 🚀

