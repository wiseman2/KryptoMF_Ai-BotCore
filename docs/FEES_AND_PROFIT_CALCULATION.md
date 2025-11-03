# Trading Fees and Profit Calculation

This document explains how KryptoMF Bot Core handles trading fees and profit calculations to ensure you get your desired profit **after all fees**.

## Table of Contents

- [Why Fees Matter](#why-fees-matter)
- [Fee Types](#fee-types)
- [Profit Calculation Formula](#profit-calculation-formula)
- [Configuration](#configuration)
- [Examples](#examples)
- [RSI Rising Check](#rsi-rising-check)

---

## Why Fees Matter

Trading fees can significantly impact your profitability. Without accounting for fees:

- ❌ You might sell at what looks like a profit, but actually lose money
- ❌ Your profit targets won't be accurate
- ❌ You'll have unexpected losses from fee accumulation

With proper fee accounting:

- ✅ You know exactly what sell price gives you your target profit
- ✅ All calculations are transparent and accurate
- ✅ You avoid unexpected losses

---

## Fee Types

### Maker Fee
- **When**: You add liquidity to the order book (limit orders)
- **Typical**: 0.1% - 0.5%
- **Example**: Placing a limit buy order below current price

### Taker Fee
- **When**: You remove liquidity from the order book (market orders)
- **Typical**: 0.1% - 0.5%
- **Example**: Placing a market sell order at current price

### Common Exchange Fees

| Exchange | Maker Fee | Taker Fee |
|----------|-----------|-----------|
| Binance / Binance.US | 0.1% | 0.1% |
| Coinbase Pro | 0.5% | 0.5% |
| Kraken | 0.16% | 0.26% |
| KuCoin | 0.1% | 0.1% |
| OKX | 0.08% | 0.1% |

**Note**: Fees may be lower with high volume or holding exchange tokens (BNB, KCS, etc.)

---

## Profit Calculation Formula

### Step 1: Calculate Total Cost (Buy + Fee)

```
total_cost = buy_price × (1 + maker_fee%)
```

**Example:**
- Buy price: $50,000
- Maker fee: 0.1%
- Total cost: $50,000 × 1.001 = **$50,050**

### Step 2: Add Desired Profit

```
target_with_profit = total_cost × (1 + profit_target%)
```

**Example:**
- Total cost: $50,050
- Profit target: 1.0%
- Target with profit: $50,050 × 1.01 = **$50,550.50**

### Step 3: Account for Sell Fee

```
sell_price = target_with_profit / (1 - taker_fee%)
```

**Example:**
- Target with profit: $50,550.50
- Taker fee: 0.1%
- Sell price: $50,550.50 / 0.999 = **$50,601.05**

### Complete Formula

```python
sell_price = (buy_price × (1 + maker_fee%) × (1 + profit_target%)) / (1 - taker_fee%)
```

---

## Configuration

### Interactive Setup

When you run the bot without a config file, it will ask:

```
Step 6: Trading Fees
----------------------------------------------------------------------
ℹ️  Trading fees are crucial for accurate profit calculations
  • Maker fee: When you add liquidity (limit orders)
  • Taker fee: When you remove liquidity (market orders)

Common exchange fees:
  • Binance/Binance.US: 0.1% maker, 0.1% taker
  • Coinbase Pro: 0.5% maker, 0.5% taker
  • Kraken: 0.16% maker, 0.26% taker

Maker fee (%) [0.1]: 0.1
Taker fee (%) [0.1]: 0.1

Step 7: Profit Target
----------------------------------------------------------------------
ℹ️  Minimum profit percentage before selling
  • This is AFTER accounting for all trading fees
  • Example: 1.0% means you need 1% profit after buy+sell fees

Minimum profit target (%) [1.0]: 1.0
```

### YAML Configuration

```yaml
# Trading fees
fees:
  maker: 0.1  # Maker fee percentage
  taker: 0.1  # Taker fee percentage

# Profit target (after fees)
profit_target: 1.0  # 1.0% net profit
```

---

## Examples

### Example 1: Binance.US (0.1% fees, 1% profit target)

**Buy:**
- Price: $50,000
- Fee: $50 (0.1%)
- **Total cost: $50,050**

**Sell:**
- Target profit: 1% of $50,050 = $500.50
- Target price: $50,550.50
- Fee: $50.55 (0.1%)
- **Sell price: $50,601.05**

**Result:**
- Proceeds: $50,601.05 - $50.55 = $50,550.50
- Profit: $50,550.50 - $50,050 = $500.50
- **Profit %: 1.0% ✓**

### Example 2: Coinbase Pro (0.5% fees, 2% profit target)

**Buy:**
- Price: $50,000
- Fee: $250 (0.5%)
- **Total cost: $50,250**

**Sell:**
- Target profit: 2% of $50,250 = $1,005
- Target price: $51,255
- Fee: $256.28 (0.5%)
- **Sell price: $51,511.28**

**Result:**
- Proceeds: $51,511.28 - $257.56 = $51,253.72
- Profit: $51,253.72 - $50,250 = $1,003.72
- **Profit %: 2.0% ✓**

### Example 3: High Fees Impact

**Scenario A: No fee accounting**
- Buy at $50,000
- Want 1% profit
- Sell at $50,500 (naive calculation)
- **Actual result: LOSS of $50!**

**Scenario B: With fee accounting**
- Buy at $50,000
- Want 1% profit after fees
- Sell at $50,601.05 (correct calculation)
- **Actual result: $500.50 profit (1.0%) ✓**

---

## RSI Rising Check

### What It Does

The RSI rising check is an **optional feature** that helps avoid "catching a falling knife" - buying when the price is still dropping.

**Traditional RSI:**
- RSI < 30 = Oversold → Buy signal

**Problem:**
- RSI can stay oversold while price continues falling
- You might buy too early and watch price drop further

**RSI Rising Check (Optional):**
- RSI < 30 AND RSI is rising for 3+ periods → Buy signal
- This indicates the downtrend is reversing
- **User preference** - Some traders prefer this, others don't

### Configuration

This is a **user preference** - you can enable or disable it based on your trading style:

```yaml
strategy_params:
  indicators:
    rsi:
      enabled: true
      period: 14
      oversold: 30
      overbought: 70
      check_rising: true  # Set to false if you don't want this check
```

**When to enable:**
- You want to wait for momentum reversal
- You're trading volatile assets
- You prefer fewer, higher-quality entries

**When to disable:**
- You want to buy at the lowest possible price
- You're comfortable with temporary drawdown
- You prefer more frequent entries

### How It Works

```python
# Check 1: Is RSI oversold?
rsi = 28  # Yes, below 30

# Check 2: Is RSI rising?
rsi_history = [25, 26, 27, 28]  # Yes, rising for 3 periods

# Result: BUY SIGNAL ✓
```

**Without rising check:**
```python
rsi_history = [35, 32, 30, 28]  # Falling
# Would still buy at RSI=28, but price might drop more
```

**With rising check:**
```python
rsi_history = [35, 32, 30, 28]  # Falling
# WAIT - RSI is oversold but still falling
# Don't buy yet, wait for reversal
```

### Benefits

1. **Better Entry Timing** - Buy when momentum is reversing, not while still falling
2. **Fewer False Signals** - Avoid buying during strong downtrends
3. **Higher Win Rate** - Enter positions closer to the bottom
4. **Less Drawdown** - Avoid watching your position drop immediately after buying

### Example Scenario

**BTC Price Action:**
```
Day 1: $52,000 → RSI 45
Day 2: $50,000 → RSI 35
Day 3: $48,000 → RSI 28 (oversold, but falling)
Day 4: $47,000 → RSI 25 (still falling - DON'T BUY)
Day 5: $47,500 → RSI 27 (rising!)
Day 6: $48,000 → RSI 29 (rising!)
Day 7: $48,500 → RSI 31 (rising! - BUY SIGNAL ✓)
```

**Without RSI rising check:**
- Would buy on Day 3 at $48,000
- Watch it drop to $47,000 (2.1% loss)
- Eventually recover

**With RSI rising check:**
- Wait for reversal signal
- Buy on Day 7 at $48,500
- Already near the bottom
- Less drawdown, better entry

---

## Bot Output Example

When you make a purchase, the bot will show:

```
============================================================
DCA Purchase Complete
============================================================
  Purchase #1
  Buy Price: $50,000.00
  Amount: 0.00040000
  Cost: $20.00
  Buy Fee: 0.1%

  Target Sell Price: $50,601.05
  Profit Target: 1.0% (after fees)
  Actual Profit: 1.00%
  Sell Fee: 0.1%

  Total purchased: 0.00040000
  Total spent: $20.00
  Average price: $50,000.00
============================================================
```

This shows you exactly:
- What you paid (including fees)
- What price you need to sell at
- What your actual profit will be

---

## Verification

You can verify the calculations yourself:

```python
from plugins.indicators import TechnicalIndicators

# Calculate sell price
sell_price = TechnicalIndicators.calculate_sell_price_with_fees(
    buy_price=50000,
    buy_fee_percent=0.1,
    sell_fee_percent=0.1,
    profit_target_percent=1.0
)
print(f"Sell price: ${sell_price:,.2f}")  # $50,601.05

# Verify actual profit
actual_profit = TechnicalIndicators.calculate_actual_profit_percent(
    buy_price=50000,
    sell_price=50601.05,
    buy_fee_percent=0.1,
    sell_fee_percent=0.1
)
print(f"Actual profit: {actual_profit:.2f}%")  # 1.00%
```

---

## Best Practices

1. **Know Your Fees** - Check your exchange's fee schedule
2. **Use Limit Orders** - Lower maker fees vs taker fees
3. **Consider Volume Discounts** - Higher volume = lower fees
4. **Hold Exchange Tokens** - BNB, KCS, etc. for fee discounts
5. **Set Realistic Targets** - Higher fees require higher profit targets
6. **Monitor Actual Results** - Verify the bot's calculations match reality

---

## Troubleshooting

### "My profit is less than expected"

**Check:**
1. Are you using market orders? (Higher taker fees)
2. Did fees increase on your exchange?
3. Is slippage affecting your fills?
4. Are you accounting for both buy AND sell fees?

### "The sell price seems too high"

**This is normal!** The sell price must be higher to account for:
1. Buy fee (already paid)
2. Desired profit
3. Sell fee (will be paid)

**Example:**
- Buy at $50,000 with 0.1% fee = $50,050 total cost
- Want 1% profit = $500.50
- Need $50,550.50 after sell fee
- Sell fee is 0.1%, so sell price = $50,601.05
- **$601.05 higher than buy price for 1% net profit**

---

## Summary

✅ **Always account for fees** - Both buy and sell  
✅ **Use the bot's calculations** - They're accurate  
✅ **Verify with your exchange** - Check actual fees paid  
✅ **Set realistic targets** - Higher fees need higher targets  
✅ **Enable RSI rising check** - Better entry timing  
✅ **Monitor results** - Track actual vs expected profit  

The bot handles all the complex math for you, ensuring you get your desired profit after all fees!

