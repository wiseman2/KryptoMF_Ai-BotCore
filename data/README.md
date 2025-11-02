# Data Directory

This directory stores historical market data and backtest results.

## Structure

```
data/
├── historical/          # Cached historical OHLCV data
│   ├── binanceus_BTC-USD_1h_2024-01-01_2024-06-30.csv
│   ├── coinbasepro_ETH-USD_4h_2024-05-01_2024-11-01.csv
│   └── ...
├── backtest_results_*.json  # Backtest results (auto-generated)
└── README.md           # This file
```

## Historical Data Cache

When you run backtests, historical data is automatically downloaded from exchanges and cached here to avoid re-downloading.

### Cache File Naming

Format: `{exchange}_{symbol}_{timeframe}_{start_date}_{end_date}.csv`

Examples:
- `binanceus_BTC-USD_1h_2024-01-01_2024-12-31.csv`
- `coinbasepro_ETH-USD_4h_2024-06-01_2024-11-01.csv`
- `kraken_BTC-USDT_1d_2023-01-01_2024-01-01.csv`

### Cache Benefits

- **Instant Loading** - Reusing the same parameters loads from cache instantly
- **No API Limits** - Avoid exchange API rate limits
- **Offline Backtesting** - Test strategies without internet connection
- **Reproducibility** - Same data for consistent backtest results

### Managing Cache

**View cache size:**
```bash
# Windows
dir data\historical

# Linux/Mac
du -sh data/historical/*
```

**Clear cache:**
```bash
# Windows
del data\historical\*.csv

# Linux/Mac
rm data/historical/*.csv
```

**Force re-download:**
- Delete specific cache file
- Or use a different date range

## Backtest Results

Backtest results are saved as JSON files in this directory.

### File Naming

Format: `backtest_results_{symbol}_{start_date}_{end_date}.json`

Examples:
- `backtest_results_BTC-USD_2024-01-01_2024-06-30.json`
- `backtest_results_ETH-USD_2024-05-01_2024-11-01.json`

### Contents

Each JSON file contains:
- Performance summary (return, win rate, max drawdown)
- Trade statistics
- Complete trade log
- Equity curve data

### Example

```json
{
  "summary": {
    "initial_balance": 10000.0,
    "final_equity": 12450.0,
    "total_return": 2450.0,
    "total_return_pct": 24.5,
    "max_drawdown": 8.32,
    "total_trades": 45,
    "win_rate": 68.2
  },
  "trades": [...],
  "equity_curve": [...]
}
```

## Data Formats

### Historical Data CSV

Columns: `timestamp`, `open`, `high`, `low`, `close`, `volume`

```csv
timestamp,open,high,low,close,volume
1704067200,42150.5,42380.2,42100.0,42250.8,1234.56
1704070800,42250.8,42450.0,42200.0,42380.5,2345.67
```

**Note:** Timestamp is in Unix seconds (not milliseconds).

### Custom Data

You can add your own CSV files here and use them with:

```bash
python cli.py --config config/bot_config.yaml \
  --backtest \
  --backtest-data data/my_custom_data.csv
```

## .gitignore

This directory is configured to:
- ✅ Track this README.md
- ❌ Ignore all CSV files (historical data)
- ❌ Ignore all JSON files (backtest results)

This prevents accidentally committing large data files to git.

## Disk Space

Historical data can consume significant disk space depending on timeframe and duration:

| Timeframe | 1 Month | 6 Months | 1 Year |
|-----------|---------|----------|--------|
| 1 minute  | ~4 MB   | ~25 MB   | ~50 MB |
| 5 minutes | ~0.8 MB | ~5 MB    | ~10 MB |
| 1 hour    | ~0.07 MB| ~0.4 MB  | ~0.8 MB|
| 1 day     | ~0.003 MB| ~0.02 MB| ~0.03 MB|

**Tip:** Use higher timeframes (1h, 4h, 1d) for longer backtests to save space.

## Troubleshooting

### "Permission denied" when writing cache

**Solution:** Ensure the `data/historical/` directory exists and is writable:

```bash
# Create directory if missing
mkdir -p data/historical

# Fix permissions (Linux/Mac)
chmod 755 data/historical
```

### Cache files are huge

**Solution:** 
- Use higher timeframes (1h instead of 1m)
- Use shorter date ranges
- Delete old cache files you don't need

### "File not found" when loading cache

**Solution:**
- Check that the file exists in `data/historical/`
- Verify the filename matches the expected format
- Try re-downloading by deleting the cache file

## Best Practices

1. **Keep cache organized** - Delete old/unused cache files periodically
2. **Backup important results** - Copy backtest JSON files to a safe location
3. **Use version control** - Don't commit data files to git (already in .gitignore)
4. **Monitor disk space** - Large backtests can consume significant space
5. **Document custom data** - If adding custom CSV files, document their source

---

**Note:** This directory is automatically created when you run your first backtest.

