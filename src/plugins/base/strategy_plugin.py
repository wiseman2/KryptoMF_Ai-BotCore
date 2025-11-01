"""
Strategy Plugin Base Class

All trading strategies must inherit from this class.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class StrategyPlugin(ABC):
    """
    Base class for trading strategies.
    
    All strategy plugins must implement these methods to provide
    a consistent interface for the bot engine.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize strategy plugin.
        
        Args:
            config: Strategy configuration
        """
        self.config = config
        self.name = config.get('name', 'unknown')
        self.params = config.get('params', {})
    
    @abstractmethod
    def initialize(self, bot_instance):
        """
        Initialize strategy with bot instance.
        
        This is called once when the bot starts.
        
        Args:
            bot_instance: Reference to the bot engine
        """
        pass
    
    @abstractmethod
    def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market data and return signals.
        
        Args:
            market_data: Current market data
            
        Returns:
            Signal dictionary with:
            - action: 'buy', 'sell', or 'hold'
            - confidence: 0.0 to 1.0
            - reason: Human-readable explanation
            - metadata: Additional data
        """
        pass
    
    def on_order_filled(self, order: Dict[str, Any]):
        """
        Handle order fill event.
        
        Args:
            order: Order details
        """
        pass
    
    def on_order_cancelled(self, order: Dict[str, Any]):
        """
        Handle order cancellation event.
        
        Args:
            order: Order details
        """
        pass
    
    def on_market_update(self, data: Dict[str, Any]):
        """
        Handle market data update.
        
        Args:
            data: Market data
        """
        pass
    
    def on_balance_update(self, balance: Dict[str, float]):
        """
        Handle balance update.
        
        Args:
            balance: Current balance
        """
        pass
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Return strategy parameters for UI/display.
        
        Returns:
            Dictionary of parameter names and values
        """
        return self.params
    
    def update_parameters(self, params: Dict[str, Any]):
        """
        Update strategy parameters.
        
        Args:
            params: New parameters
        """
        self.params.update(params)
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get current strategy state for persistence.
        
        Returns:
            State dictionary
        """
        return {}
    
    def restore_state(self, state: Dict[str, Any]):
        """
        Restore strategy state from persistence.
        
        Args:
            state: Saved state dictionary
        """
        pass

