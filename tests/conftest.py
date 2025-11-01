"""
Pytest Configuration and Fixtures

Shared fixtures for all tests.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))


@pytest.fixture
def mock_exchange():
    """Mock exchange connector."""
    exchange = Mock()
    exchange.exchange_id = 'binance_us'
    exchange.paper_trading = True
    exchange.get_balance.return_value = {'USD': 10000.0, 'BTC': 0.0}
    exchange.get_market_data.return_value = {
        'symbol': 'BTC/USD',
        'last': 67450.0,
        'bid': 67449.0,
        'ask': 67451.0,
        'high': 68000.0,
        'low': 66000.0,
        'volume': 1000.0,
        'timestamp': 1234567890
    }
    exchange.place_order.return_value = {
        'id': 'test_order_123',
        'symbol': 'BTC/USD',
        'side': 'buy',
        'type': 'limit',
        'amount': 0.01,
        'price': 67450.0,
        'status': 'closed',
        'filled': 0.01
    }
    return exchange


@pytest.fixture
def mock_secret_provider():
    """Mock secret provider."""
    provider = Mock()
    provider.get_key.return_value = ('test_api_key', 'test_api_secret')
    provider.store_key.return_value = None
    return provider


@pytest.fixture
def bot_config():
    """Sample bot configuration."""
    return {
        'name': 'Test Bot',
        'exchange': 'binance_us',
        'symbol': 'BTC/USD',
        'strategy': 'grid_trading',
        'strategy_params': {
            'grid_spacing': 2.5,
            'grid_levels': 10,
            'position_size': 100
        },
        'paper_trading': True,
        'check_interval': 1  # 1 second for faster tests
    }


@pytest.fixture
def grid_strategy_config():
    """Grid trading strategy configuration."""
    return {
        'name': 'grid_trading',
        'params': {
            'grid_spacing': 2.5,
            'grid_levels': 10,
            'position_size': 100
        }
    }


@pytest.fixture
def dca_strategy_config():
    """DCA strategy configuration."""
    return {
        'name': 'dca',
        'params': {
            'interval_hours': 24,
            'amount_usd': 100,
            'max_price': 70000,
            'min_price': 60000
        }
    }


@pytest.fixture
def market_data():
    """Sample market data."""
    return {
        'symbol': 'BTC/USD',
        'last': 67450.0,
        'bid': 67449.0,
        'ask': 67451.0,
        'high': 68000.0,
        'low': 66000.0,
        'volume': 1000.0,
        'timestamp': 1234567890
    }

