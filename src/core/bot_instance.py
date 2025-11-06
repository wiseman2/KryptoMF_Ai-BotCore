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
import json
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from utils.logger import get_logger
from security.secret_provider import get_secret_provider
from plugins.exchanges.ccxt_exchange import CCXTExchange
from plugins.strategies import get_strategy_class

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

        # State persistence
        state_dir = Path(config.get('state_dir', 'data'))
        state_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = state_dir / f"bot_state_{self.bot_id}.json"
        self.auto_save = config.get('auto_save', True)
        self.save_interval = config.get('save_interval', 60)  # Seconds
        self.last_save_time = 0

        # Connectivity tracking
        self.connectivity_failures = 0
        self.max_connectivity_failures = config.get('max_connectivity_failures', 2)
        self.last_connectivity_check = 0
        self.connectivity_check_interval = config.get('connectivity_check_interval', 120)

        # Order tracking (to avoid notifying strategy multiple times for same order)
        self.notified_orders = set()  # Set of order IDs we've already notified strategy about

        logger.info(f"[{self.name}] Bot instance created")
        logger.info(f"  ID: {self.bot_id}")
        logger.info(f"  Exchange: {self.exchange_id}")
        logger.info(f"  Symbol: {self.symbol}")
        logger.info(f"  Strategy: {self.strategy_name}")
        logger.info(f"  Paper trading: {self.paper_trading}")
        logger.info(f"  State file: {self.state_file}")
    
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

            # Restore state if exists
            self._load_state()

            logger.info(f"[{self.name}] ✓ Initialization complete")
            return True

        except Exception as e:
            logger.error(f"[{self.name}] Failed to initialize: {e}")
            if self.on_error:
                self.on_error(self.bot_id, str(e))
            return False

    def _save_state(self):
        """Save bot state to disk."""
        try:
            if not self.strategy:
                return

            # Convert stats to JSON-serializable format
            stats_copy = self.stats.copy()
            if 'last_update' in stats_copy and isinstance(stats_copy['last_update'], datetime):
                stats_copy['last_update'] = stats_copy['last_update'].isoformat()

            state = {
                'bot_id': self.bot_id,
                'name': self.name,
                'symbol': self.symbol,
                'exchange': self.exchange_id,
                'strategy': self.strategy_name,
                'last_update': datetime.now().isoformat(),
                'stats': stats_copy,
                'strategy_state': self.strategy.get_state(),
                'connectivity': {
                    'last_success': datetime.now().isoformat() if self.connectivity_failures == 0 else None,
                    'failure_count': self.connectivity_failures
                }
            }

            # Write to temp file first, then rename (atomic operation)
            temp_file = self.state_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(state, f, indent=2)

            temp_file.replace(self.state_file)
            self.last_save_time = time.time()

            logger.debug(f"[{self.name}] State saved to {self.state_file}")

        except Exception as e:
            logger.error(f"[{self.name}] Failed to save state: {e}")

    def _load_state(self):
        """Load bot state from disk."""
        try:
            if not self.state_file.exists():
                logger.info(f"[{self.name}] No saved state found")
                return

            with open(self.state_file, 'r') as f:
                state = json.load(f)

            # Restore strategy state
            if self.strategy and 'strategy_state' in state:
                self.strategy.restore_state(state['strategy_state'])
                logger.info(f"[{self.name}] Strategy state restored")

            # Restore stats
            if 'stats' in state:
                self.stats.update(state['stats'])
                logger.info(f"[{self.name}] Stats restored")

            # Restore connectivity info
            if 'connectivity' in state:
                self.connectivity_failures = state['connectivity'].get('failure_count', 0)

            logger.info(f"[{self.name}] ✓ State loaded from {self.state_file}")

        except Exception as e:
            logger.error(f"[{self.name}] Failed to load state: {e}")

    def _auto_save_if_needed(self):
        """Auto-save state if interval has passed."""
        if not self.auto_save:
            return

        current_time = time.time()
        if current_time - self.last_save_time >= self.save_interval:
            self._save_state()

    def _check_connectivity(self) -> bool:
        """
        Check internet connectivity by pinging a reliable public endpoint.

        Uses Google DNS (8.8.8.8) for a simple connectivity check that doesn't
        require API keys or authentication.

        Returns:
            True if connected, False otherwise
        """
        try:
            import socket

            # Simple connectivity check - ping Google DNS
            # This works for both live trading and paper trading
            socket.create_connection(("8.8.8.8", 53), timeout=3)

            # Reset failure counter on success
            if self.connectivity_failures > 0:
                logger.info(f"[{self.name}] ✓ Connectivity restored after {self.connectivity_failures} failures")
                self.connectivity_failures = 0

            return True

        except (socket.error, socket.timeout) as e:
            # Increment failure counter
            self.connectivity_failures += 1
            logger.warning(f"[{self.name}] ⚠️  No internet connection (failure #{self.connectivity_failures})")

            # Reset trailing state after max failures
            if self.connectivity_failures >= self.max_connectivity_failures:
                self._reset_trailing_state()

            # Wait before retrying with exponential backoff
            backoff_time = min(30 * self.connectivity_failures, 300)  # Max 5 minutes
            logger.info(f"[{self.name}] Waiting {backoff_time}s before retry...")
            time.sleep(backoff_time)

            return False

        except Exception as e:
            logger.error(f"[{self.name}] Connectivity check error: {e}")

            # Reset trailing state after max failures
            if self.connectivity_failures >= self.max_connectivity_failures:
                self._reset_trailing_state()

            return False

    def _reset_trailing_state(self):
        """Reset trailing state after connectivity loss."""
        logger.warning(f"[{self.name}] Resetting trailing state due to {self.connectivity_failures} connectivity failures")

        # Call strategy's reset_trailing method if available
        if self.strategy and hasattr(self.strategy, 'reset_trailing'):
            self.strategy.reset_trailing()

        # Save state after reset
        self._save_state()
    
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
            passphrase = self.config.get('passphrase')  # May be None
            self.secret_provider.store_key(
                self.exchange_id,
                self.config['api_key'],
                self.config['api_secret'],
                passphrase
            )
        
        # Connect
        exchange.connect()
        
        return exchange
    
    def _init_strategy(self):
        """
        Initialize trading strategy using auto-discovery.

        Strategies are automatically discovered from the plugins/strategies directory.
        No manual registration required - just add a new .py file with a StrategyPlugin subclass.
        """
        logger.info(f"[{self.name}] Loading {self.strategy_name} strategy...")

        strategy_params = self.config.get('strategy_params', {})

        strategy_config = {
            'name': self.strategy_name,
            'params': strategy_params
        }

        # Get strategy class using auto-discovery
        strategy_class = get_strategy_class(self.strategy_name)
        strategy = strategy_class(strategy_config)

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

        # Save final state to disk
        self._save_state()
        logger.info(f"[{self.name}] Final state saved")

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

                # Check connectivity periodically
                current_time = time.time()
                if current_time - self.last_connectivity_check >= self.connectivity_check_interval:
                    if not self._check_connectivity():
                        # Connectivity failed, skip this iteration
                        continue
                    self.last_connectivity_check = current_time

                # Get market data
                market_data = self.exchange.get_market_data(self.symbol)

                # Update stats
                self.stats['last_price'] = market_data.get('last', 0)
                self.stats['last_update'] = datetime.now()

                # Reset connectivity failures on successful data fetch
                if self.connectivity_failures > 0:
                    logger.info(f"[{self.name}] ✓ Connectivity restored")
                    self.connectivity_failures = 0

                # Check for filled orders (limit orders that weren't immediately filled)
                self._check_filled_orders()

                # Run strategy
                signal = self.strategy.analyze(market_data)

                # Execute signal
                if signal['action'] == 'buy':
                    self._execute_buy(signal)
                elif signal['action'] == 'sell':
                    self._execute_sell(signal)
                else:
                    logger.info(f"[{self.name}] {signal['reason']}")

                # Auto-save state if needed
                self._auto_save_if_needed()

                # Sleep
                time.sleep(check_interval)

            except Exception as e:
                logger.error(f"[{self.name}] Error in trading loop: {e}", exc_info=True)

                # Increment connectivity failures
                self.connectivity_failures += 1

                if self.on_error:
                    self.on_error(self.bot_id, str(e))

                # Exponential backoff
                backoff_time = min(10 * (2 ** min(self.connectivity_failures - 1, 4)), 300)  # Max 5 minutes
                logger.warning(f"[{self.name}] Waiting {backoff_time}s before retry (failure #{self.connectivity_failures})")
                time.sleep(backoff_time)
        
        logger.info(f"[{self.name}] Trading loop stopped")

    def _check_filled_orders(self):
        """
        Check for filled orders and notify strategy.

        This handles limit orders that weren't immediately filled.
        """
        try:
            # Get all open orders
            open_orders = self.exchange.get_open_orders(self.symbol)

            if not open_orders:
                return

            # Check each order
            for order_id in list(open_orders.keys()):
                # Skip if we've already notified strategy about this order
                if order_id in self.notified_orders:
                    continue

                # Fetch order details
                order = self.exchange.get_order(order_id, self.symbol)

                if order and order.get('status') == 'closed':
                    logger.info(f"[{self.name}] Order {order_id} filled")

                    # Notify strategy
                    self.strategy.on_order_filled(order)

                    # Mark as notified
                    self.notified_orders.add(order_id)

                    # Update profit stats if it was a sell order
                    if order.get('side') == 'sell':
                        self._update_profit_stats()

                    # Save state after order fill
                    self._save_state()

        except Exception as e:
            logger.error(f"[{self.name}] Error checking filled orders: {e}")

    def _update_profit_stats(self):
        """Update profit statistics from strategy."""
        try:
            # Get profit from strategy if available
            if hasattr(self.strategy, 'total_profit'):
                self.stats['total_profit'] = self.strategy.total_profit

            # Get win/loss counts if available
            if hasattr(self.strategy, 'winning_trades'):
                self.stats['winning_trades'] = self.strategy.winning_trades
            if hasattr(self.strategy, 'losing_trades'):
                self.stats['losing_trades'] = self.strategy.losing_trades

        except Exception as e:
            logger.error(f"[{self.name}] Error updating profit stats: {e}")

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

                # Mark as notified
                self.notified_orders.add(order.get('id'))

                # Save state immediately after purchase
                self._save_state()
                logger.info(f"[{self.name}] State saved after purchase")

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

                # Mark as notified
                self.notified_orders.add(order.get('id'))

                # Update profit stats from strategy
                self._update_profit_stats()

                # Save state immediately after sell
                self._save_state()
                logger.info(f"[{self.name}] State saved after sell")

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

