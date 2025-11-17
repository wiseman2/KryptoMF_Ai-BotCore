# State Persistence and Reliability Features

**Date**: 2025-11-03  
**Status**: ✅ Production Ready

This document describes the state persistence, connectivity monitoring, and reliability features implemented in KryptoMF_Ai-BotCore.

---

## 🎯 Overview

The bot now includes enterprise-grade reliability features to ensure:
- **No data loss** on crashes or restarts
- **Automatic recovery** from network issues
- **Smart resource usage** to minimize API calls
- **Trailing order management** for bot-managed trailing

---

## 💾 State Persistence

### What Gets Saved

The bot automatically saves its complete state to disk, including:

1. **Purchase History**
   - Complete buy order information (ID, price, amount, cost, timestamp, fees)
   - Complete sell order information (ID, price, amount, timestamp, fees)
   - Purchase metadata (cost basis, DCA applied, profit/loss)
   - Purchase count and totals

2. **Pending Buy Orders**
   - List of order IDs for pending buy orders
   - Prevents multiple simultaneous buy orders
   - Restored on bot restart

3. **Pending Sell Orders** (tracked within each purchase)
   - Sell order status (pending, active, pending_market, pending_trail, trailing_active, filled, cancelled, error)
   - Sell order type (limit, market, trailing_market, trailing_limit, trailing_stop)
   - Target sell price and profit target
   - Order ID and client order ID (when placed)
   - Complete sell order details when filled
   - Activation price for trailing orders

4. **Trailing State** (for bot-managed trailing)
   - Trailing status (inactive, waiting, active, triggered)
   - Direction (up for sells, down for buys)
   - Activation price
   - Current watermark (highest/lowest price seen)
   - Trailing percentage

5. **Bot Statistics**
   - Total trades
   - Win/loss ratio
   - Total profit and DCA applied
   - Current positions

6. **Connectivity Status**
   - Last successful connection
   - Failure count

### When State is Saved

State is saved automatically in multiple scenarios:

1. **After Every Purchase** - Immediate save when buy order fills
2. **After Pending Buy Order Placed** - Immediate save to track pending order
3. **After Every Sell** - Immediate save when sell order fills
4. **Periodic Auto-Save** - Every 60 seconds (configurable)
5. **On Bot Stop** - Final state save when bot shuts down
6. **After Connectivity Issues** - Save after resetting trailing state

### State File Location

```
data/bot_state_{bot_id}.json
```

Example state file:
```json
{
  "bot_id": "abc123-def456",
  "name": "BTC-DCA-Bot",
  "symbol": "BTC/USD",
  "exchange": "binance_us",
  "strategy": "dca",
  "last_update": "2025-11-03T10:30:00Z",
  "stats": {
    "total_trades": 5,
    "winning_trades": 3,
    "losing_trades": 0,
    "total_profit": 125.50,
    "current_position": 0.0008,
    "last_price": 50500.00
  },
  "strategy_state": {
    "last_purchase_time": 1730635800,
    "last_purchase_price": 50000.00,
    "total_purchased": 0.0004,
    "total_spent": 20.00,
    "purchase_count": 1,
    "pending_sell_order": {
      "buy_order_id": "order_123",
      "buy_price": 50000.00,
      "buy_amount": 0.0004,
      "buy_cost": 20.00,
      "buy_timestamp": 1730635800,
      "target_sell_price": 50601.05,
      "profit_target": 1.0,
      "actual_profit": 1.0,
      "status": "pending"
    },
    "trailing_state": {
      "status": "active",
      "direction": "up",
      "activation_price": 50500.00,
      "watermark": 50800.00,
      "trailing_percent": 0.25,
      "last_update": 1730636000
    }
  },
  "connectivity": {
    "last_success": "2025-11-03T10:30:00Z",
    "failure_count": 0
  }
}
```

### State Restoration

On bot startup, the state is automatically restored:
- Strategy state is loaded from the saved file
- Pending sell orders are restored
- Trailing state is resumed (if still valid)
- Statistics are restored

---

## 🌐 Connectivity Monitoring

### How It Works

The bot monitors internet connectivity to avoid wasting cycles and detect network issues:

1. **Periodic Checks** - Every 2 minutes (configurable)
2. **Simple Ping** - Uses socket connection to Google DNS (8.8.8.8:53) - no API keys required
3. **Works for All Modes** - Paper trading and live trading both need internet for market data
4. **Failure Tracking** - Counts consecutive failures
5. **Exponential Backoff** - Waits longer between retries after failures

**Why Google DNS?**
- No authentication required (works for paper trading)
- Highly reliable (99.99% uptime)
- Fast response (< 100ms typically)
- Works worldwide

### Connectivity Check Flow

```
┌─────────────────────────────────────┐
│  Main Trading Loop                  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Check if 2 minutes passed          │
│  since last connectivity check      │
└──────────────┬──────────────────────┘
               │ Yes
               ▼
┌─────────────────────────────────────┐
│  Ping exchange (fetch_time)         │
└──────────────┬──────────────────────┘
               │
        ┌──────┴──────┐
        │             │
        ▼             ▼
    Success       Failure
        │             │
        │             ▼
        │    ┌────────────────────┐
        │    │ Increment failures │
        │    │ counter            │
        │    └────────┬───────────┘
        │             │
        │             ▼
        │    ┌────────────────────┐
        │    │ failures >= 2?     │
        │    └────────┬───────────┘
        │             │ Yes
        │             ▼
        │    ┌────────────────────┐
        │    │ Reset trailing     │
        │    │ state              │
        │    └────────┬───────────┘
        │             │
        │             ▼
        │    ┌────────────────────┐
        │    │ Wait with backoff  │
        │    │ (30s, 60s, 120s..) │
        │    └────────┬───────────┘
        │             │
        │             ▼
        │         Skip cycle
        │
        ▼
   Continue trading
```

### Configuration

```yaml
# Connectivity monitoring
connectivity_check_interval: 120  # Check every 2 minutes
max_connectivity_failures: 2      # Reset trailing after 2 failures
```

### Backoff Strategy

After connectivity failures, the bot uses exponential backoff:

| Failure # | Wait Time |
|-----------|-----------|
| 1         | 30s       |
| 2         | 60s       |
| 3         | 120s      |
| 4         | 240s      |
| 5+        | 300s (max)|

---

## 📋 Pending Order Tracking

### Pending Buy Orders

The bot tracks pending buy orders to prevent placing multiple simultaneous orders while waiting for trailing orders to fill.

**Problem Solved:**
When a trailing buy order is placed on the exchange, it has status `'open'` (not `'closed'`). Without tracking, the bot would see the same buy signal every iteration and place multiple orders.

**How It Works:**

1. **Order Placed** → `on_buy_order_placed()` called
   - Order ID added to `pending_buy_orders` list
   - State saved to disk

2. **Strategy Analysis** → Checks for pending orders
   - If `pending_buy_orders` is not empty, return 'hold' signal
   - Prevents new buy signals while waiting for fill

3. **Order Fills** → `on_order_filled()` called
   - Order ID removed from `pending_buy_orders` list
   - Purchase added to active purchases
   - Sell order placed immediately

4. **State Persistence**
   - Pending orders saved to state file
   - Restored on bot restart
   - Prevents duplicate orders after crashes

**Example Flow:**
```
Iteration #1: Buy signal detected → Place trailing order #12345
              → Add #12345 to pending_buy_orders
              → Save state

Iteration #2: Check pending_buy_orders → [#12345] exists
              → Return 'hold' signal (don't place another order)

Iteration #3: Check pending_buy_orders → [#12345] exists
              → Return 'hold' signal

Order #12345 fills → on_order_filled() called
                   → Remove #12345 from pending_buy_orders
                   → Add to purchases
                   → Place sell order

Iteration #4: Check pending_buy_orders → [] empty
              → Can place new order if signals align
```

### Pending Sell Orders

Sell orders are tracked differently - within each purchase object:

**Sell Order Status Values:**
- `'pending'` - Sell order not yet created (initial state)
- `'active'` - Sell order placed on exchange (limit or exchange-native trailing)
- `'pending_market'` - Market order waiting for price to reach target
- `'pending_trail'` - Bot-managed trailing order waiting for activation price
- `'trailing_active'` - Bot-managed trailing order actively tracking price
- `'filled'` - Sell order completed
- `'cancelled'` - Sell order cancelled
- `'error'` - Error placing sell order

**Purchase Object Structure:**
```python
purchase = {
    # Buy order info
    'buy_order': {
        'order_id': '12345',
        'price': 700.00,
        'amount': 0.01,
        'cost': 7.00,
        'fee': 0.007,
        'timestamp': 1700000000,
        'order_info': {...}  # Complete order details
    },

    # Sell order tracking
    'sell_order': {
        'status': 'active',  # Current status
        'type': 'trailing_market',
        'target_price': 707.00,
        'order_id': '12346',
        'client_order_id': 'abc123',
        'filled_price': None,
        'filled_timestamp': None,
        'filled_amount': None,
        'order_info': {...}  # Complete order details when placed
    },

    # Purchase metadata
    'cost': 7.00,
    'amount': 0.01,
    'sell_price': 707.00,
    'dca_applied': 0.0,
    'profit': None  # Set when sold
}
```

**Why Different Tracking?**
- **Buy Orders**: Only ONE pending buy order at a time (controls entry)
- **Sell Orders**: MULTIPLE sell orders active (one per open position)

---

## 🎯 Trailing State Management

### Exchange-Native Trailing (Binance/Binance.US)

For exchanges that support native trailing orders, the bot places orders directly on the exchange:

**Advantages:**
- Orders persist through bot crashes, power outages, internet issues
- Exchange manages trailing logic (more reliable)
- No need for bot to continuously monitor price

**Implementation:**
- Buy orders use `STOP_LOSS_LIMIT` type with `trailingDelta` parameter
- Sell orders use `TAKE_PROFIT_LIMIT` type with `trailingDelta` parameter
- Trailing distance specified in basis points (BIPS): 100 BIPS = 1%

### Bot-Managed Trailing

For exchanges that don't support native trailing orders, the bot can manage trailing locally:

### Trailing States

1. **inactive** - No trailing active
2. **waiting** - Waiting for price to reach activation price
3. **active** - Actively trailing price movements
4. **triggered** - Trailing condition met, ready to execute

### Trailing Up (for Sells)

```
Price reaches activation → Start tracking highest price (watermark)
Price goes higher → Update watermark
Price drops X% from watermark → Trigger sell
```

Example:
```
Activation: $50,000
Price hits $50,500 → Watermark = $50,500 (active)
Price hits $50,800 → Watermark = $50,800
Price drops to $50,600 → Drop = 0.39% (not enough)
Price drops to $50,550 → Drop = 0.49% (triggered at 0.5%)
```

### Trailing Down (for Buys)

```
Price reaches activation → Start tracking lowest price (watermark)
Price goes lower → Update watermark
Price rises X% from watermark → Trigger buy
```

### Trailing State Reset

Trailing state is automatically reset in these scenarios:

1. **After Connectivity Failures** - If 2+ consecutive failures
2. **After Order Fill** - When trailing order executes
3. **Manual Reset** - Via bot control commands

### Configuration

```yaml
# Trailing percentages
trailing_buy_percent: 0.25   # 0.25% for buys
trailing_sell_percent: 0.25  # 0.25% for sells
```

---

## ⚡ Smart Indicator Checks

### Optimization Strategy

To reduce API calls and CPU usage, the bot now uses smart indicator checking:

### When Indicators Are Checked

1. **Price Movement Threshold** - Only if price moved ≥0.5% from last purchase
2. **OHLCV Caching** - Reuse OHLCV data for 5 minutes
3. **Skip When Not Needed** - Don't check if no positions or far from buy zone

### OHLCV Data Caching

```python
# First call - fetches from exchange
df = strategy._get_ohlcv_data(market_data)  # API call

# Subsequent calls within 5 minutes - uses cache
df = strategy._get_ohlcv_data(market_data)  # No API call
```

### Configuration

```yaml
# Smart indicator checks
smart_indicator_checks: true      # Enable optimization
min_price_change_percent: 0.5     # Only check if price moved this much
indicator_cache_ttl: 300          # Cache OHLCV for 5 minutes
```

### Performance Impact

**Before optimization:**
- OHLCV fetch every cycle (60s) = 1,440 API calls/day
- Indicator calculations every cycle

**After optimization:**
- OHLCV fetch every 5 minutes = 288 API calls/day
- Indicator calculations only when price moves
- **80% reduction in API calls**

---

## 🔧 Configuration Reference

### Complete Configuration Example

```yaml
# State persistence
state_dir: data              # Directory for state files
auto_save: true              # Enable auto-save
save_interval: 60            # Auto-save every 60 seconds

# Connectivity monitoring
connectivity_check_interval: 120  # Check every 2 minutes
max_connectivity_failures: 2      # Reset trailing after 2 failures

# Smart indicator checks
smart_indicator_checks: true      # Enable optimization
min_price_change_percent: 0.5     # Only check if price moved 0.5%
indicator_cache_ttl: 300          # Cache OHLCV for 5 minutes

# Trailing orders
trailing_buy_percent: 0.25   # 0.25% trailing for buys
trailing_sell_percent: 0.25  # 0.25% trailing for sells
```

---

## 📊 Monitoring and Logs

### State Save Logs

```
[Bot-abc123] State saved to data/bot_state_abc123.json
[Bot-abc123] State saved after purchase
[Bot-abc123] State saved after sell
```

### Connectivity Logs

```
[Bot-abc123] ✓ Connectivity check passed
[Bot-abc123] ⚠️  Connectivity check failed (failure #1)
[Bot-abc123] Resetting trailing state due to 2 connectivity failures
[Bot-abc123] Waiting 30s before retry...
```

### Trailing Logs

```
[Bot-abc123] Trailing started: up from $50,000.00 with 0.25% trail
[Bot-abc123] Trailing activated at $50,500.00
[Bot-abc123] Trailing watermark updated: $50,800.00
[Bot-abc123] Trailing sell triggered! Price dropped 0.50% from $50,800.00 to $50,550.00
```

### Smart Check Logs

```
[Bot-abc123] Price change 0.3% < 0.5%, skipping indicator checks
[Bot-abc123] Using cached OHLCV data (age: 120s)
[Bot-abc123] OHLCV data cached
```

---

## 🚀 Benefits

### Reliability
- ✅ No data loss on crashes
- ✅ Automatic state recovery
- ✅ Resilient to network issues
- ✅ Trailing state preserved across restarts

### Performance
- ✅ 80% reduction in API calls
- ✅ Lower CPU usage
- ✅ Faster response times
- ✅ Better rate limit management

### Operational
- ✅ Automatic recovery from failures
- ✅ Clear logging and monitoring
- ✅ Configurable behavior
- ✅ Production-ready reliability

---

## 🔍 Troubleshooting

### State File Not Found

**Issue**: Bot starts with no previous state

**Solution**: This is normal for first run. State file is created after first purchase.

### Trailing State Reset

**Issue**: Trailing state keeps resetting

**Solution**: Check connectivity. If internet is unstable, increase `max_connectivity_failures`.

### Too Many API Calls

**Issue**: Hitting rate limits

**Solution**: 
- Enable `smart_indicator_checks: true`
- Increase `indicator_cache_ttl` to 600 (10 minutes)
- Increase `min_price_change_percent` to 1.0

### State File Corruption

**Issue**: Bot fails to load state

**Solution**: State files use atomic writes (temp file + rename). If corrupted, delete and restart.

---

## 📚 Related Documentation

- [Fees and Profit Calculation](FEES_AND_PROFIT_CALCULATION.md) - Trading fee integration
- [Strategy Enhancements](STRATEGY_ENHANCEMENTS.md) - Indicator configuration

---

**All critical reliability features are now implemented and production-ready!**

