"""
CCXT Exchange Plugin

Universal exchange connector using the ccxt library.
Supports all exchanges that ccxt supports.
"""

import ccxt
from typing import Dict, Any, Optional, List
from plugins.base.exchange_plugin import ExchangePlugin
from utils.logger import get_logger

logger = get_logger(__name__)


class CCXTExchange(ExchangePlugin):
    """
    Universal exchange connector using ccxt.

    Supports:
    - Binance.US
    - Coinbase
    - Kraken
    - And 100+ other exchanges
    """

    # Map user-friendly exchange names to ccxt IDs
    EXCHANGE_ID_MAP = {
        'binance_us': 'binanceus',
        'coinbase': 'coinbasepro',
        'coinbase_pro': 'coinbasepro',
        'binance': 'binance',
        'kraken': 'kraken',
        'kucoin': 'kucoin',
        'okx': 'okx',
    }

    def __init__(self, config: Dict[str, Any], secret_provider):
        """
        Initialize CCXT exchange connector.

        Args:
            config: Exchange configuration
            secret_provider: Secure key storage
        """
        super().__init__(config, secret_provider)

        self.exchange_id = config.get('exchange', 'binance_us')
        self.paper_trading = config.get('paper_trading', False)
        self.exchange = None

        logger.info(f"Initializing {self.exchange_id} connector")
    
    def connect(self):
        """
        Connect to exchange using ccxt.
        """
        logger.info(f"Connecting to {self.exchange_id}...")

        # Map user-friendly exchange ID to ccxt ID
        ccxt_exchange_id = self.EXCHANGE_ID_MAP.get(self.exchange_id, self.exchange_id)

        # Get exchange class from ccxt
        exchange_class = getattr(ccxt, ccxt_exchange_id, None)

        if not exchange_class:
            raise ValueError(
                f"Exchange {self.exchange_id} (ccxt: {ccxt_exchange_id}) not supported by ccxt. "
                f"Available exchanges: {', '.join(ccxt.exchanges)}"
            )
        
        # Get API credentials from secure storage
        credentials = self.secret_provider.get_key(self.exchange_id)
        
        if not credentials and not self.paper_trading:
            raise ValueError(
                f"No API credentials found for {self.exchange_id}. "
                "Please run interactive setup first."
            )
        
        # Initialize exchange
        exchange_config = {
            'enableRateLimit': True,  # Respect rate limits
            'timeout': 30000,         # 30 second timeout
        }
        
        if credentials:
            api_key, api_secret = credentials
            exchange_config['apiKey'] = api_key
            exchange_config['secret'] = api_secret
        
        self.exchange = exchange_class(exchange_config)
        
        # Load markets
        logger.info("Loading markets...")
        self.exchange.load_markets()
        
        logger.info(f"✓ Connected to {self.exchange_id}")
        logger.info(f"✓ Loaded {len(self.exchange.markets)} markets")
        
        # Verify credentials if not paper trading
        if not self.paper_trading and credentials:
            try:
                balance = self.exchange.fetch_balance()
                logger.info("✓ API credentials verified")
            except Exception as e:
                logger.error(f"Failed to verify API credentials: {e}")
                raise
    
    def disconnect(self):
        """
        Disconnect from exchange.
        """
        logger.info(f"Disconnecting from {self.exchange_id}")

        if self.exchange:
            # Close any open connections
            if hasattr(self.exchange, 'close'):
                self.exchange.close()

        self.exchange = None
        logger.info("✓ Disconnected")

    def check_connectivity(self) -> bool:
        """
        Check if exchange is reachable.

        Returns:
            True if connected, False otherwise
        """
        try:
            # Quick ping to exchange - fetch status or time
            if hasattr(self.exchange, 'fetch_status'):
                self.exchange.fetch_status()
            else:
                # Fallback: fetch server time (lightweight call)
                self.exchange.fetch_time()

            logger.debug(f"Connectivity check passed for {self.exchange_id}")
            return True

        except Exception as e:
            logger.warning(f"Connectivity check failed for {self.exchange_id}: {e}")
            return False

    def get_balance(self) -> Dict[str, float]:
        """
        Get account balance.
        
        Returns:
            Dictionary of {currency: amount}
        """
        if self.paper_trading:
            logger.warning("Paper trading mode - returning mock balance")
            return {'USD': 10000.0, 'BTC': 0.0}
        
        logger.debug("Fetching balance...")
        balance = self.exchange.fetch_balance()
        
        # Return free balance (available for trading)
        return balance.get('free', {})
    
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
            order_type: 'limit', 'market', 'stop_loss', 'stop_loss_limit', etc.
            params: Additional exchange-specific parameters

        Returns:
            Order details
        """
        if params is None:
            params = {}
        if self.paper_trading:
            logger.warning(f"⚠️  PAPER TRADING - Would place {side} {order_type} order: "
                          f"{amount} {symbol} @ {price}")
            return {
                'id': 'paper_' + str(hash(f"{symbol}{side}{amount}{price}")),
                'symbol': symbol,
                'side': side,
                'type': order_type,
                'amount': amount,
                'price': price,
                'status': 'closed',
                'filled': amount
            }
        
        logger.info(f"Placing {side} {order_type} order: {amount} {symbol} @ {price}")
        if params:
            logger.info(f"  Additional params: {params}")

        try:
            # Use create_order for maximum flexibility with params
            order = self.exchange.create_order(
                symbol=symbol,
                type=order_type,
                side=side,
                amount=amount,
                price=price,
                params=params
            )

            logger.info(f"✓ Order placed: {order['id']}")
            return order

        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            raise
    
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """
        Cancel an order.
        
        Args:
            order_id: Order ID
            symbol: Trading pair
            
        Returns:
            True if cancelled successfully
        """
        if self.paper_trading:
            logger.warning(f"⚠️  PAPER TRADING - Would cancel order {order_id}")
            return True
        
        logger.info(f"Cancelling order {order_id}")
        
        try:
            self.exchange.cancel_order(order_id, symbol)
            logger.info(f"✓ Order cancelled: {order_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel order: {e}")
            return False
    
    def get_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """
        Get order details.
        
        Args:
            order_id: Order ID
            symbol: Trading pair
            
        Returns:
            Order details
        """
        logger.debug(f"Fetching order {order_id}")
        return self.exchange.fetch_order(order_id, symbol)
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get open orders.
        
        Args:
            symbol: Trading pair (None for all pairs)
            
        Returns:
            List of open orders
        """
        if self.paper_trading:
            return []
        
        logger.debug(f"Fetching open orders for {symbol or 'all symbols'}")
        return self.exchange.fetch_open_orders(symbol)
    
    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get current market data (ticker).
        
        Args:
            symbol: Trading pair
            
        Returns:
            Market data
        """
        logger.debug(f"Fetching market data for {symbol}")
        ticker = self.exchange.fetch_ticker(symbol)
        
        return {
            'symbol': symbol,
            'last': ticker.get('last'),
            'bid': ticker.get('bid'),
            'ask': ticker.get('ask'),
            'high': ticker.get('high'),
            'low': ticker.get('low'),
            'volume': ticker.get('volume'),
            'timestamp': ticker.get('timestamp')
        }
    
    def get_orderbook(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
        """
        Get order book.
        
        Args:
            symbol: Trading pair
            limit: Number of levels
            
        Returns:
            Order book data
        """
        logger.debug(f"Fetching orderbook for {symbol}")
        return self.exchange.fetch_order_book(symbol, limit)
    
    def subscribe_websocket(self, symbol: str, callback):
        """
        Subscribe to WebSocket updates.
        
        Args:
            symbol: Trading pair
            callback: Function to call with updates
        """
        # TODO: Implement WebSocket using ccxt.pro
        logger.warning("WebSocket not yet implemented")
        pass
    
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
            List of OHLCV candles [timestamp, open, high, low, close, volume]
        """
        logger.debug(f"Fetching {timeframe} candles for {symbol}")
        return self.exchange.fetch_ohlcv(symbol, timeframe, since, limit)

    def supports_trailing_orders(self) -> bool:
        """
        Check if exchange supports trailing orders.

        Different exchanges have different support for trailing orders.
        Binance, Binance.US, and some others support them.

        Returns:
            True if trailing orders are supported
        """
        # List of exchanges known to support trailing orders
        trailing_supported = [
            'binance',
            'binanceus',
            'binanceusdm',  # Binance USD-M Futures
            'binancecoinm',  # Binance COIN-M Futures
        ]

        exchange_id = self.exchange.id.lower()
        return exchange_id in trailing_supported

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

        For Binance/Binance.US:
        - Trailing orders use the 'trailingPercent' parameter
        - The order trails the market price by the specified percentage

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
        if not self.supports_trailing_orders():
            raise NotImplementedError(
                f"{self.exchange.id} does not support trailing orders. "
                "Consider implementing bot-managed trailing orders instead."
            )

        exchange_id = self.exchange.id.lower()

        # Binance-style trailing orders
        if exchange_id in ['binance', 'binanceus', 'binanceusdm', 'binancecoinm']:
            params = {
                'trailingPercent': trailing_percent,  # Percentage away from current market price
            }

            # For Binance, trailing orders are typically stop-loss or take-profit orders
            if side == 'sell':
                # Trailing sell (stop-loss that trails up)
                order_type_to_use = 'TRAILING_STOP_MARKET'
            else:
                # Trailing buy (less common, but supported)
                order_type_to_use = 'TRAILING_STOP_MARKET'

            logger.info(f"Placing trailing {side} order: {amount} {symbol}")
            logger.info(f"  Trailing percent: {trailing_percent}%")
            logger.info(f"  Order type: {order_type_to_use}")

            if self.paper_trading:
                logger.warning(f"⚠️  PAPER TRADING - Would place trailing {side} order")
                return {
                    'id': 'paper_trailing_' + str(hash(f"{symbol}{side}{amount}{trailing_percent}")),
                    'symbol': symbol,
                    'side': side,
                    'type': order_type_to_use,
                    'amount': amount,
                    'status': 'open',
                    'info': {'trailingPercent': trailing_percent}
                }

            try:
                order = self.exchange.create_order(
                    symbol=symbol,
                    type=order_type_to_use,
                    side=side,
                    amount=amount,
                    price=None,  # Market price for trailing orders
                    params=params
                )

                logger.info(f"✓ Trailing order placed: {order['id']}")
                return order

            except Exception as e:
                logger.error(f"Failed to place trailing order: {e}")
                raise

        # Other exchanges - would need specific implementation
        raise NotImplementedError(
            f"Trailing orders not yet implemented for {self.exchange.id}"
        )

