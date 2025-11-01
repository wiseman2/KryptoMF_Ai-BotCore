"""
Tests for BotInstance

Tests the core bot instance functionality.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from core.bot_instance import BotInstance


class TestBotInstance:
    """Test BotInstance class."""
    
    def test_bot_creation(self, bot_config):
        """Test bot instance creation."""
        bot = BotInstance(bot_config)
        
        assert bot.name == 'Test Bot'
        assert bot.exchange_id == 'binance_us'
        assert bot.symbol == 'BTC/USD'
        assert bot.strategy_name == 'grid_trading'
        assert bot.paper_trading is True
        assert bot.running is False
        assert bot.paused is False
    
    def test_bot_id_generation(self, bot_config):
        """Test bot ID is generated if not provided."""
        bot = BotInstance(bot_config)
        assert bot.bot_id is not None
        assert len(bot.bot_id) == 36  # UUID length
    
    def test_bot_id_custom(self, bot_config):
        """Test custom bot ID."""
        custom_id = 'my-custom-bot-id'
        bot = BotInstance(bot_config, bot_id=custom_id)
        assert bot.bot_id == custom_id
    
    @patch('core.bot_instance.CCXTExchange')
    @patch('core.bot_instance.GridTradingStrategy')
    @patch('core.bot_instance.get_secret_provider')
    def test_bot_initialization(self, mock_secret, mock_strategy, mock_exchange, bot_config):
        """Test bot initialization."""
        # Setup mocks
        mock_secret.return_value = Mock()
        mock_exchange_instance = Mock()
        mock_exchange.return_value = mock_exchange_instance
        mock_strategy_instance = Mock()
        mock_strategy.return_value = mock_strategy_instance
        
        # Create and initialize bot
        bot = BotInstance(bot_config)
        result = bot.initialize()
        
        assert result is True
        assert bot.exchange is not None
        assert bot.strategy is not None
        mock_exchange_instance.connect.assert_called_once()
        mock_strategy_instance.initialize.assert_called_once_with(bot)
    
    @patch('core.bot_instance.CCXTExchange')
    @patch('core.bot_instance.GridTradingStrategy')
    @patch('core.bot_instance.get_secret_provider')
    def test_bot_start_stop(self, mock_secret, mock_strategy, mock_exchange, bot_config):
        """Test bot start and stop."""
        # Setup mocks
        mock_secret.return_value = Mock()
        mock_exchange_instance = Mock()
        mock_exchange.return_value = mock_exchange_instance
        mock_strategy_instance = Mock()
        mock_strategy.return_value = mock_strategy_instance
        mock_strategy_instance.get_state.return_value = {}
        
        # Create and initialize bot
        bot = BotInstance(bot_config)
        bot.initialize()
        
        # Start bot
        bot.start()
        assert bot.running is True
        assert bot.thread is not None
        assert bot.thread.is_alive()
        
        # Stop bot
        time.sleep(0.1)  # Let it run briefly
        bot.stop()
        assert bot.running is False
        mock_exchange_instance.disconnect.assert_called_once()
    
    @patch('core.bot_instance.CCXTExchange')
    @patch('core.bot_instance.GridTradingStrategy')
    @patch('core.bot_instance.get_secret_provider')
    def test_bot_pause_resume(self, mock_secret, mock_strategy, mock_exchange, bot_config):
        """Test bot pause and resume."""
        # Setup mocks
        mock_secret.return_value = Mock()
        mock_exchange_instance = Mock()
        mock_exchange.return_value = mock_exchange_instance
        mock_strategy_instance = Mock()
        mock_strategy.return_value = mock_strategy_instance
        
        # Create and initialize bot
        bot = BotInstance(bot_config)
        bot.initialize()
        bot.start()
        
        # Pause bot
        bot.pause()
        assert bot.paused is True
        assert bot.running is True  # Still running, just paused
        
        # Resume bot
        bot.resume()
        assert bot.paused is False
        
        # Cleanup
        bot.stop()
    
    @patch('core.bot_instance.CCXTExchange')
    @patch('core.bot_instance.GridTradingStrategy')
    @patch('core.bot_instance.get_secret_provider')
    def test_bot_callbacks(self, mock_secret, mock_strategy, mock_exchange, bot_config):
        """Test bot callbacks."""
        # Setup mocks
        mock_secret.return_value = Mock()
        mock_exchange_instance = Mock()
        mock_exchange.return_value = mock_exchange_instance
        mock_strategy_instance = Mock()
        mock_strategy.return_value = mock_strategy_instance
        
        # Create callbacks
        status_callback = Mock()
        trade_callback = Mock()
        error_callback = Mock()
        
        # Create bot with callbacks
        bot = BotInstance(bot_config)
        bot.on_status_update = status_callback
        bot.on_trade_executed = trade_callback
        bot.on_error = error_callback
        
        bot.initialize()
        bot.start()
        
        # Verify status callback was called
        status_callback.assert_called_with(bot.bot_id, 'running')
        
        # Cleanup
        bot.stop()
    
    def test_bot_get_status(self, bot_config):
        """Test get_status method."""
        bot = BotInstance(bot_config)
        status = bot.get_status()
        
        assert status['bot_id'] == bot.bot_id
        assert status['name'] == 'Test Bot'
        assert status['exchange'] == 'binance_us'
        assert status['symbol'] == 'BTC/USD'
        assert status['strategy'] == 'grid_trading'
        assert status['running'] is False
        assert status['paused'] is False
        assert status['paper_trading'] is True
        assert 'stats' in status
        assert 'created_at' in status
    
    @patch('core.bot_instance.CCXTExchange')
    @patch('core.bot_instance.GridTradingStrategy')
    @patch('core.bot_instance.get_secret_provider')
    def test_execute_buy(self, mock_secret, mock_strategy, mock_exchange, bot_config):
        """Test buy order execution."""
        # Setup mocks
        mock_secret.return_value = Mock()
        mock_exchange_instance = Mock()
        mock_exchange.return_value = mock_exchange_instance
        mock_exchange_instance.place_order.return_value = {
            'id': 'test_order_123',
            'symbol': 'BTC/USD',
            'side': 'buy',
            'amount': 0.01,
            'price': 67450.0,
            'status': 'closed'
        }
        mock_strategy_instance = Mock()
        mock_strategy.return_value = mock_strategy_instance
        
        # Create bot
        bot = BotInstance(bot_config)
        bot.initialize()
        
        # Execute buy
        signal = {
            'action': 'buy',
            'metadata': {
                'price': 67450.0,
                'amount': 0.01
            }
        }
        bot._execute_buy(signal)
        
        # Verify order was placed
        mock_exchange_instance.place_order.assert_called_once_with(
            symbol='BTC/USD',
            side='buy',
            amount=0.01,
            price=67450.0,
            order_type='limit'
        )
        
        # Verify stats updated
        assert bot.stats['total_trades'] == 1
    
    @patch('core.bot_instance.CCXTExchange')
    @patch('core.bot_instance.GridTradingStrategy')
    @patch('core.bot_instance.get_secret_provider')
    def test_execute_sell(self, mock_secret, mock_strategy, mock_exchange, bot_config):
        """Test sell order execution."""
        # Setup mocks
        mock_secret.return_value = Mock()
        mock_exchange_instance = Mock()
        mock_exchange.return_value = mock_exchange_instance
        mock_exchange_instance.place_order.return_value = {
            'id': 'test_order_456',
            'symbol': 'BTC/USD',
            'side': 'sell',
            'amount': 0.01,
            'price': 68000.0,
            'status': 'closed'
        }
        mock_strategy_instance = Mock()
        mock_strategy.return_value = mock_strategy_instance
        
        # Create bot
        bot = BotInstance(bot_config)
        bot.initialize()
        
        # Execute sell
        signal = {
            'action': 'sell',
            'metadata': {
                'price': 68000.0,
                'amount': 0.01
            }
        }
        bot._execute_sell(signal)
        
        # Verify order was placed
        mock_exchange_instance.place_order.assert_called_once_with(
            symbol='BTC/USD',
            side='sell',
            amount=0.01,
            price=68000.0,
            order_type='limit'
        )
        
        # Verify stats updated
        assert bot.stats['total_trades'] == 1
    
    @patch('core.bot_instance.CCXTExchange')
    @patch('core.bot_instance.DCAStrategy')
    @patch('core.bot_instance.get_secret_provider')
    def test_dca_strategy_initialization(self, mock_secret, mock_strategy, mock_exchange, bot_config):
        """Test DCA strategy initialization."""
        # Modify config for DCA
        bot_config['strategy'] = 'dca'
        bot_config['strategy_params'] = {
            'interval_hours': 24,
            'amount_usd': 100
        }
        
        # Setup mocks
        mock_secret.return_value = Mock()
        mock_exchange_instance = Mock()
        mock_exchange.return_value = mock_exchange_instance
        mock_strategy_instance = Mock()
        mock_strategy.return_value = mock_strategy_instance
        
        # Create and initialize bot
        bot = BotInstance(bot_config)
        result = bot.initialize()
        
        assert result is True
        mock_strategy.assert_called_once()
        mock_strategy_instance.initialize.assert_called_once_with(bot)

