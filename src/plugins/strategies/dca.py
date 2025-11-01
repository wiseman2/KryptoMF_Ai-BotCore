"""
DCA (Dollar Cost Averaging) Strategy

Buys a fixed amount of cryptocurrency at regular intervals, regardless of price.
This strategy reduces the impact of volatility by averaging the purchase price over time.

Good for long-term accumulation and reducing timing risk.
"""

import time
from typing import Dict, Any
from plugins.base.strategy_plugin import StrategyPlugin
from utils.logger import get_logger

logger = get_logger(__name__)


class DCAStrategy(StrategyPlugin):
    """
    Dollar Cost Averaging (DCA) strategy.
    
    Buys a fixed amount at regular intervals.
    
    Parameters:
    - interval_hours: Hours between purchases (default: 24)
    - amount_usd: Amount to purchase each interval (default: 100)
    - max_price: Maximum price to buy at (optional)
    - min_price: Minimum price to buy at (optional)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize DCA strategy.
        
        Args:
            config: Strategy configuration
        """
        super().__init__(config)
        
        # Strategy parameters
        self.interval_hours = self.params.get('interval_hours', 24)
        self.amount_usd = self.params.get('amount_usd', 100)
        self.max_price = self.params.get('max_price', None)
        self.min_price = self.params.get('min_price', None)
        
        # State
        self.last_purchase_time = None
        self.total_purchased = 0.0
        self.total_spent = 0.0
        self.purchase_count = 0
        self.bot = None
        
        logger.info(f"DCA Strategy initialized:")
        logger.info(f"  Interval: {self.interval_hours} hours")
        logger.info(f"  Amount: ${self.amount_usd} per purchase")
        if self.max_price:
            logger.info(f"  Max price: ${self.max_price:,.2f}")
        if self.min_price:
            logger.info(f"  Min price: ${self.min_price:,.2f}")
    
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
        Analyze market and determine if it's time to buy.
        
        Args:
            market_data: Current market data
            
        Returns:
            Signal dictionary
        """
        current_price = market_data.get('last')
        current_time = time.time()
        
        if not current_price:
            return {
                'action': 'hold',
                'confidence': 0.0,
                'reason': 'No price data available'
            }
        
        logger.info(f"Current price: ${current_price:,.2f}")
        
        # Check if it's time to buy
        if self.last_purchase_time:
            time_since_last = (current_time - self.last_purchase_time) / 3600  # hours
            logger.info(f"Time since last purchase: {time_since_last:.1f} hours")
            
            if time_since_last < self.interval_hours:
                hours_remaining = self.interval_hours - time_since_last
                return {
                    'action': 'hold',
                    'confidence': 1.0,
                    'reason': f'Next purchase in {hours_remaining:.1f} hours',
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
        
        # Time to buy!
        amount = self.amount_usd / current_price
        
        logger.info("=" * 60)
        logger.info("DCA BUY SIGNAL")
        logger.info("=" * 60)
        logger.info(f"  Price: ${current_price:,.2f}")
        logger.info(f"  Amount: {amount:.8f}")
        logger.info(f"  Cost: ${self.amount_usd:,.2f}")
        logger.info("=" * 60)
        
        return {
            'action': 'buy',
            'confidence': 1.0,
            'reason': f'DCA interval reached - buying ${self.amount_usd}',
            'metadata': {
                'price': current_price,
                'amount': amount,
                'cost': self.amount_usd
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

