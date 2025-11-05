# Saved Backtest Results

This folder contains saved backtest logs and results that demonstrate the performance of various trading strategies.

## Purpose

These saved backtests serve multiple purposes:
1. **Historical Record**: Maintain a history of successful strategy tests
2. **Performance Validation**: Provide proof of strategy effectiveness
3. **Marketing Material**: Demonstrate value proposition to potential users
4. **Development Reference**: Compare performance across strategy iterations
5. **Repository Documentation**: Include in version control for transparency

## File Naming Convention

Backtest files follow this naming pattern:
```
backtest_YYYYMMDD_HHMMSS_SYMBOL_STRATEGY.log
backtest_results_SYMBOL_STARTDATE_ENDDATE.json
```

Example:
- `backtest_20251104_194439_BTC-USD_advanced_dca.log` - Full execution log
- `backtest_results_BTC-USDT_2024-11-04_2025-11-04.json` - Results data in JSON format

## Current Saved Tests

### 1. Advanced DCA - 1 Year BTC Test (Nov 2024 - Nov 2025)

**Files:**
- `backtest_20251104_194439_BTC-USD_advanced_dca.log`
- `backtest_results_BTC-USDT_2024-11-04_2025-11-04.json`

**Summary:**
- Strategy: Advanced Dollar Cost Averaging
- Asset: BTC/USDT
- Timeframe: 1 minute candles
- Period: 1 year (525,601 candles)
- Initial Capital: $100.00
- Final Equity: $133.86
- Return: +33.86%
- Win Rate: 100% (780 wins, 0 losses)
- Max Drawdown: 14.14%

**Documentation:** See `docs/backtest_examples/advanced_dca_1year_btc_analysis.md` for detailed analysis

## How to Save a Backtest

After running a backtest, you can save the results to this folder:

### Option 1: Manual Copy
```bash
# Copy log file
copy logs\backtest\backtest_YYYYMMDD_HHMMSS_SYMBOL_STRATEGY.log logs\backtest\saved\

# Copy JSON results
copy backtest_results_SYMBOL_STARTDATE_ENDDATE.json logs\backtest\saved\
```

### Option 2: Automated (Future Enhancement)
The backtest engine could be enhanced to automatically save notable results based on:
- Performance thresholds (e.g., >20% return)
- Win rate thresholds (e.g., >70%)
- User confirmation after viewing results

## Using Saved Results

### For Development
- Compare strategy performance across iterations
- Identify optimal parameter configurations
- Validate bug fixes don't degrade performance

### For Marketing
- Include in website "Proven Results" section
- Share in social media posts
- Include in pitch decks and presentations
- Demonstrate transparency and track record

### For Analysis
- Load JSON files for custom analysis
- Generate charts and visualizations
- Compare across different market conditions
- Identify strategy strengths and weaknesses

## Best Practices

1. **Document Each Test**: Create a corresponding markdown file in `docs/backtest_examples/` for each saved test
2. **Include Context**: Note market conditions, strategy parameters, and any special circumstances
3. **Version Control**: Commit saved tests to git for historical tracking
4. **Regular Cleanup**: Archive very old tests or move to separate archive folder
5. **Naming Consistency**: Follow the established naming convention

## JSON File Structure

The JSON results file contains:
```json
{
  "metadata": {
    "symbol": "BTC/USDT",
    "timeframe": "1m",
    "start_date": "2024-11-04",
    "end_date": "2025-11-04",
    "initial_balance": 100.0,
    "strategy": "advanced_dca"
  },
  "performance": {
    "final_equity": 133.86,
    "total_return": 33.86,
    "total_return_pct": 33.86,
    "max_drawdown": 14.14,
    "win_rate": 100.0
  },
  "trades": [
    {
      "timestamp": "2024-11-04T...",
      "type": "buy",
      "price": 68605.53,
      "amount": 0.00014576,
      "cost": 10.0
    },
    ...
  ],
  "equity_curve": [...]
}
```

## Future Enhancements

Potential improvements to the saved backtest system:
- [ ] Automated saving of high-performing backtests
- [ ] Comparison tool to analyze multiple saved tests
- [ ] Web-based viewer for backtest results
- [ ] Export to PDF for sharing
- [ ] Integration with performance tracking dashboard
- [ ] Automated report generation

---

**Note**: Always include a disclaimer when sharing backtest results publicly:
> "Past performance does not guarantee future results. Cryptocurrency trading involves substantial risk. These results are from historical backtesting and may not reflect live trading performance."

