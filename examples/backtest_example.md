# Backtesting Examples

This guide shows how to use the backtesting feature to test your strategies on historical data.

## Quick Start

The easiest way to backtest is using the interactive mode:

```bash
python cli.py --config config/bot_config.yaml --backtest
```

This will guide you through selecting:
- Trading pair (BTC/USD, ETH/USD, etc.)
- Timeframe (1m, 5m, 1h, 1d, etc.)
- Date range (1 month, 6 months, 1 year, or custom)

## Data Size Estimates

Here are approximate data sizes for different timeframes and durations:

### 1 Month (30 days)

| Timeframe | Candles | Size (MB) |
|-----------|---------|-----------|
| 1 minute  | 43,200  | ~4.1 MB   |
| 5 minutes | 8,640   | ~0.8 MB   |
| 15 minutes| 2,880   | ~0.3 MB   |
| 1 hour    | 720     | ~0.07 MB  |
| 4 hours   | 180     | ~0.02 MB  |
| 1 day     | 30      | ~0.003 MB |

### 3 Months (90 days)

| Timeframe | Candles | Size (MB) |
|-----------|---------|-----------|
| 1 minute  | 129,600 | ~12.4 MB  |
| 5 minutes | 25,920  | ~2.5 MB   |
| 15 minutes| 8,640   | ~0.8 MB   |
| 1 hour    | 2,160   | ~0.21 MB  |
| 4 hours   | 540     | ~0.05 MB  |
| 1 day     | 90      | ~0.009 MB |

### 6 Months (180 days)

| Timeframe | Candles | Size (MB) |
|-----------|---------|-----------|
| 1 minute  | 259,200 | ~24.7 MB  |
| 5 minutes | 51,840  | ~4.9 MB   |
| 15 minutes| 17,280  | ~1.6 MB   |
| 1 hour    | 4,320   | ~0.41 MB  |
| 4 hours   | 1,080   | ~0.10 MB  |
| 1 day     | 180     | ~0.02 MB  |

### 1 Year (365 days)

| Timeframe | Candles | Size (MB) |
|-----------|---------|-----------|
| 1 minute  | 525,600 | ~50.1 MB  |
| 5 minutes | 105,120 | ~10.0 MB  |
| 15 minutes| 35,040  | ~3.3 MB   |
| 1 hour    | 8,760   | ~0.84 MB  |
| 4 hours   | 2,190   | ~0.21 MB  |
| 1 day     | 365     | ~0.03 MB  |

## Example Backtest Sessions

### Example 1: Quick 1-Month Test

```bash
python cli.py --config config/bot_config.yaml --backtest
```

```
Enter trading pair: BTC/USD
Enter timeframe (default: 1h): 1h
Select option (1-5): 1

═══ DATA ESTIMATE ═══
Symbol:           BTC/USD
Timeframe:        1h (1 hour)
Date Range:       2024-10-02 to 2024-11-02
Duration:         31 days
Expected Candles: ~744
Estimated Size:   ~0.07 MB

Proceed with download? (y/n): y
```

**Result:** Small, fast download. Good for quick strategy validation.

### Example 2: Comprehensive 6-Month Test

```bash
python cli.py --config config/bot_config.yaml --backtest
```

```
Enter trading pair: ETH/USD
Enter timeframe (default: 1h): 4h
Select option (1-5): 3

═══ DATA ESTIMATE ═══
Symbol:           ETH/USD
Timeframe:        4h (4 hours)
Date Range:       2024-05-02 to 2024-11-02
Duration:         184 days
Expected Candles: ~1,104
Estimated Size:   ~0.11 MB

Proceed with download? (y/n): y
```

**Result:** Moderate download. Good balance between data coverage and speed.

### Example 3: Detailed 1-Year Test with 15-Minute Candles

```bash
python cli.py --config config/bot_config.yaml --backtest
```

```
Enter trading pair: BTC/USDT
Enter timeframe (default: 1h): 15m
Select option (1-5): 4

═══ DATA ESTIMATE ═══
Symbol:           BTC/USDT
Timeframe:        15m (15 minutes)
Date Range:       2023-11-02 to 2024-11-02
Duration:         366 days
Expected Candles: ~35,136
Estimated Size:   ~3.35 MB

Proceed with download? (y/n): y
```

**Result:** Larger download but very detailed data. Best for fine-tuning strategies.

### Example 4: Custom Date Range

```bash
python cli.py --config config/bot_config.yaml --backtest
```

```
Enter trading pair: BTC/USD
Enter timeframe (default: 1h): 1h
Select option (1-5): 5
Enter start date (YYYY-MM-DD): 2024-01-01
Enter end date (YYYY-MM-DD, or press Enter for today): 2024-06-30

═══ DATA ESTIMATE ═══
Symbol:           BTC/USD
Timeframe:        1h (1 hour)
Date Range:       2024-01-01 to 2024-06-30
Duration:         182 days
Expected Candles: ~4,368
Estimated Size:   ~0.42 MB

Proceed with download? (y/n): y
```

**Result:** Test specific market conditions (e.g., bull run, bear market, consolidation).

## Understanding the Results

After the backtest completes, you'll see:

```
══════════════════════════════════════════════════════════════════════
                          BACKTEST RESULTS
══════════════════════════════════════════════════════════════════════

═══ PERFORMANCE ═══
Initial Balance:  $10,000.00
Final Equity:     $12,450.00
Total Return:     +$2,450.00 (+24.50%)
Max Drawdown:     8.32%

═══ TRADE STATISTICS ═══
Total Trades:     45
  Buy Orders:     23
  Sell Orders:    22
Winning Trades:   15
Losing Trades:    7
Win Rate:         68.2%

Average Win:      +$245.50
Average Loss:     $-125.30
Profit Factor:    1.96
```

### Key Metrics Explained

- **Total Return** - Overall profit/loss as percentage of initial balance
- **Max Drawdown** - Largest peak-to-trough decline (lower is better)
- **Win Rate** - Percentage of profitable trades
- **Profit Factor** - Ratio of gross profit to gross loss (>1.0 is profitable)

### What to Look For

✅ **Good Strategy:**
- Win rate > 50%
- Profit factor > 1.5
- Max drawdown < 20%
- Consistent equity curve (smooth upward trend)

⚠️ **Needs Improvement:**
- Win rate < 40%
- Profit factor < 1.2
- Max drawdown > 30%
- Erratic equity curve (lots of spikes)

## Tips for Effective Backtesting

1. **Start Small** - Test 1 month first, then expand to 6-12 months
2. **Multiple Timeframes** - Test same strategy on different timeframes
3. **Different Market Conditions** - Test bull markets, bear markets, and sideways
4. **Multiple Pairs** - Test on BTC/USD, ETH/USD, etc. to verify robustness
5. **Realistic Parameters** - Use actual exchange fees and slippage
6. **Walk-Forward Testing** - Test on recent data after optimizing on older data

## Cached Data

Data is automatically cached in `data/historical/` directory:

```
data/historical/
├── binanceus_BTC-USD_1h_2024-01-01_2024-06-30.csv
├── binanceus_ETH-USD_4h_2024-05-01_2024-11-01.csv
└── coinbasepro_BTC-USD_1d_2023-01-01_2024-01-01.csv
```

**Benefits:**
- Instant loading on subsequent runs
- No API rate limits
- Offline backtesting

**To force re-download:**
- Delete the cache file
- Or use a different date range

## Advanced: Using Manual CSV Files

If you have your own data source:

```bash
python cli.py --config config/bot_config.yaml \
  --backtest \
  --backtest-data my_custom_data.csv
```

CSV format:
```csv
timestamp,open,high,low,close,volume
1704067200,42150.5,42380.2,42100.0,42250.8,1234.56
1704070800,42250.8,42450.0,42200.0,42380.5,2345.67
```

**Note:** Timestamp should be in Unix seconds (not milliseconds).

## Troubleshooting

### "No data available for symbol"

- Check that the exchange supports the trading pair
- Try a different exchange (e.g., use `binance` instead of `binanceus`)
- Verify the symbol format (BTC/USD vs BTC/USDT)

### "Rate limit exceeded"

- The bot automatically handles rate limits
- If it fails, wait a few minutes and try again
- Or use a cached file if available

### "Insufficient data"

- Some exchanges have limited historical data
- Try a shorter date range
- Or use a different exchange

## Next Steps

After backtesting:

1. **Analyze Results** - Review trade log and equity curve
2. **Optimize Parameters** - Adjust strategy settings based on results
3. **Paper Trade** - Test in real-time with paper trading mode
4. **Live Trade** - Start with small amounts on live exchange

Remember: **Past performance does not guarantee future results!**

