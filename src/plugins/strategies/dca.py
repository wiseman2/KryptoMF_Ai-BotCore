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

        # Indicator settings
        self.use_rsi = self.params.get('use_rsi', True)
        self.rsi_oversold = self.params.get('rsi_oversold', 35)
        self.use_stoch_rsi = self.params.get('use_stoch_rsi', False)
        self.stoch_oversold = self.params.get('stoch_oversold', 33)
        self.use_ema = self.params.get('use_ema', True)
        self.ema_length = self.params.get('ema_length', 25)
        self.use_macd = self.params.get('use_macd', False)
        self.use_mfi = self.params.get('use_mfi', False)
        self.mfi_oversold = self.params.get('mfi_oversold', 25)

        # State
        self.last_purchase_time = None
        self.total_purchased = 0.0
        self.total_spent = 0.0
        self.purchase_count = 0
        self.bot = None

        logger.info(f"Enhanced DCA Strategy initialized:")
        logger.info(f"  Amount: ${self.amount_usd} per purchase")
        logger.info(f"  Min interval: {self.min_interval_hours} hours")
        logger.info(f"  Price drop trigger: {self.price_drop_percent}%")
        if self.max_price:
            logger.info(f"  Max price: ${self.max_price:,.2f}")
        if self.min_price:
            logger.info(f"  Min price: ${self.min_price:,.2f}")
        logger.info(f"  Indicators: RSI={self.use_rsi}, StochRSI={self.use_stoch_rsi}, "
                   f"EMA={self.use_ema}, MACD={self.use_macd}, MFI={self.use_mfi}")
    
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

        # RSI oversold
        if self.use_rsi:
            rsi, rising = TechnicalIndicators.get_rsi(df, period=14)
            if rsi <= self.rsi_oversold:
                buy_signals.append(True)
                reasons.append(f"RSI oversold ({rsi:.1f})")
            else:
                buy_signals.append(False)

        # Stochastic RSI oversold
        if self.use_stoch_rsi:
            if TechnicalIndicators.is_stoch_oversold(df, oversold_level=self.stoch_oversold):
                buy_signals.append(True)
                stoch = TechnicalIndicators.get_stoch_rsi(df)
                reasons.append(f"Stoch RSI oversold ({stoch:.1f})")
            else:
                buy_signals.append(False)

        # Price below EMA
        if self.use_ema:
            if TechnicalIndicators.is_price_below_ema(df, length=self.ema_length):
                buy_signals.append(True)
                ema = TechnicalIndicators.get_ema(df, length=self.ema_length)
                reasons.append(f"Price below EMA ({ema:.2f})")
            else:
                buy_signals.append(False)

        # MACD rising
        if self.use_macd:
            if TechnicalIndicators.is_macd_rising(df):
                buy_signals.append(True)
                reasons.append("MACD rising")
            else:
                buy_signals.append(False)

        # MFI oversold
        if self.use_mfi:
            if TechnicalIndicators.is_mfi_oversold(df, oversold_level=self.mfi_oversold):
                buy_signals.append(True)
                mfi = TechnicalIndicators.get_mfi(df)
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
        self.purchase_count += 1
        self.total_purchased += order.get('filled', 0)
        self.total_spent += order.get('cost', 0)
        
        avg_price = self.total_spent / self.total_purchased if self.total_purchased > 0 else 0
        
        logger.info("=" * 60)
        logger.info("DCA Purchase Complete")
        logger.info("=" * 60)
        logger.info(f"  Purchase #{self.purchase_count}")
        logger.info(f"  Price: ${order.get('price'):,.2f}")
        logger.info(f"  Amount: {order.get('filled'):.8f}")
        logger.info(f"  Cost: ${order.get('cost'):,.2f}")
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
        self.total_purchased = state.get('total_purchased', 0.0)
        self.total_spent = state.get('total_spent', 0.0)
        self.purchase_count = state.get('purchase_count', 0)
        
        logger.info(f"State restored: {self.purchase_count} purchases, "
                   f"{self.total_purchased:.8f} total")

