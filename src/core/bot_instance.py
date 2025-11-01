"""
Bot Instance - Individual Trading Bot

Each BotInstance represents a single trading bot with its own:
- Exchange connection
- Trading strategy
- Configuration
- State

Multiple BotInstances can run simultaneously in the GUI.
"""

import time
import uuid
import threading
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from utils.logger import get_logger
from security.secret_provider import get_secret_provider
from plugins.exchanges.ccxt_exchange import CCXTExchange
from plugins.strategies.grid_trading import GridTradingStrategy
from plugins.strategies.dca import DCAStrategy

logger = get_logger(__name__)


class BotInstance:
    """
    Individual bot instance that can run independently.
    
    In CLI mode: Only one instance runs
    In GUI mode: Multiple instances can run simultaneously
    """
    
    def __init__(self, config: Dict[str, Any], bot_id: Optional[str] = None):
        """
        Initialize bot instance.
        
        Args:
            config: Bot configuration
            bot_id: Unique bot ID (auto-generated if not provided)
        """
        self.bot_id = bot_id or str(uuid.uuid4())
        self.config = config
        self.name = config.get('name', f"Bot-{self.bot_id[:8]}")
        
        # Bot state
        self.running = False
        self.paused = False
        self.thread = None
        self.created_at = datetime.now()
        self.started_at = None
        
        # Trading configuration
        self.paper_trading = config.get('paper_trading', False)
        self.symbol = config.get('symbol', 'BTC/USD')
        self.exchange_id = config.get('exchange', 'binance_us')
        self.strategy_name = config.get('strategy', 'grid_trading')
        
        # Components
        self.secret_provider = get_secret_provider()
        self.exchange = None
        self.strategy = None
        
        # Statistics
        self.stats = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_profit': 0.0,
            'current_position': 0.0,
            'last_price': 0.0,
            'last_update': None
        }
        
        # Callbacks for GUI updates
        self.on_status_update = None
        self.on_trade_executed = None
        self.on_error = None
        
        logger.info(f"[{self.name}] Bot instance created")
        logger.info(f"  ID: {self.bot_id}")
        logger.info(f"  Exchange: {self.exchange_id}")
        logger.info(f"  Symbol: {self.symbol}")
        logger.info(f"  Strategy: {self.strategy_name}")
        logger.info(f"  Paper trading: {self.paper_trading}")
    
    def initialize(self):
        """
        Initialize bot components (exchange, strategy).
        Call this before starting the bot.
        """
        logger.info(f"[{self.name}] Initializing components...")
        
        try:
            # Initialize exchange
            self.exchange = self._init_exchange()
            
            # Initialize strategy
            self.strategy = self._init_strategy()
            
            logger.info(f"[{self.name}] ✓ Initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"[{self.name}] Failed to initialize: {e}")
            if self.on_error:
                self.on_error(self.bot_id, str(e))
            return False
    
    def _init_exchange(self) -> CCXTExchange:
        """Initialize exchange connector."""
        logger.info(f"[{self.name}] Connecting to {self.exchange_id}...")
        
        exchange_config = {
            'exchange': self.exchange_id,
            'paper_trading': self.paper_trading
        }
        
        exchange = CCXTExchange(exchange_config, self.secret_provider)
        
        # Store API credentials if provided
        if 'api_key' in self.config and 'api_secret' in self.config:
            self.secret_provider.store_key(
                self.exchange_id,
                self.config['api_key'],
                self.config['api_secret']
            )
        
        # Connect
        exchange.connect()
        
        return exchange
    
    def _init_strategy(self):
        """Initialize trading strategy."""
        logger.info(f"[{self.name}] Loading {self.strategy_name} strategy...")
        
        strategy_params = self.config.get('strategy_params', {})
        
        strategy_config = {
            'name': self.strategy_name,
            'params': strategy_params
        }
        
        # Create strategy instance
        if self.strategy_name == 'grid_trading':
            strategy = GridTradingStrategy(strategy_config)
        elif self.strategy_name == 'dca':
            strategy = DCAStrategy(strategy_config)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy_name}")
        
        # Initialize with bot instance
        strategy.initialize(self)
        
        return strategy
    
    def start(self):
        """
        Start the bot in a separate thread.
        """
        if self.running:
            logger.warning(f"[{self.name}] Already running")
            return
        
        if not self.exchange or not self.strategy:
            logger.error(f"[{self.name}] Not initialized. Call initialize() first.")
            return
        
        logger.info(f"[{self.name}] Starting bot...")
        
        self.running = True
        self.started_at = datetime.now()
        
        # Start in separate thread
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        
        logger.info(f"[{self.name}] ✓ Bot started")
        
        if self.on_status_update:
            self.on_status_update(self.bot_id, 'running')
    
    def stop(self):
        """
        Stop the bot gracefully.
        """
        logger.info(f"[{self.name}] Stopping bot...")
        
        self.running = False
        
        # Wait for thread to finish
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        
        # Save state
        if self.strategy:
            state = self.strategy.get_state()
            logger.info(f"[{self.name}] Strategy state: {state}")
        
        # Disconnect
        if self.exchange:
            self.exchange.disconnect()
        
        logger.info(f"[{self.name}] ✓ Bot stopped")
        
        if self.on_status_update:
            self.on_status_update(self.bot_id, 'stopped')
    
    def pause(self):
        """Pause the bot (stop trading but keep connection)."""
        logger.info(f"[{self.name}] Pausing bot...")
        self.paused = True
        
        if self.on_status_update:
            self.on_status_update(self.bot_id, 'paused')
    
    def resume(self):
        """Resume the bot."""
        logger.info(f"[{self.name}] Resuming bot...")
        self.paused = False
        
        if self.on_status_update:
            self.on_status_update(self.bot_id, 'running')
    
    def _run_loop(self):
        """
        Main trading loop (runs in separate thread).
        """
        iteration = 0
        check_interval = self.config.get('check_interval', 60)
        
        logger.info(f"[{self.name}] Trading loop started")
        
        if self.paper_trading:
            logger.warning(f"[{self.name}] ⚠️  PAPER TRADING MODE")
        
        while self.running:
            try:
                if self.paused:
                    time.sleep(1)
                    continue
                
                iteration += 1
                
                logger.info(f"[{self.name}] Iteration #{iteration}")
                
                # Get market data
                market_data = self.exchange.get_market_data(self.symbol)
                
                # Update stats
                self.stats['last_price'] = market_data.get('last', 0)
                self.stats['last_update'] = datetime.now()
                
                # Run strategy
                signal = self.strategy.analyze(market_data)
                
                # Execute signal
                if signal['action'] == 'buy':
                    self._execute_buy(signal)
                elif signal['action'] == 'sell':
                    self._execute_sell(signal)
                else:
                    logger.info(f"[{self.name}] {signal['reason']}")
                
                # Sleep
                time.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"[{self.name}] Error in trading loop: {e}", exc_info=True)
                
                if self.on_error:
                    self.on_error(self.bot_id, str(e))
                
                time.sleep(10)
        
        logger.info(f"[{self.name}] Trading loop stopped")
    
    def _execute_buy(self, signal: Dict[str, Any]):
        """Execute buy order."""
        metadata = signal.get('metadata', {})
        price = metadata.get('price')
        amount = metadata.get('amount')
        
        if not price or not amount:
            return
        
        try:
            order = self.exchange.place_order(
                symbol=self.symbol,
                side='buy',
                amount=amount,
                price=price,
                order_type='limit'
            )
            
            logger.info(f"[{self.name}] ✓ Buy order: {order.get('id')}")
            
            # Update stats
            self.stats['total_trades'] += 1
            
            # Notify strategy
            if order.get('status') == 'closed':
                self.strategy.on_order_filled(order)
            
            # Notify GUI
            if self.on_trade_executed:
                self.on_trade_executed(self.bot_id, order)
            
        except Exception as e:
            logger.error(f"[{self.name}] Buy order failed: {e}")
    
    def _execute_sell(self, signal: Dict[str, Any]):
        """Execute sell order."""
        metadata = signal.get('metadata', {})
        price = metadata.get('price')
        amount = metadata.get('amount')
        
        if not price or not amount:
            return
        
        try:
            order = self.exchange.place_order(
                symbol=self.symbol,
                side='sell',
                amount=amount,
                price=price,
                order_type='limit'
            )
            
            logger.info(f"[{self.name}] ✓ Sell order: {order.get('id')}")
            
            # Update stats
            self.stats['total_trades'] += 1
            
            # Notify strategy
            if order.get('status') == 'closed':
                self.strategy.on_order_filled(order)
            
            # Notify GUI
            if self.on_trade_executed:
                self.on_trade_executed(self.bot_id, order)
            
        except Exception as e:
            logger.error(f"[{self.name}] Sell order failed: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current bot status for GUI display.
        
        Returns:
            Status dictionary
        """
        return {
            'bot_id': self.bot_id,
            'name': self.name,
            'exchange': self.exchange_id,
            'symbol': self.symbol,
            'strategy': self.strategy_name,
            'running': self.running,
            'paused': self.paused,
            'paper_trading': self.paper_trading,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'stats': self.stats
        }

