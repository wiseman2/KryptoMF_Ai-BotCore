"""
Tests for CCXT Exchange Connector

Tests the universal exchange connector.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from plugins.exchanges.ccxt_exchange import CCXTExchange


class TestCCXTExchange:
    """Test CCXTExchange class."""
    
    def test_exchange_creation(self, mock_secret_provider):
        """Test exchange creation."""
        config = {
            'exchange': 'binance_us',
            'paper_trading': True
        }
        
        exchange = CCXTExchange(config, mock_secret_provider)
        
        assert exchange.exchange_id == 'binance_us'
        assert exchange.paper_trading is True
        assert exchange.exchange is None
    
    @patch('plugins.exchanges.ccxt_exchange.ccxt')
    def test_connect_paper_trading(self, mock_ccxt, mock_secret_provider):
        """Test connection in paper trading mode."""
        config = {
            'exchange': 'binance_us',
            'paper_trading': True
        }
        
        # Setup mock
        mock_exchange_class = Mock()
        mock_exchange_instance = Mock()
        mock_exchange_instance.load_markets.return_value = None
        mock_exchange_class.return_value = mock_exchange_instance
        mock_ccxt.binance_us = mock_exchange_class
        
        # Create and connect
        exchange = CCXTExchange(config, mock_secret_provider)
        exchange.connect()
        
        assert exchange.exchange is not None
        mock_exchange_instance.load_markets.assert_called_once()
    
    @patch('plugins.exchanges.ccxt_exchange.ccxt')
    def test_connect_with_credentials(self, mock_ccxt, mock_secret_provider):
        """Test connection with API credentials."""
        config = {
            'exchange': 'binance_us',
            'paper_trading': False
        }
        
        # Setup mock
        mock_exchange_class = Mock()
        mock_exchange_instance = Mock()
        mock_exchange_instance.load_markets.return_value = None
        mock_exchange_instance.fetch_balance.return_value = {'free': {'USD': 1000.0}}
        mock_exchange_class.return_value = mock_exchange_instance
        mock_ccxt.binance_us = mock_exchange_class
        
        # Create and connect
        exchange = CCXTExchange(config, mock_secret_provider)
        exchange.connect()
        
        assert exchange.exchange is not None
        mock_exchange_instance.load_markets.assert_called_once()
        mock_exchange_instance.fetch_balance.assert_called_once()
    
    @patch('plugins.exchanges.ccxt_exchange.ccxt')
    def test_connect_invalid_exchange(self, mock_ccxt, mock_secret_provider):
        """Test connection with invalid exchange."""
        config = {
            'exchange': 'invalid_exchange',
            'paper_trading': True
        }
        
        # Setup mock to not have the exchange
        mock_ccxt.invalid_exchange = None
        
        exchange = CCXTExchange(config, mock_secret_provider)
        
        with pytest.raises(ValueError, match="not supported"):
            exchange.connect()
    
    def test_get_balance_paper_trading(self, mock_secret_provider):
        """Test get_balance in paper trading mode."""
        config = {
            'exchange': 'binance_us',
            'paper_trading': True
        }
        
        exchange = CCXTExchange(config, mock_secret_provider)
        balance = exchange.get_balance()
        
        assert 'USD' in balance
        assert balance['USD'] == 10000.0
    
    @patch('plugins.exchanges.ccxt_exchange.ccxt')
    def test_get_balance_live(self, mock_ccxt, mock_secret_provider):
        """Test get_balance in live mode."""
        config = {
            'exchange': 'binance_us',
            'paper_trading': False
        }
        
        # Setup mock
        mock_exchange_instance = Mock()
        mock_exchange_instance.fetch_balance.return_value = {
            'free': {'USD': 5000.0, 'BTC': 0.1}
        }
        
        exchange = CCXTExchange(config, mock_secret_provider)
        exchange.exchange = mock_exchange_instance
        
        balance = exchange.get_balance()
        
        assert balance['USD'] == 5000.0
        assert balance['BTC'] == 0.1
    
    def test_place_order_paper_trading(self, mock_secret_provider):
        """Test place_order in paper trading mode."""
        config = {
            'exchange': 'binance_us',
            'paper_trading': True
        }
        
        exchange = CCXTExchange(config, mock_secret_provider)
        
        order = exchange.place_order(
            symbol='BTC/USD',
            side='buy',
            amount=0.01,
            price=67450.0,
            order_type='limit'
        )
        
        assert order['symbol'] == 'BTC/USD'
        assert order['side'] == 'buy'
        assert order['amount'] == 0.01
        assert order['price'] == 67450.0
        assert order['status'] == 'closed'
        assert 'paper_' in order['id']
    
    @patch('plugins.exchanges.ccxt_exchange.ccxt')
    def test_place_order_limit(self, mock_ccxt, mock_secret_provider):
        """Test place limit order."""
        config = {
            'exchange': 'binance_us',
            'paper_trading': False
        }
        
        # Setup mock
        mock_exchange_instance = Mock()
        mock_exchange_instance.create_limit_order.return_value = {
            'id': 'real_order_123',
            'symbol': 'BTC/USD',
            'side': 'buy',
            'amount': 0.01,
            'price': 67450.0
        }
        
        exchange = CCXTExchange(config, mock_secret_provider)
        exchange.exchange = mock_exchange_instance
        
        order = exchange.place_order(
            symbol='BTC/USD',
            side='buy',
            amount=0.01,
            price=67450.0,
            order_type='limit'
        )
        
        mock_exchange_instance.create_limit_order.assert_called_once_with(
            'BTC/USD', 'buy', 0.01, 67450.0
        )
        assert order['id'] == 'real_order_123'
    
    @patch('plugins.exchanges.ccxt_exchange.ccxt')
    def test_place_order_market(self, mock_ccxt, mock_secret_provider):
        """Test place market order."""
        config = {
            'exchange': 'binance_us',
            'paper_trading': False
        }
        
        # Setup mock
        mock_exchange_instance = Mock()
        mock_exchange_instance.create_market_order.return_value = {
            'id': 'market_order_456',
            'symbol': 'BTC/USD',
            'side': 'sell',
            'amount': 0.01
        }
        
        exchange = CCXTExchange(config, mock_secret_provider)
        exchange.exchange = mock_exchange_instance
        
        order = exchange.place_order(
            symbol='BTC/USD',
            side='sell',
            amount=0.01,
            order_type='market'
        )
        
        mock_exchange_instance.create_market_order.assert_called_once_with(
            'BTC/USD', 'sell', 0.01
        )
        assert order['id'] == 'market_order_456'
    
    def test_cancel_order_paper_trading(self, mock_secret_provider):
        """Test cancel_order in paper trading mode."""
        config = {
            'exchange': 'binance_us',
            'paper_trading': True
        }
        
        exchange = CCXTExchange(config, mock_secret_provider)
        result = exchange.cancel_order('test_order', 'BTC/USD')
        
        assert result is True
    
    @patch('plugins.exchanges.ccxt_exchange.ccxt')
    def test_cancel_order_live(self, mock_ccxt, mock_secret_provider):
        """Test cancel_order in live mode."""
        config = {
            'exchange': 'binance_us',
            'paper_trading': False
        }
        
        # Setup mock
        mock_exchange_instance = Mock()
        mock_exchange_instance.cancel_order.return_value = None
        
        exchange = CCXTExchange(config, mock_secret_provider)
        exchange.exchange = mock_exchange_instance
        
        result = exchange.cancel_order('order_123', 'BTC/USD')
        
        mock_exchange_instance.cancel_order.assert_called_once_with('order_123', 'BTC/USD')
        assert result is True
    
    @patch('plugins.exchanges.ccxt_exchange.ccxt')
    def test_get_market_data(self, mock_ccxt, mock_secret_provider):
        """Test get_market_data."""
        config = {
            'exchange': 'binance_us',
            'paper_trading': True
        }
        
        # Setup mock
        mock_exchange_instance = Mock()
        mock_exchange_instance.fetch_ticker.return_value = {
            'last': 67450.0,
            'bid': 67449.0,
            'ask': 67451.0,
            'high': 68000.0,
            'low': 66000.0,
            'volume': 1000.0,
            'timestamp': 1234567890
        }
        
        exchange = CCXTExchange(config, mock_secret_provider)
        exchange.exchange = mock_exchange_instance
        
        data = exchange.get_market_data('BTC/USD')
        
        assert data['symbol'] == 'BTC/USD'
        assert data['last'] == 67450.0
        assert data['bid'] == 67449.0
        assert data['ask'] == 67451.0
        assert data['high'] == 68000.0
        assert data['low'] == 66000.0
        assert data['volume'] == 1000.0
    
    @patch('plugins.exchanges.ccxt_exchange.ccxt')
    def test_disconnect(self, mock_ccxt, mock_secret_provider):
        """Test disconnect."""
        config = {
            'exchange': 'binance_us',
            'paper_trading': True
        }
        
        # Setup mock
        mock_exchange_instance = Mock()
        mock_exchange_instance.close = Mock()
        
        exchange = CCXTExchange(config, mock_secret_provider)
        exchange.exchange = mock_exchange_instance
        
        exchange.disconnect()
        
        mock_exchange_instance.close.assert_called_once()
        assert exchange.exchange is None

