"""
Bot Engine - DEPRECATED

This module is deprecated. Use bot_instance.py instead.

Kept for backwards compatibility.
"""

import warnings
from core.bot_instance import BotInstance

warnings.warn(
    "bot_engine.py is deprecated. Use bot_instance.py instead.",
    DeprecationWarning,
    stacklevel=2
)


# Alias for backwards compatibility
BotEngine = BotInstance


class _DeprecatedBotEngine:
    """
    Main bot engine that coordinates all trading activities.

    This is the heart of the open source bot - it manages:
    - Exchange connections
    - Strategy execution
    - Order management
    - Risk management
    - Event handling
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the bot engine.

        Args:
            config: Bot configuration dictionary
        """
        self.config = config
        self.running = False
        self.paper_trading = config.get('paper_trading', False)
        self.symbol = config.get('symbol', 'BTC/USD')

        logger.info("Initializing bot engine...")
        logger.info(f"Exchange: {config.get('exchange')}")
        logger.info(f"Symbol: {self.symbol}")
        logger.info(f"Strategy: {config.get('strategy')}")
        logger.info(f"Paper trading: {self.paper_trading}")

        # Initialize components
        self.secret_provider = get_secret_provider()
        self.exchange = self._init_exchange()
        self.strategy = self._init_strategy()

        logger.info("✓ Bot engine initialized")

    def _init_exchange(self) -> CCXTExchange:
        """Initialize exchange connector."""
        logger.info("Initializing exchange connector...")

        exchange_config = {
            'exchange': self.config.get('exchange'),
            'paper_trading': self.paper_trading
        }

        exchange = CCXTExchange(exchange_config, self.secret_provider)

        # Store API credentials if provided in config
        if 'api_key' in self.config and 'api_secret' in self.config:
            logger.info("Storing API credentials in secure keychain...")
            self.secret_provider.store_key(
                self.config.get('exchange'),
                self.config['api_key'],
                self.config['api_secret']
            )

        # Connect to exchange
        exchange.connect()

        return exchange

    def _init_strategy(self):
        """Initialize trading strategy."""
        logger.info("Initializing trading strategy...")

        strategy_name = self.config.get('strategy', 'grid_trading')
        strategy_params = self.config.get('strategy_params', {})

        strategy_config = {
            'name': strategy_name,
            'params': strategy_params
        }

        # Create strategy instance
        if strategy_name == 'grid_trading':
            strategy = GridTradingStrategy(strategy_config)
        elif strategy_name == 'dca':
            strategy = DCAStrategy(strategy_config)
        else:
            raise ValueError(f"Unknown strategy: {strategy_name}")

        # Initialize strategy with bot instance
        strategy.initialize(self)

        return strategy
    
    def run(self):
        """
        Start the bot and run the main trading loop.
        """
        self.running = True
        logger.info("=" * 60)
        logger.info("Bot started successfully!")
        logger.info("=" * 60)
        
        if self.paper_trading:
            logger.warning("⚠️  PAPER TRADING MODE - No real orders will be placed")
        
        try:
            self._main_loop()
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
            self.stop()
    
    def _main_loop(self):
        """
        Main trading loop.
        """
        iteration = 0
        check_interval = 60  # Check every 60 seconds

        while self.running:
            iteration += 1

            try:
                logger.info("")
                logger.info("=" * 60)
                logger.info(f"Iteration #{iteration}")
                logger.info("=" * 60)

                # Get current market data
                market_data = self.exchange.get_market_data(self.symbol)

                # Run strategy analysis
                signal = self.strategy.analyze(market_data)

                # Handle signal
                if signal['action'] == 'buy':
                    self._execute_buy(signal)
                elif signal['action'] == 'sell':
                    self._execute_sell(signal)
                else:
                    logger.info(f"Signal: {signal['reason']}")

                # Check open orders
                open_orders = self.exchange.get_open_orders(self.symbol)
                if open_orders:
                    logger.info(f"Open orders: {len(open_orders)}")

                # Sleep until next iteration
                logger.info(f"Next check in {check_interval} seconds...")
                time.sleep(check_interval)

            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                time.sleep(10)

    def _execute_buy(self, signal: Dict[str, Any]):
        """
        Execute buy order based on signal.

        Args:
            signal: Buy signal from strategy
        """
        logger.info("=" * 60)
        logger.info("EXECUTING BUY ORDER")
        logger.info("=" * 60)

        metadata = signal.get('metadata', {})
        price = metadata.get('price')
        amount = metadata.get('amount')

        if not price or not amount:
            logger.error("Invalid buy signal - missing price or amount")
            return

        try:
            order = self.exchange.place_order(
                symbol=self.symbol,
                side='buy',
                amount=amount,
                price=price,
                order_type='limit'
            )

            logger.info(f"✓ Buy order placed: {order.get('id')}")

            # Notify strategy
            if order.get('status') == 'closed':
                self.strategy.on_order_filled(order)

        except Exception as e:
            logger.error(f"Failed to execute buy order: {e}")

    def _execute_sell(self, signal: Dict[str, Any]):
        """
        Execute sell order based on signal.

        Args:
            signal: Sell signal from strategy
        """
        logger.info("=" * 60)
        logger.info("EXECUTING SELL ORDER")
        logger.info("=" * 60)

        metadata = signal.get('metadata', {})
        price = metadata.get('price')
        amount = metadata.get('amount')

        if not price or not amount:
            logger.error("Invalid sell signal - missing price or amount")
            return

        try:
            order = self.exchange.place_order(
                symbol=self.symbol,
                side='sell',
                amount=amount,
                price=price,
                order_type='limit'
            )

            logger.info(f"✓ Sell order placed: {order.get('id')}")

            # Notify strategy
            if order.get('status') == 'closed':
                self.strategy.on_order_filled(order)

        except Exception as e:
            logger.error(f"Failed to execute sell order: {e}")
    
    def stop(self):
        """
        Stop the bot gracefully.
        """
        logger.info("Stopping bot...")
        self.running = False

        # Save strategy state
        if self.strategy:
            state = self.strategy.get_state()
            logger.info(f"Strategy state: {state}")

        # Disconnect from exchange
        if self.exchange:
            self.exchange.disconnect()

        logger.info("Bot stopped")
    
    def run_backtest(self):
        """
        Run backtest mode.
        """
        logger.info("=" * 60)
        logger.info("Backtest Mode")
        logger.info("=" * 60)
        
        # TODO: Implement backtesting
        logger.warning("Backtesting not yet implemented")

