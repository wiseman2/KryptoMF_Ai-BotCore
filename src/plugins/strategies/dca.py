"""
DCA (Dollar Cost Averaging) Strategy

Enhanced DCA strategy that uses indicator-based decisions instead of time-based intervals.
Takes advantage of dropping prices and oversold conditions to make smarter purchases.

This strategy reduces the impact of volatility by averaging the purchase price over time,
while also using technical indicators to avoid buying at poor entry points.

Good for long-term accumulation with better entry timing.
"""

import time
from typing import Dict, Any
from plugins.base.strategy_plugin import StrategyPlugin
from plugins.indicators import TechnicalIndicators
from utils.logger import get_logger

logger = get_logger(__name__)


class DCAStrategy(StrategyPlugin):
    """
    Enhanced Dollar Cost Averaging (DCA) strategy with indicator-based decisions.

    Uses technical indicators and price action instead of time-based intervals.
    Takes advantage of dropping prices and oversold conditions.

    Parameters:
    - amount_usd: Amount to purchase each time (default: 100)
    - max_price: Maximum price to buy at (optional)
    - min_price: Minimum price to buy at (optional)
    - min_interval_hours: Minimum hours between purchases to avoid overtrading (default: 1)
    - price_drop_percent: Minimum price drop to consider buying (default: 1.0)
    - use_rsi: Use RSI indicator (default: True)
    - rsi_oversold: RSI oversold level (default: 35)
    - use_stoch_rsi: Use Stochastic RSI (default: False)
    - stoch_oversold: Stochastic oversold level (default: 33)
    - use_ema: Use EMA indicator (default: True)
    - ema_length: EMA period (default: 25)
    - use_macd: Use MACD indicator (default: False)
    - use_mfi: Use MFI indicator (default: False)
    - mfi_oversold: MFI oversold level (default: 25)
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize DCA strategy.

        Args:
            config: Strategy configuration
        """
        super().__init__(config)

        # Strategy parameters
        self.amount_usd = self.params.get('amount_usd', 100)
        self.max_price = self.params.get('max_price', None)
        self.min_price = self.params.get('min_price', None)
        self.min_interval_hours = self.params.get('min_interval_hours', 1)
        self.price_drop_percent = self.params.get('price_drop_percent', 1.0)

        # Trading fees (from config)
        fees = config.get('fees', {})
        self.maker_fee = fees.get('maker', 0.1)  # Default 0.1%
        self.taker_fee = fees.get('taker', 0.1)  # Default 0.1%

        # Profit target (from config)
        self.profit_target = config.get('profit_target', 1.0)  # Default 1.0%

        # Indicator settings from config
        indicators_config = self.params.get('indicators', {})

        # RSI configuration
        rsi_config = indicators_config.get('rsi', {})
        self.use_rsi = rsi_config.get('enabled', True)
        self.rsi_period = rsi_config.get('period', 14)
        self.rsi_oversold = rsi_config.get('oversold', 30)
        self.rsi_overbought = rsi_config.get('overbought', 70)
        self.check_rsi_rising = rsi_config.get('check_rising', True)  # New: check if RSI is rising

        # Stochastic RSI configuration
        stoch_config = indicators_config.get('stoch_rsi', {})
        self.use_stoch_rsi = stoch_config.get('enabled', False)
        self.stoch_period = stoch_config.get('period', 14)
        self.stoch_oversold = stoch_config.get('oversold', 20)
        self.stoch_overbought = stoch_config.get('overbought', 80)

        # EMA configuration
        ema_config = indicators_config.get('ema', {})
        self.use_ema = ema_config.get('enabled', True)
        self.ema_short = ema_config.get('short_period', 12)
        self.ema_long = ema_config.get('long_period', 26)

        # MACD configuration
        macd_config = indicators_config.get('macd', {})
        self.use_macd = macd_config.get('enabled', False)
        self.macd_fast = macd_config.get('fast_period', 12)
        self.macd_slow = macd_config.get('slow_period', 26)
        self.macd_signal = macd_config.get('signal_period', 9)

        # MFI configuration
        mfi_config = indicators_config.get('mfi', {})
        self.use_mfi = mfi_config.get('enabled', False)
        self.mfi_period = mfi_config.get('period', 14)
        self.mfi_oversold = mfi_config.get('oversold', 20)
        self.mfi_overbought = mfi_config.get('overbought', 80)

        # State
        self.last_purchase_time = None
        self.last_purchase_price = None
        self.total_purchased = 0.0
        self.total_spent = 0.0
        self.purchase_count = 0
        self.bot = None

        logger.info(f"Enhanced DCA Strategy initialized:")
        logger.info(f"  Amount: ${self.amount_usd} per purchase")
        logger.info(f"  Trading fees: {self.maker_fee}% maker, {self.taker_fee}% taker")
        logger.info(f"  Profit target: {self.profit_target}% (after fees)")
        logger.info(f"  Min interval: {self.min_interval_hours} hours")
        logger.info(f"  Price drop trigger: {self.price_drop_percent}%")
        if self.max_price:
            logger.info(f"  Max price: ${self.max_price:,.2f}")
        if self.min_price:
            logger.info(f"  Min price: ${self.min_price:,.2f}")
        logger.info(f"  Indicators: RSI={self.use_rsi}, StochRSI={self.use_stoch_rsi}, "
                   f"EMA={self.use_ema}, MACD={self.use_macd}, MFI={self.use_mfi}")
        if self.use_rsi and self.check_rsi_rising:
            logger.info(f"  RSI rising check: enabled")
    
    def initialize(self, bot_instance):
        """
        Initialize strategy with bot instance.
        
        Args:
            bot_instance: Reference to the bot engine
        """
        self.bot = bot_instance
        logger.info("DCA Strategy ready")
    
    def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market and determine if it's time to buy using indicators.

        Args:
            market_data: Current market data including OHLCV DataFrame

        Returns:
            Signal dictionary
        """
        current_price = market_data.get('last')
        df = market_data.get('ohlcv')  # Pandas DataFrame with OHLCV data
        current_time = time.time()

        if not current_price or df is None or len(df) < 50:
            return {
                'action': 'hold',
                'confidence': 0.0,
                'reason': 'Insufficient market data'
            }

        logger.info(f"Current price: ${current_price:,.2f}")

        # Check minimum interval to avoid overtrading
        if self.last_purchase_time:
            time_since_last = (current_time - self.last_purchase_time) / 3600  # hours
            logger.info(f"Time since last purchase: {time_since_last:.1f} hours")

            if time_since_last < self.min_interval_hours:
                hours_remaining = self.min_interval_hours - time_since_last
                return {
                    'action': 'hold',
                    'confidence': 1.0,
                    'reason': f'Min interval not met ({hours_remaining:.1f}h remaining)',
                    'metadata': {
                        'hours_remaining': hours_remaining,
                        'current_price': current_price
                    }
                }

        # Check price limits
        if self.max_price and current_price > self.max_price:
            return {
                'action': 'hold',
                'confidence': 1.0,
                'reason': f'Price ${current_price:,.2f} above max ${self.max_price:,.2f}',
                'metadata': {
                    'current_price': current_price,
                    'max_price': self.max_price
                }
            }

        if self.min_price and current_price < self.min_price:
            return {
                'action': 'hold',
                'confidence': 1.0,
                'reason': f'Price ${current_price:,.2f} below min ${self.min_price:,.2f}',
                'metadata': {
                    'current_price': current_price,
                    'min_price': self.min_price
                }
            }

        # Evaluate indicators for buy signal
        buy_signals = []
        reasons = []

        # Check price drop (required)
        if TechnicalIndicators.has_price_dropped(df, lookback=24, drop_percent=self.price_drop_percent):
            buy_signals.append(True)
            reasons.append(f"Price dropped {self.price_drop_percent}%")
        else:
            # If price hasn't dropped, don't buy
            return {
                'action': 'hold',
                'confidence': 1.0,
                'reason': f'Price has not dropped {self.price_drop_percent}%',
                'metadata': {'current_price': current_price}
            }

        # RSI oversold and rising check
        if self.use_rsi:
            rsi, rising = TechnicalIndicators.get_rsi(df, period=self.rsi_period)
            is_oversold = rsi <= self.rsi_oversold

            # Check if RSI is rising (indicates momentum building)
            if self.check_rsi_rising:
                is_rising_trend = TechnicalIndicators.is_rsi_rising(df, period=self.rsi_period, lookback=3)

                if is_oversold and not is_rising_trend:
                    # RSI is oversold but still falling - wait for reversal
                    buy_signals.append(False)
                    reasons.append(f"RSI oversold ({rsi:.1f}) but still falling - waiting for reversal")
                elif is_oversold and is_rising_trend:
                    # RSI is oversold AND rising - good buy signal
                    buy_signals.append(True)
                    reasons.append(f"RSI oversold ({rsi:.1f}) and rising ✓")
                else:
                    buy_signals.append(False)
            else:
                # Just check oversold without rising check
                if is_oversold:
                    buy_signals.append(True)
                    reasons.append(f"RSI oversold ({rsi:.1f})")
                else:
                    buy_signals.append(False)

        # Stochastic RSI oversold
        if self.use_stoch_rsi:
            if TechnicalIndicators.is_stoch_oversold(df, period=self.stoch_period, oversold_level=self.stoch_oversold):
                buy_signals.append(True)
                stoch = TechnicalIndicators.get_stoch_rsi(df, period=self.stoch_period)
                reasons.append(f"Stoch RSI oversold ({stoch:.1f})")
            else:
                buy_signals.append(False)

        # Price below EMA (using short EMA)
        if self.use_ema:
            if TechnicalIndicators.is_price_below_ema(df, length=self.ema_short):
                buy_signals.append(True)
                ema = TechnicalIndicators.get_ema(df, length=self.ema_short)
                reasons.append(f"Price below EMA-{self.ema_short} ({ema:.2f})")
            else:
                buy_signals.append(False)

        # MACD rising
        if self.use_macd:
            if TechnicalIndicators.is_macd_rising(df, fast=self.macd_fast, slow=self.macd_slow, signal=self.macd_signal):
                buy_signals.append(True)
                reasons.append("MACD rising")
            else:
                buy_signals.append(False)

        # MFI oversold
        if self.use_mfi:
            if TechnicalIndicators.is_mfi_oversold(df, period=self.mfi_period, oversold_level=self.mfi_oversold):
                buy_signals.append(True)
                mfi = TechnicalIndicators.get_mfi(df, period=self.mfi_period)
                reasons.append(f"MFI oversold ({mfi:.1f})")
            else:
                buy_signals.append(False)

        # Determine if we should buy (at least 50% of indicators must agree)
        positive_signals = sum(buy_signals)
        total_signals = len(buy_signals)

        if positive_signals >= max(1, total_signals * 0.5):  # At least 50% agreement
            amount = self.amount_usd / current_price

            logger.info("=" * 60)
            logger.info("ENHANCED DCA BUY SIGNAL")
            logger.info("=" * 60)
            logger.info(f"  Price: ${current_price:,.2f}")
            logger.info(f"  Amount: {amount:.8f}")
            logger.info(f"  Cost: ${self.amount_usd:,.2f}")
            logger.info(f"  Signals: {positive_signals}/{total_signals}")
            logger.info(f"  Reasons: {', '.join(reasons)}")
            logger.info("=" * 60)

            return {
                'action': 'buy',
                'confidence': positive_signals / total_signals if total_signals > 0 else 1.0,
                'reason': f'Indicators triggered: {", ".join(reasons)}',
                'metadata': {
                    'price': current_price,
                    'amount': amount,
                    'cost': self.amount_usd,
                    'signals': positive_signals,
                    'total_signals': total_signals
                }
            }

        return {
            'action': 'hold',
            'confidence': 1.0,
            'reason': f'Indicators not aligned ({positive_signals}/{total_signals})',
            'metadata': {
                'current_price': current_price,
                'signals': positive_signals,
                'total_signals': total_signals
            }
        }
    
    def on_order_filled(self, order: Dict[str, Any]):
        """
        Handle order fill event.

        Args:
            order: Order details
        """
        if order.get('side') != 'buy':
            return

        # Update state
        self.last_purchase_time = time.time()
        self.last_purchase_price = order.get('price', 0)
        self.purchase_count += 1
        self.total_purchased += order.get('filled', 0)
        self.total_spent += order.get('cost', 0)

        avg_price = self.total_spent / self.total_purchased if self.total_purchased > 0 else 0

        # Calculate sell price with fees and profit target
        sell_price = TechnicalIndicators.calculate_sell_price_with_fees(
            buy_price=self.last_purchase_price,
            buy_fee_percent=self.maker_fee,
            sell_fee_percent=self.taker_fee,
            profit_target_percent=self.profit_target
        )

        # Calculate what the actual profit will be at that sell price
        actual_profit = TechnicalIndicators.calculate_actual_profit_percent(
            buy_price=self.last_purchase_price,
            sell_price=sell_price,
            buy_fee_percent=self.maker_fee,
            sell_fee_percent=self.taker_fee
        )

        logger.info("=" * 60)
        logger.info("DCA Purchase Complete")
        logger.info("=" * 60)
        logger.info(f"  Purchase #{self.purchase_count}")
        logger.info(f"  Buy Price: ${order.get('price'):,.2f}")
        logger.info(f"  Amount: {order.get('filled'):.8f}")
        logger.info(f"  Cost: ${order.get('cost'):,.2f}")
        logger.info(f"  Buy Fee: {self.maker_fee}%")
        logger.info("")
        logger.info(f"  Target Sell Price: ${sell_price:,.2f}")
        logger.info(f"  Profit Target: {self.profit_target}% (after fees)")
        logger.info(f"  Actual Profit: {actual_profit:.2f}%")
        logger.info(f"  Sell Fee: {self.taker_fee}%")
        logger.info("")
        logger.info(f"  Total purchased: {self.total_purchased:.8f}")
        logger.info(f"  Total spent: ${self.total_spent:,.2f}")
        logger.info(f"  Average price: ${avg_price:,.2f}")
        logger.info("=" * 60)
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get current strategy state.

        Returns:
            State dictionary
        """
        return {
            'last_purchase_time': self.last_purchase_time,
            'last_purchase_price': self.last_purchase_price,
            'total_purchased': self.total_purchased,
            'total_spent': self.total_spent,
            'purchase_count': self.purchase_count
        }

    def restore_state(self, state: Dict[str, Any]):
        """
        Restore strategy state.

        Args:
            state: Saved state dictionary
        """
        self.last_purchase_time = state.get('last_purchase_time')
        self.last_purchase_price = state.get('last_purchase_price')
        self.total_purchased = state.get('total_purchased', 0.0)
        self.total_spent = state.get('total_spent', 0.0)
        self.purchase_count = state.get('purchase_count', 0)

        logger.info(f"State restored: {self.purchase_count} purchases, "
                   f"{self.total_purchased:.8f} total")

    def get_sell_price(self) -> float:
        """
        Get the target sell price for current position.

        Returns:
            Target sell price accounting for fees and profit target
        """
        if not self.last_purchase_price:
            return 0.0

        return TechnicalIndicators.calculate_sell_price_with_fees(
            buy_price=self.last_purchase_price,
            buy_fee_percent=self.maker_fee,
            sell_fee_percent=self.taker_fee,
            profit_target_percent=self.profit_target
        )

