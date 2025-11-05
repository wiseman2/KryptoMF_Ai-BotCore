"""
Advanced DCA (Dollar Cost Averaging) Strategy with Profit Application

This strategy implements an advanced DCA approach where profit from selling
a subsequent purchase is applied to reduce the cost basis of previous purchases.

Example:
- Buy #1: 1 BTC @ $50,000 (cost: $50,000)
- Buy #2: 1 BTC @ $48,000 (cost: $48,000)
- Sell #2: 1 BTC @ $49,000 (revenue: $49,000, profit: $1,000)
- After minimum profit (0.5% = $240), remaining profit ($760) is applied to Buy #1
- Buy #1 new cost: $50,000 - $760 = $49,240
- Buy #1 new sell price: $49,240 * 1.01 = $49,732 (instead of $50,500)

This makes it easier to sell the first purchase at a profit.
"""

import time
from typing import Dict, Any, List
from plugins.base.strategy_plugin import StrategyPlugin
from plugins.indicators import TechnicalIndicators
from utils.logger import get_logger

logger = get_logger(__name__)


class AdvancedDCAStrategy(StrategyPlugin):
    """
    Advanced DCA strategy with profit application to previous purchases.
    
    Features:
    - Indicator-based buy decisions (not time-based)
    - Profit from sales applied to reduce cost of previous purchases
    - Configurable indicators and thresholds
    - Takes advantage of dropping prices
    
    Parameters:
    - amount_usd: Amount to purchase each time (default: 100)
    - min_profit_percent: Minimum profit percentage before applying DCA (default: 0.5)
    - dca_pool_percent: Percentage of excess profit to apply to previous purchase (default: 100)
    - max_purchases: Maximum number of active purchases (default: -1 for unlimited)
    - price_drop_percent: Minimum price drop to trigger buy (default: 1.0)
    - use_rsi: Use RSI indicator (default: True)
    - rsi_oversold: RSI oversold level (default: 35)
    - use_stoch_rsi: Use Stochastic RSI (default: True)
    - stoch_oversold: Stochastic oversold level (default: 33)
    - use_ema: Use EMA indicator (default: True)
    - ema_length: EMA period (default: 25)
    - use_macd: Use MACD indicator (default: True)
    - use_mfi: Use MFI indicator (default: True)
    - mfi_oversold: MFI oversold level (default: 25)
    - step_down_multiplier: Multiplier for each additional purchase (default: 1.5)
    - max_step_down: Maximum step-down percentage per purchase (default: 5.0)

    Note: Base step-down is automatically set to min(profit_target, 5%)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Advanced DCA strategy.
        
        Args:
            config: Strategy configuration
        """
        super().__init__(config)
        
        # Strategy parameters
        self.amount_usd = self.params.get('amount_usd', 100)
        self.min_profit_percent = self.params.get('min_profit_percent', 0.5) / 100  # Convert to decimal
        self.dca_pool_percent = self.params.get('dca_pool_percent', 100) / 100  # Convert to decimal
        self.max_purchases = self.params.get('max_purchases', -1)  # -1 = unlimited (default)

        # Price drop configuration (OPTIONAL - disabled by default)
        price_drop_config = self.params.get('price_drop', {})
        if isinstance(price_drop_config, dict):
            self.use_price_drop = price_drop_config.get('enabled', False)
            self.price_drop_percent = price_drop_config.get('percent', 1.0)
            self.price_drop_lookback = price_drop_config.get('lookback_candles', 24)
        else:
            # Legacy support: if price_drop_percent is set directly
            self.price_drop_percent = self.params.get('price_drop_percent', None)
            self.use_price_drop = self.price_drop_percent is not None
            self.price_drop_lookback = 24  # Default lookback

        # Indicator settings
        self.use_rsi = self.params.get('use_rsi', True)
        self.rsi_oversold = self.params.get('rsi_oversold', 35)
        self.use_stoch_rsi = self.params.get('use_stoch_rsi', True)
        self.stoch_oversold = self.params.get('stoch_oversold', 33)
        self.use_ema = self.params.get('use_ema', True)
        self.ema_length = self.params.get('ema_length', 25)
        self.use_macd = self.params.get('use_macd', True)
        self.use_mfi = self.params.get('use_mfi', True)
        self.mfi_oversold = self.params.get('mfi_oversold', 25)

        # Progressive step-down settings (based on profit target)
        # Base step-down is the smaller of profit target or 5%
        self.base_step_down = min(self.min_profit_percent * 100, 5.0)
        self.step_down_multiplier = self.params.get('step_down_multiplier', 1.5)
        self.max_step_down = self.params.get('max_step_down', 5.0)

        # Indicator agreement threshold (percentage of indicators that must agree)
        self.indicator_agreement = self.params.get('indicator_agreement', 0.6)  # Default 60%

        # State - list of active purchases
        self.purchases = []  # List of purchase dicts with cost, amount, sell_price, dca_applied
        self.total_profit = 0.0
        self.total_dca_applied = 0.0
        self.bot = None

        # Backtest mode flag (reduces logging noise)
        self.is_backtest = False

        # Trailing state (for bot-managed trailing orders)
        self.trailing_state = {
            'status': 'inactive',  # inactive, waiting, active, triggered
            'direction': None,  # 'up' for sell trailing, 'down' for buy trailing
            'activation_price': None,  # Price to start trailing
            'watermark': None,  # Highest (sell) or lowest (buy) price seen while trailing
            'trailing_percent': None,  # Trailing percentage
            'last_update': None  # Last time watermark was updated
        }
        
        logger.info(f"Advanced DCA Strategy initialized:")
        logger.info(f"  Amount per purchase: ${self.amount_usd}")
        logger.info(f"  Min profit: {self.min_profit_percent * 100}%")
        logger.info(f"  DCA pool: {self.dca_pool_percent * 100}% of excess profit")
        logger.info(f"  Max purchases: {'Unlimited' if self.max_purchases == -1 else self.max_purchases}")
        logger.info(f"  Progressive step-down: Base={self.base_step_down}%, Multiplier={self.step_down_multiplier}x, Max={self.max_step_down}%")
        logger.info(f"  Price drop trigger: {'Disabled' if not self.use_price_drop else f'{self.price_drop_percent}% in {self.price_drop_lookback} candles'}")
        logger.info(f"  Indicators: RSI={self.use_rsi}, StochRSI={self.use_stoch_rsi}, "
                   f"EMA={self.use_ema}, MACD={self.use_macd}, MFI={self.use_mfi}")
    
    def initialize(self, bot_instance):
        """
        Initialize strategy with bot instance.
        
        Args:
            bot_instance: Reference to the bot engine
        """
        self.bot = bot_instance
        logger.info("Advanced DCA Strategy ready")
    
    def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market and determine if it's time to buy or sell.

        SELL LOGIC: Simple profit-based - sell when purchase reaches target price (no indicators)
        BUY LOGIC: Indicator-based decisions (RSI, MACD, MFI, etc.)

        Args:
            market_data: Current market data including OHLCV DataFrame

        Returns:
            Signal dictionary
        """
        current_price = market_data.get('last')
        df = market_data.get('ohlcv')  # Pandas DataFrame with OHLCV data

        if not current_price or df is None or len(df) < 50:
            return {
                'action': 'hold',
                'confidence': 0.0,
                'reason': 'Insufficient market data'
            }

        # Only log in live/paper trading, not backtest
        if not self.is_backtest:
            logger.info(f"Current price: ${current_price:,.2f}")
            logger.info(f"Active purchases: {len(self.purchases)}")

        # PRIORITY 1: Check if any purchases are ready to sell (profit target reached)
        # Sell logic is simple - no indicators, just price-based
        for purchase in self.purchases:
            sell_price = purchase.get('sell_price', 0)
            if current_price >= sell_price:
                amount = purchase.get('amount', 0)

                if not self.is_backtest:
                    logger.info("=" * 60)
                    logger.info("ADVANCED DCA SELL SIGNAL")
                    logger.info("=" * 60)
                    logger.info(f"  Current price: ${current_price:,.2f}")
                    logger.info(f"  Sell price: ${sell_price:,.2f}")
                    logger.info(f"  Amount: {amount:.8f}")
                    logger.info(f"  Revenue: ${current_price * amount:,.2f}")
                    logger.info("=" * 60)

                return {
                    'action': 'sell',
                    'confidence': 1.0,
                    'reason': f'Purchase reached profit target (${sell_price:,.2f})',
                    'metadata': {
                        'price': current_price,
                        'amount': amount,
                        'cost': purchase.get('cost', 0),
                        'purchase': purchase
                    }
                }

        # PRIORITY 2: Evaluate indicators for BUY signal
        buy_signals = []
        reasons = []

        # Check price drop (OPTIONAL - only if enabled)
        if self.use_price_drop:
            if TechnicalIndicators.has_price_dropped(df, lookback=self.price_drop_lookback, drop_percent=self.price_drop_percent):
                buy_signals.append(True)
                reasons.append(f"Price dropped {self.price_drop_percent}%")
            else:
                buy_signals.append(False)
        
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
        
        # Check if price is low enough compared to last purchase (progressive step-down)
        if len(self.purchases) > 0:
            last_purchase_price = self.purchases[-1]['price']

            # Calculate required step-down for this purchase
            # Each purchase requires progressively larger drop
            purchase_number = len(self.purchases) + 1  # Next purchase number
            required_step = self.base_step_down * (self.step_down_multiplier ** (purchase_number - 2))
            required_step = min(required_step, self.max_step_down)  # Cap at max

            price_drop_from_last = ((last_purchase_price - current_price) / last_purchase_price) * 100

            if price_drop_from_last < required_step:
                if not self.is_backtest:
                    logger.info(f"Price not low enough: {price_drop_from_last:.2f}% drop (need {required_step:.2f}%)")
                return {
                    'action': 'hold',
                    'confidence': 0.0,
                    'reason': f'Price needs to drop {required_step:.2f}% from last purchase (currently {price_drop_from_last:.2f}%)'
                }

        # Determine if we should buy (majority of indicators agree)
        positive_signals = sum(buy_signals)
        # print(f"Positive signals: {positive_signals}")
        total_signals = len(buy_signals)
        # print(f"Total signals: {total_signals}... percentage = {positive_signals / total_signals}")

        if positive_signals >= (total_signals * self.indicator_agreement):
            amount = self.amount_usd / current_price


            # Only show detailed logging in live/paper trading, not backtest
            if not self.is_backtest:
                logger.info("=" * 60)
                logger.info("ADVANCED DCA BUY SIGNAL")
                logger.info("=" * 60)
                logger.info(f"  Price: ${current_price:,.2f}")
                logger.info(f"  Amount: {amount:.8f}")
                logger.info(f"  Cost: ${self.amount_usd:,.2f}")
                logger.info(f"  Signals: {positive_signals}/{total_signals}")
                logger.info(f"  Reasons: {', '.join(reasons)}")
                logger.info("=" * 60)

            return {
                'action': 'buy',
                'confidence': positive_signals / total_signals,
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
        
        For buys: Add to purchases list
        For sells: Apply profit to previous purchase
        
        Args:
            order: Order details
        """
        if order.get('side') == 'buy':
            self._handle_buy_filled(order)
        elif order.get('side') == 'sell':
            self._handle_sell_filled(order)
    
    def _handle_buy_filled(self, order: Dict[str, Any]):
        """Handle a filled buy order."""
        # Calculate sell price with minimum profit
        cost = order.get('cost', 0)
        amount = order.get('filled', 0)
        price = order.get('price', 0)
        fee = order.get('fee', {}).get('cost', 0)
        
        # Sell price = (cost + fees) * (1 + min_profit)
        sell_price = ((cost + fee) / amount) * (1 + self.min_profit_percent + 0.002)  # Add 0.2% buffer
        
        purchase = {
            'buy_order_id': order.get('id'),
            'cost': cost,
            'amount': amount,
            'price': price,
            'fee': fee,
            'sell_price': sell_price,
            'dca_applied': 0.0,
            'timestamp': time.time(),
            'sell_order': {
                'status': 'pending',  # pending, filled, cancelled
                'target_price': sell_price,
                'order_id': None,
                'filled_price': None,
                'filled_timestamp': None
            }
        }

        self.purchases.append(purchase)
        
        logger.info("=" * 60)
        logger.info("Advanced DCA Purchase Complete")
        logger.info("=" * 60)
        logger.info(f"  Purchase #{len(self.purchases)}")
        logger.info(f"  Price: ${price:,.2f}")
        logger.info(f"  Amount: {amount:.8f}")
        logger.info(f"  Cost: ${cost:,.2f}")
        logger.info(f"  Sell price: ${sell_price:,.2f}")
        logger.info(f"  Active purchases: {len(self.purchases)}")
        logger.info("=" * 60)
    
    def _handle_sell_filled(self, order: Dict[str, Any]):
        """Handle a filled sell order and apply profit to previous purchase."""
        sale_amount = order.get('cost', 0)  # Total revenue from sale
        fee = order.get('fee', {}).get('cost', 0)
        sold_amount = order.get('amount', 0)

        # Find and remove the sold purchase by matching the amount
        if not self.purchases:
            logger.warning("Sell order filled but no purchases in list!")
            return

        # Find the purchase that matches this sell order (by amount)
        sold_purchase = None
        for i, purchase in enumerate(self.purchases):
            if abs(purchase.get('amount', 0) - sold_amount) < 1e-10:  # Floating point comparison
                sold_purchase = self.purchases.pop(i)
                break

        if not sold_purchase:
            logger.warning(f"Could not find purchase matching sell amount {sold_amount:.8f}")
            return

        # Update sell order status
        if 'sell_order' in sold_purchase:
            sold_purchase['sell_order']['status'] = 'filled'
            sold_purchase['sell_order']['order_id'] = order.get('id')
            sold_purchase['sell_order']['filled_price'] = order.get('price', 0)
            sold_purchase['sell_order']['filled_timestamp'] = time.time()

        # Calculate profit
        purchase_cost = sold_purchase['cost']
        profit_minimum = self.min_profit_percent * purchase_cost
        total_profit = sale_amount - fee - purchase_cost
        leftover_profit = total_profit - profit_minimum

        # Calculate DCA to add to previous purchase
        dca_to_add = 0.0
        if leftover_profit > 0:
            dca_to_add = leftover_profit * self.dca_pool_percent

        logger.info("=" * 60)
        logger.info("Advanced DCA Sale Complete")
        logger.info("=" * 60)
        logger.info(f"  Sale revenue: ${sale_amount:,.2f}")
        logger.info(f"  Purchase cost: ${purchase_cost:,.2f}")
        logger.info(f"  Total profit: ${total_profit:,.2f}")
        logger.info(f"  DCA to apply: ${dca_to_add:,.2f}")
        logger.info("=" * 60)

        self.total_profit += total_profit

        # Apply DCA to previous purchase if exists
        if dca_to_add > 0 and len(self.purchases) > 0:
            self._apply_dca_to_previous(dca_to_add)
    
    def _apply_dca_to_previous(self, dca_amount: float):
        """
        Apply DCA profit to the previous purchase to lower its cost basis.
        
        Args:
            dca_amount: Amount of profit to apply
        """
        # Apply to the most recent remaining purchase (last in list)
        prev_purchase = self.purchases[-1]
        
        logger.info(f"Applying ${dca_amount:,.2f} DCA to previous purchase...")
        logger.info(f"  Previous cost: ${prev_purchase['cost']:,.2f}")
        
        # Reduce the cost by the DCA amount
        new_cost = prev_purchase['cost'] - dca_amount
        
        # Recalculate sell price based on new cost
        adj_profit = self.min_profit_percent + 0.002  # Add 0.2% buffer
        amount_and_profit = (1 + adj_profit) * (new_cost + (2 * prev_purchase['fee']))
        new_sell_price = amount_and_profit / prev_purchase['amount']
        
        logger.info(f"  New cost: ${new_cost:,.2f}")
        logger.info(f"  Old sell price: ${prev_purchase['sell_price']:,.2f}")
        logger.info(f"  New sell price: ${new_sell_price:,.2f}")
        
        # Update the purchase
        prev_purchase['cost'] = new_cost
        prev_purchase['sell_price'] = new_sell_price
        prev_purchase['dca_applied'] += dca_amount
        
        self.total_dca_applied += dca_amount
        
        logger.info(f"✓ DCA applied successfully")
        logger.info(f"  Total DCA applied: ${self.total_dca_applied:,.2f}")
        
        # TODO: Cancel and replace the sell order on the exchange with new price
        # This would require exchange integration
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get current strategy state.

        Returns:
            State dictionary
        """
        return {
            'purchases': self.purchases,
            'total_profit': self.total_profit,
            'total_dca_applied': self.total_dca_applied,
            'trailing_state': self.trailing_state
        }

    def restore_state(self, state: Dict[str, Any]):
        """
        Restore strategy state.

        Args:
            state: Saved state dictionary
        """
        self.purchases = state.get('purchases', [])
        self.total_profit = state.get('total_profit', 0.0)
        self.total_dca_applied = state.get('total_dca_applied', 0.0)

        # Restore trailing state
        if 'trailing_state' in state:
            self.trailing_state = state['trailing_state']
            if self.trailing_state.get('status') != 'inactive':
                logger.info(f"Trailing state restored: {self.trailing_state['status']} "
                           f"{self.trailing_state['direction']} from ${self.trailing_state.get('activation_price', 0):,.2f}")

        logger.info(f"State restored: {len(self.purchases)} active purchases, "
                   f"${self.total_profit:,.2f} total profit, "
                   f"${self.total_dca_applied:,.2f} total DCA applied")

    def start_trailing(self, direction: str, activation_price: float, trailing_percent: float):
        """Start trailing for buy or sell (same as DCA strategy)."""
        self.trailing_state = {
            'status': 'waiting',
            'direction': direction,
            'activation_price': activation_price,
            'watermark': None,
            'trailing_percent': trailing_percent,
            'last_update': time.time()
        }
        logger.info(f"Trailing started: {direction} from ${activation_price:,.2f} with {trailing_percent}% trail")

    def update_trailing(self, current_price: float) -> bool:
        """Update trailing state (same logic as DCA strategy)."""
        if self.trailing_state['status'] == 'inactive':
            return False

        direction = self.trailing_state['direction']
        activation_price = self.trailing_state['activation_price']
        trailing_percent = self.trailing_state['trailing_percent']

        if self.trailing_state['status'] == 'waiting':
            if direction == 'up' and current_price >= activation_price:
                self.trailing_state['status'] = 'active'
                self.trailing_state['watermark'] = current_price
                self.trailing_state['last_update'] = time.time()
                logger.info(f"Trailing activated at ${current_price:,.2f}")
            elif direction == 'down' and current_price <= activation_price:
                self.trailing_state['status'] = 'active'
                self.trailing_state['watermark'] = current_price
                self.trailing_state['last_update'] = time.time()
                logger.info(f"Trailing activated at ${current_price:,.2f}")
            return False

        if self.trailing_state['status'] == 'active':
            watermark = self.trailing_state['watermark']

            if direction == 'up':
                if current_price > watermark:
                    self.trailing_state['watermark'] = current_price
                    self.trailing_state['last_update'] = time.time()

                drop_percent = ((watermark - current_price) / watermark) * 100
                if drop_percent >= trailing_percent:
                    logger.info(f"Trailing sell triggered! Price dropped {drop_percent:.2f}%")
                    self.trailing_state['status'] = 'triggered'
                    return True

            elif direction == 'down':
                if current_price < watermark:
                    self.trailing_state['watermark'] = current_price
                    self.trailing_state['last_update'] = time.time()

                rise_percent = ((current_price - watermark) / watermark) * 100
                if rise_percent >= trailing_percent:
                    logger.info(f"Trailing buy triggered! Price rose {rise_percent:.2f}%")
                    self.trailing_state['status'] = 'triggered'
                    return True

        return False

    def reset_trailing(self):
        """Reset trailing state."""
        if self.trailing_state['status'] != 'inactive':
            logger.info("Resetting trailing state")
            self.trailing_state = {
                'status': 'inactive',
                'direction': None,
                'activation_price': None,
                'watermark': None,
                'trailing_percent': None,
                'last_update': None
            }

