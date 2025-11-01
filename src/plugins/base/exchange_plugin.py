"""
Exchange Plugin Base Class

All exchange connectors must inherit from this class.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class ExchangePlugin(ABC):
    """
    Base class for exchange connectors.
    
    All exchange plugins must implement these methods to provide
    a consistent interface for the bot engine.
    """
    
    def __init__(self, config: Dict[str, Any], secret_provider):
        """
        Initialize exchange plugin.
        
        Args:
            config: Exchange configuration
            secret_provider: Secure key storage interface
        """
        self.config = config
        self.secret_provider = secret_provider
        self.exchange_id = config.get('exchange_id', 'unknown')
    
    @abstractmethod
    def connect(self):
        """
        Establish connection to exchange.
        
        This should:
        - Load API credentials from secret_provider
        - Initialize exchange client
        - Verify connection
        """
        pass
    
    @abstractmethod
    def disconnect(self):
        """
        Disconnect from exchange.
        
        This should:
        - Close WebSocket connections
        - Clean up resources
        """
        pass
    
    @abstractmethod
    def get_balance(self) -> Dict[str, float]:
        """
        Get account balance.
        
        Returns:
            Dictionary of {currency: amount}
        """
        pass
    
    @abstractmethod
    def place_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        price: Optional[float] = None,
        order_type: str = 'limit',
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Place an order.

        Args:
            symbol: Trading pair (e.g., 'BTC/USD')
            side: 'buy' or 'sell'
            amount: Order amount
            price: Order price (None for market orders)
            order_type: 'limit', 'market', 'stop_loss', 'stop_loss_limit', 'take_profit', 'take_profit_limit'
            params: Additional exchange-specific parameters (e.g., trailing orders)

        Returns:
            Order details
        """
        pass

    def place_trailing_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        trailing_percent: float,
        price: Optional[float] = None,
        order_type: str = 'limit'
    ) -> Dict[str, Any]:
        """
        Place a trailing order (if supported by exchange).

        Trailing orders automatically adjust the trigger price as the market moves
        in a favorable direction. This helps protect profits and limit losses.

        For trailing sell: Order price trails below market price by trailing_percent.
        For trailing buy: Order price trails above market price by trailing_percent.

        Args:
            symbol: Trading pair (e.g., 'BTC/USD')
            side: 'buy' or 'sell'
            amount: Order amount
            trailing_percent: Percentage to trail (e.g., 1.0 for 1%)
            price: Initial price (optional, uses market price if None)
            order_type: 'limit' or 'market'

        Returns:
            Order details

        Raises:
            NotImplementedError: If exchange doesn't support trailing orders
        """
        raise NotImplementedError(
            f"{self.name} does not support trailing orders. "
            "Override this method in the exchange plugin if supported."
        )

    def supports_trailing_orders(self) -> bool:
        """
        Check if exchange supports trailing orders.

        Returns:
            True if trailing orders are supported
        """
        return False
    
    @abstractmethod
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """
        Cancel an order.
        
        Args:
            order_id: Order ID
            symbol: Trading pair
            
        Returns:
            True if cancelled successfully
        """
        pass
    
    @abstractmethod
    def get_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """
        Get order details.
        
        Args:
            order_id: Order ID
            symbol: Trading pair
            
        Returns:
            Order details
        """
        pass
    
    @abstractmethod
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get open orders.
        
        Args:
            symbol: Trading pair (None for all pairs)
            
        Returns:
            List of open orders
        """
        pass
    
    @abstractmethod
    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get current market data.
        
        Args:
            symbol: Trading pair
            
        Returns:
            Market data (ticker, price, volume, etc.)
        """
        pass
    
    @abstractmethod
    def get_orderbook(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
        """
        Get order book.
        
        Args:
            symbol: Trading pair
            limit: Number of levels
            
        Returns:
            Order book data
        """
        pass
    
    @abstractmethod
    def subscribe_websocket(self, symbol: str, callback):
        """
        Subscribe to WebSocket updates.
        
        Args:
            symbol: Trading pair
            callback: Function to call with updates
        """
        pass
    
    @abstractmethod
    def get_historical_data(
        self,
        symbol: str,
        timeframe: str,
        since: Optional[int] = None,
        limit: int = 100
    ) -> List[List]:
        """
        Get historical OHLCV data.
        
        Args:
            symbol: Trading pair
            timeframe: Timeframe (e.g., '1m', '5m', '1h', '1d')
            since: Start timestamp (milliseconds)
            limit: Number of candles
            
        Returns:
            List of OHLCV candles
        """
        pass

