# Backtesting Guide

## Overview

The KryptoMF_Ai Bot Core includes a comprehensive backtesting framework that allows you to test your trading strategies on historical data before risking real money.

## Features

### Core Capabilities
- ✅ **Interactive Setup** - Guided prompts for all parameters
- ✅ **Automatic Data Fetching** - Downloads historical OHLCV data from exchanges
- ✅ **Data Caching** - Saves downloaded data locally to avoid re-downloading
- ✅ **Multiple Timeframes** - 1m, 5m, 15m, 1h, 4h, 1d support
- ✅ **Configurable Parameters** - Set initial balance, amount per trade, profit % per backtest
- ✅ **Real-Time Metrics** - Monitor cash, active trades, invested amount, unrealized P/L
- ✅ **Performance Analysis** - Win rate, max drawdown, average win/loss
- ✅ **Session Logging** - Every backtest saved to dedicated log file

### What Gets Tested
- Strategy buy/sell signals
- Indicator calculations (RSI, MACD, EMA, etc.)
- Profit calculations with fees
- Position management
- DCA cost basis reduction
- Progressive step-down price requirements
- Trade execution logic

## Quick Start

### Interactive Backtesting (Recommended)

```bash
python cli.py --config config/bot_config.yaml --backtest
```

You'll be guided through:

1. **Trading Pair** - Default: BTC/USDT (press Enter to use default)
2. **Timeframe** - Default: 1h (press Enter to use default)
3. **Date Range** - Quick options or custom dates
4. **Backtest Parameters** - Initial balance, amount per trade, min profit %
5. **Data Download** - Automatic with progress display

### Command-Line Backtesting

```bash
# With CSV file
python cli.py --config config/bot_config.yaml \
  --backtest \
  --backtest-data data/BTC-USD-1h.csv

# With date range
python cli.py --config config/bot_config.yaml \
  --backtest \
  --backtest-start 2024-01-01 \
  --backtest-end 2024-12-31
```

## Interactive Setup Walkthrough

### Step 1: Trading Pair

```
Step 1: Select Trading Pair
Examples: BTC/USD, ETH/USD, BTC/USDT, ETH/BTC
Enter trading pair (default: BTC/USDT): 
```

**Options:**
- Press **Enter** to use BTC/USDT (recommended)
- Type any valid trading pair (e.g., ETH/USD, BTC/USD)

**Tips:**
- Use USDT pairs for better liquidity and more data
- Make sure the pair exists on your configured exchange

### Step 2: Timeframe

```
Step 2: Select Timeframe
Available timeframes:
  1m     - 1 minute
  5m     - 5 minutes
  15m    - 15 minutes
  1h     - 1 hour
  4h     - 4 hours
  1d     - 1 day
Enter timeframe (default: 1h): 
```

**Recommendations:**
- **1h** - Good balance of data points and speed (default)
- **5m** - More granular, slower backtest, more data
- **1d** - Fast backtest, less granular
- **1m** - Very detailed but SLOW (use short date ranges)

### Step 3: Date Range

```
Step 3: Select Date Range
Quick options:
  1 - Last 1 month
  2 - Last 3 months
  3 - Last 6 months
  4 - Last 1 year
  5 - Custom date range
Select option (1-5): 
```

**Quick Options:**
- **1** - Last month (~720 candles @ 1h)
- **2** - Last 3 months (~2,160 candles @ 1h)
- **3** - Last 6 months (~4,320 candles @ 1h)
- **4** - Last year (~8,760 candles @ 1h)
- **5** - Custom start/end dates

**Custom Date Range:**
```
Enter start date (YYYY-MM-DD): 2024-01-01
Enter end date (YYYY-MM-DD): 2024-06-30
```

### Step 4: Backtest Parameters

```
BACKTEST PARAMETERS

Initial Balance (default: $10000.00): 
Amount Per Trade (default: $100.00): 
Min Profit Percent (default: 0.5%): 
```

**Parameters:**
- **Initial Balance** - Starting capital for backtest
- **Amount Per Trade** - How much to invest per buy order
- **Min Profit %** - Minimum profit target for sells

**Tips:**
- Press **Enter** to use config defaults
- Override to test different scenarios
- Use realistic values (don't test with $1M if you have $1K)

### Step 5: Data Estimate & Download

```
═══ DATA ESTIMATE ═══
Symbol:           BTC/USDT
Timeframe:        1h (1 hour)
Date Range:       2024-05-04 to 2025-11-04
Duration:         365 days
Expected Candles: ~8,760
Estimated Size:   ~0.84 MB

Proceed with download? (y/n): 
```

**What This Shows:**
- Exact date range
- Number of candles to download
- Estimated file size
- Confirmation before downloading

Type **y** to proceed or **n** to cancel.

## Backtest Output

### Real-Time Progress

Every 1000 candles, you'll see:

```
[2025-11-04 16:25:35] INFO - Progress: 1.3% (1000/74233 candles) | Cash: $90.00 | Active Trades: 1 | Invested: $10.00 | Unrealized P/L: +$0.50 | Total P/L: +$0.50 (+0.50%)
[2025-11-04 16:25:40] INFO - Progress: 2.7% (2000/74233 candles) | Cash: $70.00 | Active Trades: 3 | Invested: $30.00 | Unrealized P/L: +$2.15 | Total P/L: +$2.15 (+2.15%)
```

**Metrics Explained:**
- **Progress** - Percentage complete and candle count
- **Cash** - Available balance (not invested)
- **Active Trades** - Number of open positions
- **Invested** - Total amount in active trades
- **Unrealized P/L** - Profit/loss on open positions
- **Total P/L** - Overall performance (realized + unrealized)

### Final Results

```
══════════════════════════════════════════════════════════════════════
                          BACKTEST RESULTS                            
══════════════════════════════════════════════════════════════════════
Initial Balance:      $10,000.00
Final Balance:        $8,500.00
Final Position:       0.03788720
Final Equity:         $12,500.00
Total Profit/Loss:    +$2,500.00 (+25.00%)

Total Trades:         45
  Buy Orders:         45
  Sell Orders:        32
Winning Trades:       28
Losing Trades:        4
Win Rate:             87.5%

Max Drawdown:         -8.50%
Average Win:          +$125.50
Average Loss:         -$45.20
══════════════════════════════════════════════════════════════════════
```

**Key Metrics:**
- **Final Equity** - Balance + position value (total worth)
- **Total P/L** - Overall profit/loss
- **Win Rate** - Percentage of profitable trades
- **Max Drawdown** - Largest peak-to-trough decline
- **Average Win/Loss** - Average profit per winning/losing trade

## Session Logs

Every backtest creates a dedicated log file:

```
logs/backtest/backtest_20251104_162530_BTC-USDT_advanced_dca.log
```

**Filename Format:**
```
{mode}_{timestamp}_{symbol}_{strategy}.log
```

**What's Logged:**
- All configuration parameters
- Progress updates (every 1000 candles)
- Buy/sell signals with reasons
- Trade executions
- Final results and statistics
- Any errors or warnings

**Use Cases:**
- Review strategy decisions
- Debug unexpected results
- Share performance with others
- Prove strategy effectiveness
- Compare different backtests

## Data Caching

Downloaded data is cached in `data/historical/`:

```
data/historical/binanceus_BTC-USDT_1h_2024-01-01_2024-12-31.csv
```

**Cache Benefits:**
- Instant loading on repeat backtests
- No API rate limits
- Offline backtesting
- Faster iteration

**Cache Management:**
```bash
# View cached data
ls data/historical/

# Delete specific cache
rm data/historical/binanceus_BTC-USDT_1h_2024-01-01_2024-12-31.csv

# Clear all cache
rm data/historical/*.csv
```

## CSV File Format

If providing your own CSV file:

```csv
timestamp,open,high,low,close,volume
1704067200,42150.5,42380.2,42100.0,42250.8,1234.56
1704070800,42250.8,42450.0,42200.0,42380.5,2345.67
1704074400,42380.5,42500.0,42350.0,42480.0,3456.78
```

**Requirements:**
- Header row with column names
- Unix timestamp (seconds since epoch)
- OHLCV data (open, high, low, close, volume)
- Chronological order (oldest first)

## Best Practices

### 1. Start Small
- Test 1 month before testing 1 year
- Use 1h timeframe before 1m
- Verify results make sense

### 2. Use Realistic Parameters
- Match your actual trading capital
- Use realistic position sizes
- Account for fees (bot does this automatically)

### 3. Test Multiple Scenarios
- Different date ranges (bull/bear markets)
- Different timeframes
- Different parameter combinations

### 4. Validate Results
- Check if trades make sense
- Review buy/sell signals in logs
- Compare to manual analysis

### 5. Don't Overfit
- Don't optimize for one specific period
- Test on out-of-sample data
- Be skeptical of "too good" results

## Troubleshooting

### No Trades Executed

**Possible Causes:**
- Indicators too restrictive (e.g., price_drop always required)
- Insufficient balance
- No buy signals triggered

**Solutions:**
- Check strategy configuration
- Review indicator settings
- Lower indicator agreement threshold
- Check session log for details

### Download Fails

**Possible Causes:**
- Exchange API rate limits
- Invalid trading pair
- No data for date range

**Solutions:**
- Wait a few minutes and retry
- Verify pair exists on exchange
- Try shorter date range
- Check internet connection

### Slow Backtest

**Causes:**
- Too many candles (1m timeframe, long range)
- Complex strategy with many indicators

**Solutions:**
- Use larger timeframe (1h instead of 1m)
- Shorter date range
- Disable unnecessary indicators

## Advanced Usage

### Testing Strategy Changes

1. Modify strategy code
2. Run backtest with same parameters
3. Compare results to baseline
4. Review session logs for differences

### Parameter Optimization

Test different parameter combinations:

```bash
# Test different profit targets
# Run backtest, enter 0.5% profit
# Run backtest, enter 1.0% profit
# Run backtest, enter 2.0% profit
# Compare results
```

### Sharing Results

```bash
# Zip session log
zip backtest_results.zip logs/backtest/backtest_20251104_162530_BTC-USDT_advanced_dca.log

# Share on GitHub, Discord, Twitter, etc.
```

**Benefits:**
- Prove strategy performance
- Get feedback from community
- Build credibility
- Attract users to your bot

## Advanced DCA: Progressive Step-Down

The Advanced DCA strategy includes **progressive step-down** logic that prevents buying at similar price levels.

### How It Works

Each additional purchase requires the price to be progressively lower than the previous purchase:

**Formula:**
- Base step-down = min(profit_target%, 5%)
- Purchase N requires: `(base × multiplier^(N-2))%` drop from Purchase N-1
- Each step is capped at `max_step_down` (default: 5%)

**Example with 0.5% profit target:**

| Purchase | Price Required | Drop from Previous |
|----------|----------------|-------------------|
| 1 | $50,000 | None (first buy) |
| 2 | ≤ $49,750 | 0.5% |
| 3 | ≤ $49,377 | 0.75% |
| 4 | ≤ $48,823 | 1.125% |
| 5 | ≤ $48,000 | 1.6875% |
| 10 | ≤ $42,500 | ~5% (capped) |

**Result:** 10 purchases cover a ~15% price range without clustering!

### Configuration

```yaml
strategy_params:
  step_down_multiplier: 1.5    # How much to increase each step (default: 1.5)
  max_step_down: 5.0           # Maximum step-down per purchase (default: 5%)
```

The base step-down is automatically calculated from your profit target (capped at 5%).

### Benefits

✅ **Prevents clustering** - Won't buy multiple times at similar prices
✅ **Covers wider range** - 10 purchases can cover 15-20% price drop
✅ **Automatic scaling** - Based on your profit target
✅ **Safety cap** - Won't require unrealistic price drops
✅ **True DCA** - Buys more as price drops significantly

### Backtest Example

```
Progress: 25.0% | Cash: $500.00 | Active Trades: 5 | Invested: $500.00
  Purchase 1: $50,000
  Purchase 2: $49,750 (0.5% lower)
  Purchase 3: $49,377 (0.75% lower)
  Purchase 4: $48,823 (1.125% lower)
  Purchase 5: $48,000 (1.6875% lower)

Price at $49,500 - HOLD (need $47,520 for next purchase - 2.53% drop)
```

## Next Steps

After successful backtesting:

1. **Paper Trading** - Test with live data, no real money
2. **Small Live Test** - Start with minimal capital
3. **Monitor Closely** - Watch first few trades carefully
4. **Scale Gradually** - Increase position size slowly

**Remember:** Past performance doesn't guarantee future results!

---

**See Also:**
- [Strategy Development Guide](STRATEGY_DEVELOPMENT.md)
- [Configuration Examples](../config/strategy_config_example.yaml)
- [README](../README.md)

