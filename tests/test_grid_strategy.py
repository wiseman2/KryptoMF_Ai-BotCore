"""
Tests for Grid Trading Strategy

Tests the grid trading strategy implementation.
"""

import pytest
from unittest.mock import Mock
from plugins.strategies.grid_trading import GridTradingStrategy


class TestGridTradingStrategy:
    """Test GridTradingStrategy class."""
    
    def test_strategy_creation(self, grid_strategy_config):
        """Test strategy creation."""
        strategy = GridTradingStrategy(grid_strategy_config)
        
        assert strategy.name == 'grid_trading'
        assert strategy.grid_spacing == 2.5
        assert strategy.grid_levels == 10
        assert strategy.position_size == 100
        assert strategy.grid_orders == []
        assert strategy.current_price is None
    
    def test_strategy_initialization(self, grid_strategy_config):
        """Test strategy initialization with bot instance."""
        strategy = GridTradingStrategy(grid_strategy_config)
        bot = Mock()
        
        strategy.initialize(bot)
        
        assert strategy.bot == bot
    
    def test_analyze_no_price(self, grid_strategy_config):
        """Test analyze with no price data."""
        strategy = GridTradingStrategy(grid_strategy_config)
        bot = Mock()
        strategy.initialize(bot)
        
        market_data = {'symbol': 'BTC/USD'}
        signal = strategy.analyze(market_data)
        
        assert signal['action'] == 'hold'
        assert signal['confidence'] == 0.0
        assert 'No price data' in signal['reason']
    
    def test_analyze_first_run(self, grid_strategy_config, market_data):
        """Test analyze on first run (places grid orders)."""
        strategy = GridTradingStrategy(grid_strategy_config)
        bot = Mock()
        strategy.initialize(bot)
        
        signal = strategy.analyze(market_data)
        
        assert signal['action'] == 'hold'
        assert signal['confidence'] == 1.0
        assert 'Placed' in signal['reason']
        assert 'grid_orders' in signal['metadata']
        assert len(strategy.grid_orders) == 20  # 10 buy + 10 sell levels
    
    def test_grid_level_calculation(self, grid_strategy_config, market_data):
        """Test grid level calculation."""
        strategy = GridTradingStrategy(grid_strategy_config)
        bot = Mock()
        strategy.initialize(bot)
        strategy.current_price = market_data['last']
        
        levels = strategy._calculate_grid_levels()
        
        assert len(levels) == 20  # 10 buy + 10 sell
        
        # Check buy levels (below current price)
        buy_levels = [l for l in levels if l['side'] == 'buy']
        assert len(buy_levels) == 10
        for level in buy_levels:
            assert level['price'] < strategy.current_price
        
        # Check sell levels (above current price)
        sell_levels = [l for l in levels if l['side'] == 'sell']
        assert len(sell_levels) == 10
        for level in sell_levels:
            assert level['price'] > strategy.current_price
    
    def test_grid_spacing(self, grid_strategy_config, market_data):
        """Test grid spacing is correct."""
        strategy = GridTradingStrategy(grid_strategy_config)
        bot = Mock()
        strategy.initialize(bot)
        strategy.current_price = market_data['last']
        
        levels = strategy._calculate_grid_levels()
        
        # Check first buy level
        first_buy = [l for l in levels if l['side'] == 'buy'][0]
        expected_price = strategy.current_price * (1 - strategy.grid_spacing / 100)
        assert abs(first_buy['price'] - expected_price) < 0.01
        
        # Check first sell level
        first_sell = [l for l in levels if l['side'] == 'sell'][0]
        expected_price = strategy.current_price * (1 + strategy.grid_spacing / 100)
        assert abs(first_sell['price'] - expected_price) < 0.01
    
    def test_on_order_filled_buy(self, grid_strategy_config, market_data):
        """Test order filled event for buy order."""
        strategy = GridTradingStrategy(grid_strategy_config)
        bot = Mock()
        strategy.initialize(bot)
        
        # Place initial grid
        strategy.analyze(market_data)
        initial_count = len(strategy.grid_orders)
        
        # Simulate buy order fill
        order = {
            'id': 'test_123',
            'side': 'buy',
            'price': 67000.0,
            'amount': 0.01,
            'status': 'closed'
        }
        
        strategy.on_order_filled(order)
        
        # Should have removed the filled order and added a sell order
        assert len(strategy.grid_orders) == initial_count
        
        # Check that a sell order was added above the buy price
        sell_orders = [o for o in strategy.grid_orders if o['side'] == 'sell']
        expected_sell_price = order['price'] * (1 + strategy.grid_spacing / 100)
        sell_at_expected_price = any(
            abs(o['price'] - expected_sell_price) < 0.01 
            for o in sell_orders
        )
        assert sell_at_expected_price
    
    def test_on_order_filled_sell(self, grid_strategy_config, market_data):
        """Test order filled event for sell order."""
        strategy = GridTradingStrategy(grid_strategy_config)
        bot = Mock()
        strategy.initialize(bot)
        
        # Place initial grid
        strategy.analyze(market_data)
        initial_count = len(strategy.grid_orders)
        
        # Simulate sell order fill
        order = {
            'id': 'test_456',
            'side': 'sell',
            'price': 68000.0,
            'amount': 0.01,
            'status': 'closed'
        }
        
        strategy.on_order_filled(order)
        
        # Should have removed the filled order and added a buy order
        assert len(strategy.grid_orders) == initial_count
        
        # Check that a buy order was added below the sell price
        buy_orders = [o for o in strategy.grid_orders if o['side'] == 'buy']
        expected_buy_price = order['price'] * (1 - strategy.grid_spacing / 100)
        buy_at_expected_price = any(
            abs(o['price'] - expected_buy_price) < 0.01 
            for o in buy_orders
        )
        assert buy_at_expected_price
    
    def test_on_order_cancelled(self, grid_strategy_config, market_data):
        """Test order cancelled event."""
        strategy = GridTradingStrategy(grid_strategy_config)
        bot = Mock()
        strategy.initialize(bot)
        
        # Place initial grid
        strategy.analyze(market_data)
        initial_count = len(strategy.grid_orders)
        
        # Get first order
        first_order = strategy.grid_orders[0]
        
        # Simulate order cancellation
        order = {
            'id': 'test_789',
            'side': first_order['side'],
            'price': first_order['price'],
            'amount': first_order['amount']
        }
        
        strategy.on_order_cancelled(order)
        
        # Should have removed the cancelled order
        assert len(strategy.grid_orders) == initial_count - 1
    
    def test_get_state(self, grid_strategy_config, market_data):
        """Test get_state method."""
        strategy = GridTradingStrategy(grid_strategy_config)
        bot = Mock()
        strategy.initialize(bot)
        
        # Place grid
        strategy.analyze(market_data)
        
        # Get state
        state = strategy.get_state()
        
        assert 'grid_orders' in state
        assert 'current_price' in state
        assert len(state['grid_orders']) == 20
        assert state['current_price'] == market_data['last']
    
    def test_restore_state(self, grid_strategy_config):
        """Test restore_state method."""
        strategy = GridTradingStrategy(grid_strategy_config)
        bot = Mock()
        strategy.initialize(bot)
        
        # Create state
        state = {
            'grid_orders': [
                {'price': 67000.0, 'side': 'buy', 'amount': 0.01},
                {'price': 68000.0, 'side': 'sell', 'amount': 0.01}
            ],
            'current_price': 67500.0
        }
        
        # Restore state
        strategy.restore_state(state)
        
        assert len(strategy.grid_orders) == 2
        assert strategy.current_price == 67500.0
    
    def test_custom_parameters(self):
        """Test strategy with custom parameters."""
        config = {
            'name': 'grid_trading',
            'params': {
                'grid_spacing': 5.0,  # 5% spacing
                'grid_levels': 5,     # 5 levels
                'position_size': 200  # $200 per level
            }
        }
        
        strategy = GridTradingStrategy(config)
        
        assert strategy.grid_spacing == 5.0
        assert strategy.grid_levels == 5
        assert strategy.position_size == 200

