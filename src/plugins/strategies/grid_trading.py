"""
Grid Trading Strategy with Indicator-Based Decisions

Places buy and sell orders at regular intervals (grid levels) above and below
the current price. When a buy order fills, it places a sell order above it.
When a sell order fills, it places a buy order below it.

Enhanced with technical indicators to avoid blind buying/selling at poor entry points.

This strategy profits from market volatility and range-bound trading.
"""

from typing import Dict, Any, List
from plugins.base.strategy_plugin import StrategyPlugin
from plugins.indicators import TechnicalIndicators
from utils.logger import get_logger

logger = get_logger(__name__)


class GridTradingStrategy(StrategyPlugin):
    """
    Enhanced grid trading strategy with indicator-based decisions.

    Uses technical indicators to validate buy/sell decisions at grid levels,
    avoiding blind execution in unfavorable market conditions.

    Parameters:
    - grid_spacing: Percentage spacing between grid levels (default: 2.5%)
    - grid_levels: Number of grid levels above and below current price (default: 10)
    - position_size: Position size in USD per grid level (default: 100)
    - use_indicators_for_buy: Use indicators to validate buy orders (default: True)
    - use_indicators_for_sell: Use indicators to validate sell orders (default: False)
    - use_rsi: Use RSI indicator for buys (default: True)
    - rsi_oversold: RSI oversold level for buys (default: 40)
    - rsi_overbought: RSI overbought level for sells (default: 65)
    - use_macd: Use MACD indicator (default: True)
    - use_ema: Use EMA indicator (default: False)
    - ema_length: EMA period (default: 25)
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize grid trading strategy.

        Args:
            config: Strategy configuration
        """
        super().__init__(config)

        # Strategy parameters
        self.grid_spacing = self.params.get('grid_spacing', 2.5)  # %
        self.grid_levels = self.params.get('grid_levels', 10)
        self.position_size = self.params.get('position_size', 100)  # USD

        # Indicator settings
        self.use_indicators_for_buy = self.params.get('use_indicators_for_buy', True)
        self.use_indicators_for_sell = self.params.get('use_indicators_for_sell', False)
        self.use_rsi = self.params.get('use_rsi', True)
        self.rsi_oversold = self.params.get('rsi_oversold', 40)
        self.rsi_overbought = self.params.get('rsi_overbought', 65)
        self.use_macd = self.params.get('use_macd', True)
        self.use_ema = self.params.get('use_ema', False)
        self.ema_length = self.params.get('ema_length', 25)

        # State
        self.grid_orders = []  # List of active grid orders
        self.current_price = None
        self.bot = None

        logger.info(f"Enhanced Grid Trading Strategy initialized:")
        logger.info(f"  Grid spacing: {self.grid_spacing}%")
        logger.info(f"  Grid levels: {self.grid_levels}")
        logger.info(f"  Position size: ${self.position_size}")
        logger.info(f"  Use indicators for buy: {self.use_indicators_for_buy}")
        logger.info(f"  Use indicators for sell: {self.use_indicators_for_sell}")
        if self.use_indicators_for_buy or self.use_indicators_for_sell:
            logger.info(f"  Indicators: RSI={self.use_rsi}, MACD={self.use_macd}, EMA={self.use_ema}")
    
    def initialize(self, bot_instance):
        """
        Initialize strategy with bot instance.
        
        Args:
            bot_instance: Reference to the bot engine
        """
        self.bot = bot_instance
        logger.info("Grid Trading Strategy ready")
    
    def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market and manage grid orders.
        
        Args:
            market_data: Current market data
            
        Returns:
            Signal dictionary
        """
        self.current_price = market_data.get('last')
        
        if not self.current_price:
            return {
                'action': 'hold',
                'confidence': 0.0,
                'reason': 'No price data available'
            }
        
        logger.info(f"Current price: ${self.current_price:,.2f}")
        
        # Check if we need to place grid orders
        if not self.grid_orders:
            logger.info("No active grid orders - placing initial grid")
            self._place_grid_orders()
            
            return {
                'action': 'hold',
                'confidence': 1.0,
                'reason': f'Placed {len(self.grid_orders)} grid orders',
                'metadata': {
                    'grid_orders': len(self.grid_orders)
                }
            }
        
        # Grid is active - just monitor
        logger.info(f"Grid active with {len(self.grid_orders)} orders")
        
        return {
            'action': 'hold',
            'confidence': 1.0,
            'reason': 'Grid orders active',
            'metadata': {
                'grid_orders': len(self.grid_orders),
                'current_price': self.current_price
            }
        }
    
    def _place_grid_orders(self):
        """
        Place grid orders above and below current price.
        """
        if not self.current_price:
            logger.error("Cannot place grid orders - no current price")
            return
        
        logger.info("=" * 60)
        logger.info("Placing Grid Orders")
        logger.info("=" * 60)
        
        # Calculate grid levels
        grid_levels = self._calculate_grid_levels()
        
        # Place orders at each level
        for level in grid_levels:
            price = level['price']
            side = level['side']
            
            # Calculate amount based on position size
            amount = self.position_size / price
            
            logger.info(f"  {side.upper()}: {amount:.8f} @ ${price:,.2f}")
            
            # Store order info (actual order placement would happen here)
            self.grid_orders.append({
                'price': price,
                'side': side,
                'amount': amount,
                'status': 'pending'
            })
        
        logger.info("=" * 60)
        logger.info(f"✓ Placed {len(self.grid_orders)} grid orders")
        logger.info("=" * 60)
    
    def _calculate_grid_levels(self) -> List[Dict[str, Any]]:
        """
        Calculate grid price levels.
        
        Returns:
            List of grid levels with price and side
        """
        levels = []
        
        # Buy levels (below current price)
        for i in range(1, self.grid_levels + 1):
            price = self.current_price * (1 - (self.grid_spacing / 100) * i)
            levels.append({
                'price': price,
                'side': 'buy'
            })
        
        # Sell levels (above current price)
        for i in range(1, self.grid_levels + 1):
            price = self.current_price * (1 + (self.grid_spacing / 100) * i)
            levels.append({
                'price': price,
                'side': 'sell'
            })
        
        return levels
    
    def on_order_filled(self, order: Dict[str, Any]):
        """
        Handle order fill event.

        When a buy order fills, place a sell order above it.
        When a sell order fills, place a buy order below it (with indicator validation).

        Args:
            order: Order details
        """
        logger.info("=" * 60)
        logger.info(f"Order Filled: {order.get('side')} @ ${order.get('price'):,.2f}")
        logger.info("=" * 60)

        # Remove filled order from grid
        self.grid_orders = [
            o for o in self.grid_orders
            if o.get('price') != order.get('price')
        ]

        # Place opposite order
        if order.get('side') == 'buy':
            # Buy filled - place sell order above
            sell_price = order.get('price') * (1 + self.grid_spacing / 100)

            # Check indicators for sell if enabled
            if self.use_indicators_for_sell and not self._validate_sell_indicators():
                logger.info(f"Sell indicators not favorable - skipping sell order @ ${sell_price:,.2f}")
                logger.info("=" * 60)
                return

            logger.info(f"Placing SELL order @ ${sell_price:,.2f}")

            self.grid_orders.append({
                'price': sell_price,
                'side': 'sell',
                'amount': order.get('amount'),
                'status': 'pending'
            })
        else:
            # Sell filled - place buy order below
            buy_price = order.get('price') * (1 - self.grid_spacing / 100)

            # Check indicators for buy if enabled
            if self.use_indicators_for_buy and not self._validate_buy_indicators():
                logger.info(f"Buy indicators not favorable - skipping buy order @ ${buy_price:,.2f}")
                logger.info("=" * 60)
                return

            logger.info(f"Placing BUY order @ ${buy_price:,.2f}")

            self.grid_orders.append({
                'price': buy_price,
                'side': 'buy',
                'amount': order.get('amount'),
                'status': 'pending'
            })

        logger.info("=" * 60)
    
    def on_order_cancelled(self, order: Dict[str, Any]):
        """
        Handle order cancellation.
        
        Args:
            order: Order details
        """
        logger.warning(f"Order cancelled: {order.get('side')} @ ${order.get('price'):,.2f}")
        
        # Remove from grid
        self.grid_orders = [
            o for o in self.grid_orders 
            if o.get('price') != order.get('price')
        ]
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get current strategy state.
        
        Returns:
            State dictionary
        """
        return {
            'grid_orders': self.grid_orders,
            'current_price': self.current_price
        }
    
    def restore_state(self, state: Dict[str, Any]):
        """
        Restore strategy state.

        Args:
            state: Saved state dictionary
        """
        self.grid_orders = state.get('grid_orders', [])
        self.current_price = state.get('current_price')

        logger.info(f"State restored: {len(self.grid_orders)} grid orders")

    def _validate_buy_indicators(self) -> bool:
        """
        Validate if indicators support buying.

        Returns:
            True if indicators are favorable for buying
        """
        if not self.bot or not hasattr(self.bot, 'get_market_data'):
            logger.warning("Cannot validate indicators - no market data available")
            return True  # Default to allowing the trade

        try:
            market_data = self.bot.get_market_data()
            df = market_data.get('ohlcv')

            if df is None or len(df) < 50:
                logger.warning("Insufficient OHLCV data for indicator validation")
                return True  # Default to allowing the trade

            signals = []

            # RSI oversold check
            if self.use_rsi:
                rsi, _ = TechnicalIndicators.get_rsi(df)
                if rsi <= self.rsi_oversold:
                    signals.append(True)
                    logger.info(f"  ✓ RSI oversold: {rsi:.1f}")
                else:
                    signals.append(False)
                    logger.info(f"  ✗ RSI not oversold: {rsi:.1f}")

            # MACD rising check
            if self.use_macd:
                if TechnicalIndicators.is_macd_rising(df):
                    signals.append(True)
                    logger.info(f"  ✓ MACD rising")
                else:
                    signals.append(False)
                    logger.info(f"  ✗ MACD not rising")

            # Price below EMA check
            if self.use_ema:
                if TechnicalIndicators.is_price_below_ema(df, length=self.ema_length):
                    signals.append(True)
                    logger.info(f"  ✓ Price below EMA")
                else:
                    signals.append(False)
                    logger.info(f"  ✗ Price above EMA")

            # Need at least 50% of indicators to agree
            if not signals:
                return True  # No indicators enabled

            positive = sum(signals)
            total = len(signals)

            return positive >= (total * 0.5)

        except Exception as e:
            logger.error(f"Error validating buy indicators: {e}")
            return True  # Default to allowing the trade on error

    def _validate_sell_indicators(self) -> bool:
        """
        Validate if indicators support selling.

        Returns:
            True if indicators are favorable for selling
        """
        if not self.bot or not hasattr(self.bot, 'get_market_data'):
            logger.warning("Cannot validate indicators - no market data available")
            return True  # Default to allowing the trade

        try:
            market_data = self.bot.get_market_data()
            df = market_data.get('ohlcv')

            if df is None or len(df) < 50:
                logger.warning("Insufficient OHLCV data for indicator validation")
                return True  # Default to allowing the trade

            signals = []

            # RSI overbought check
            if self.use_rsi:
                rsi, _ = TechnicalIndicators.get_rsi(df)
                if rsi >= self.rsi_overbought:
                    signals.append(True)
                    logger.info(f"  ✓ RSI overbought: {rsi:.1f}")
                else:
                    signals.append(False)
                    logger.info(f"  ✗ RSI not overbought: {rsi:.1f}")

            # MACD falling check (negative for sell)
            if self.use_macd:
                if not TechnicalIndicators.is_macd_rising(df):
                    signals.append(True)
                    logger.info(f"  ✓ MACD falling")
                else:
                    signals.append(False)
                    logger.info(f"  ✗ MACD still rising")

            # Need at least 50% of indicators to agree
            if not signals:
                return True  # No indicators enabled

            positive = sum(signals)
            total = len(signals)

            return positive >= (total * 0.5)

        except Exception as e:
            logger.error(f"Error validating sell indicators: {e}")
            return True  # Default to allowing the trade on error

