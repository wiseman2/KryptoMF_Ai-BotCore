"""
Tests for DCA Strategy

Tests the Dollar Cost Averaging strategy implementation.
"""

import pytest
import time
from unittest.mock import Mock
from plugins.strategies.dca import DCAStrategy


class TestDCAStrategy:
    """Test DCAStrategy class."""
    
    def test_strategy_creation(self, dca_strategy_config):
        """Test strategy creation."""
        strategy = DCAStrategy(dca_strategy_config)
        
        assert strategy.name == 'dca'
        assert strategy.interval_hours == 24
        assert strategy.amount_usd == 100
        assert strategy.max_price == 70000
        assert strategy.min_price == 60000
        assert strategy.last_purchase_time is None
        assert strategy.total_purchased == 0.0
        assert strategy.total_spent == 0.0
        assert strategy.purchase_count == 0
    
    def test_strategy_initialization(self, dca_strategy_config):
        """Test strategy initialization with bot instance."""
        strategy = DCAStrategy(dca_strategy_config)
        bot = Mock()
        
        strategy.initialize(bot)
        
        assert strategy.bot == bot
    
    def test_analyze_first_purchase(self, dca_strategy_config, market_data):
        """Test first purchase (no previous purchase)."""
        strategy = DCAStrategy(dca_strategy_config)
        bot = Mock()
        strategy.initialize(bot)
        
        signal = strategy.analyze(market_data)
        
        assert signal['action'] == 'buy'
        assert signal['confidence'] == 1.0
        assert 'metadata' in signal
        assert 'price' in signal['metadata']
        assert 'amount' in signal['metadata']
        
        # Check amount calculation
        expected_amount = strategy.amount_usd / market_data['last']
        assert abs(signal['metadata']['amount'] - expected_amount) < 0.00000001
    
    def test_analyze_interval_not_reached(self, dca_strategy_config, market_data):
        """Test when interval hasn't been reached yet."""
        strategy = DCAStrategy(dca_strategy_config)
        bot = Mock()
        strategy.initialize(bot)
        
        # Set last purchase time to now
        strategy.last_purchase_time = time.time()
        
        signal = strategy.analyze(market_data)
        
        assert signal['action'] == 'hold'
        assert 'Next purchase in' in signal['reason']
    
    def test_analyze_price_above_max(self, dca_strategy_config, market_data):
        """Test when price is above max_price."""
        strategy = DCAStrategy(dca_strategy_config)
        bot = Mock()
        strategy.initialize(bot)
        
        # Set price above max
        market_data['last'] = 75000.0
        
        signal = strategy.analyze(market_data)
        
        assert signal['action'] == 'hold'
        assert 'above max' in signal['reason']
    
    def test_analyze_price_below_min(self, dca_strategy_config, market_data):
        """Test when price is below min_price."""
        strategy = DCAStrategy(dca_strategy_config)
        bot = Mock()
        strategy.initialize(bot)
        
        # Set price below min
        market_data['last'] = 55000.0
        
        signal = strategy.analyze(market_data)
        
        assert signal['action'] == 'hold'
        assert 'below min' in signal['reason']
    
    def test_on_order_filled(self, dca_strategy_config):
        """Test order filled event updates stats."""
        strategy = DCAStrategy(dca_strategy_config)
        bot = Mock()
        strategy.initialize(bot)
        
        # Simulate order fill
        order = {
            'id': 'test_123',
            'side': 'buy',
            'price': 67450.0,
            'amount': 0.01,
            'filled': 0.01,
            'cost': 674.50
        }
        
        strategy.on_order_filled(order)
        
        assert strategy.purchase_count == 1
        assert strategy.total_purchased == 0.01
        assert strategy.total_spent == 674.50
        assert strategy.last_purchase_time is not None
    
    def test_get_state(self, dca_strategy_config):
        """Test get_state method."""
        strategy = DCAStrategy(dca_strategy_config)
        bot = Mock()
        strategy.initialize(bot)
        
        # Set some state
        strategy.last_purchase_time = time.time()
        strategy.total_purchased = 0.05
        strategy.total_spent = 3000.0
        strategy.purchase_count = 5
        
        state = strategy.get_state()
        
        assert 'last_purchase_time' in state
        assert 'total_purchased' in state
        assert 'total_spent' in state
        assert 'purchase_count' in state
        assert state['total_purchased'] == 0.05
        assert state['total_spent'] == 3000.0
        assert state['purchase_count'] == 5
    
    def test_restore_state(self, dca_strategy_config):
        """Test restore_state method."""
        strategy = DCAStrategy(dca_strategy_config)
        bot = Mock()
        strategy.initialize(bot)
        
        # Create state
        state = {
            'last_purchase_time': time.time(),
            'total_purchased': 0.1,
            'total_spent': 6000.0,
            'purchase_count': 10
        }
        
        # Restore state
        strategy.restore_state(state)
        
        assert strategy.last_purchase_time == state['last_purchase_time']
        assert strategy.total_purchased == 0.1
        assert strategy.total_spent == 6000.0
        assert strategy.purchase_count == 10
    
    def test_average_price_calculation(self, dca_strategy_config):
        """Test average price calculation."""
        strategy = DCAStrategy(dca_strategy_config)
        bot = Mock()
        strategy.initialize(bot)
        
        # Simulate multiple purchases
        orders = [
            {'price': 60000.0, 'amount': 0.01, 'cost': 600.0},
            {'price': 65000.0, 'amount': 0.01, 'cost': 650.0},
            {'price': 70000.0, 'amount': 0.01, 'cost': 700.0},
        ]
        
        for order in orders:
            order['id'] = 'test'
            order['side'] = 'buy'
            order['filled'] = order['amount']
            strategy.on_order_filled(order)
        
        # Calculate average price
        average_price = strategy.total_spent / strategy.total_purchased
        
        assert strategy.purchase_count == 3
        assert strategy.total_purchased == 0.03
        assert strategy.total_spent == 1950.0
        assert abs(average_price - 65000.0) < 0.01
    
    def test_custom_parameters(self):
        """Test strategy with custom parameters."""
        config = {
            'name': 'dca',
            'params': {
                'interval_hours': 12,  # Every 12 hours
                'amount_usd': 50,      # $50 per purchase
                'max_price': 80000,
                'min_price': 50000
            }
        }
        
        strategy = DCAStrategy(config)
        
        assert strategy.interval_hours == 12
        assert strategy.amount_usd == 50
        assert strategy.max_price == 80000
        assert strategy.min_price == 50000
    
    def test_no_price_limits(self):
        """Test DCA without price limits."""
        config = {
            'name': 'dca',
            'params': {
                'interval_hours': 24,
                'amount_usd': 100
                # No max_price or min_price
            }
        }
        
        strategy = DCAStrategy(config)
        bot = Mock()
        strategy.initialize(bot)
        
        # Should buy at any price
        market_data = {'last': 100000.0}  # Very high price
        signal = strategy.analyze(market_data)
        
        assert signal['action'] == 'buy'

