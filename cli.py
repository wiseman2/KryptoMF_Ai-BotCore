#!/usr/bin/env python3
"""
KryptoMF Bot Core - CLI Entry Point

This is the main entry point for the open source CLI bot.
Run this file to start the bot from your code editor.
"""

import argparse
import sys
from pathlib import Path

# Add src to path so we can import from it
src_path = Path(__file__).parent / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Now import from src modules (without src. prefix since we added src to path)
from core.bot_instance import BotInstance
from core.config_manager import ConfigManager
from cli.status_display import StatusDisplay
from cli.bot_controller import run_interactive_mode
from backtesting.backtest_engine import BacktestEngine
from backtesting.backtest_results import BacktestResults
from backtesting.historical_data import HistoricalDataFetcher
from utils.logger import setup_logger


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='KryptoMF Bot Core - Open Source Trading Bot'
    )
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file (YAML/JSON)'
    )
    parser.add_argument(
        '--paper-trading',
        action='store_true',
        help='Run in paper trading mode (no real orders)'
    )
    parser.add_argument(
        '--backtest',
        action='store_true',
        help='Run backtest mode'
    )
    parser.add_argument(
        '--backtest-data',
        type=str,
        help='Path to historical data CSV for backtesting'
    )
    parser.add_argument(
        '--backtest-start',
        type=str,
        help='Backtest start date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--backtest-end',
        type=str,
        help='Backtest end date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--no-interactive',
        action='store_true',
        help='Disable interactive mode (no status display or keyboard controls)'
    )

    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logger(verbose=args.verbose)
    
    print("=" * 60)
    print("KryptoMF Bot Core - Open Source Trading Bot")
    print("=" * 60)
    print()
    
    # Load or create configuration
    config_manager = ConfigManager()

    if args.config:
        logger.info(f"Loading configuration from {args.config}")
        # Show main menu with specified config file
        config = config_manager.main_menu(config_path=args.config)
    else:
        logger.info("No configuration file specified")
        # Show main menu (will check for default config)
        config = config_manager.main_menu()

    # Override with CLI flags
    if args.paper_trading:
        config['paper_trading'] = True
        logger.info("Paper trading mode enabled")

    # Check if user selected backtest mode from menu
    run_backtest = args.backtest or config.get('_mode') == 'backtest'

    # Remove internal _mode flag before passing to bot
    config.pop('_mode', None)

    # Create bot instance
    bot = BotInstance(config)

    # Initialize bot components
    logger.info("Initializing bot components...")
    if not bot.initialize():
        logger.error("Failed to initialize bot")
        sys.exit(1)

    try:
        if run_backtest:
            logger.info("Starting backtest...")

            # Get backtest parameters (interactive or from args)
            if args.backtest_data:
                # Manual CSV file provided
                import pandas as pd
                logger.info(f"Loading data from {args.backtest_data}")
                historical_data = pd.read_csv(args.backtest_data)

                # Use symbol from config or args
                symbol = config.get('symbol', 'BTC/USD')
                start_date = args.backtest_start or 'unknown'
                end_date = args.backtest_end or 'unknown'
                timeframe = 'unknown'

            else:
                # Interactive setup or use args
                if args.backtest_start and args.backtest_end:
                    # Use command-line args
                    symbol = config.get('symbol', 'BTC/USD')
                    timeframe = '1h'  # Default
                    start_date = args.backtest_start
                    end_date = args.backtest_end
                else:
                    # Interactive setup
                    backtest_params = HistoricalDataFetcher.interactive_setup()

                    if backtest_params is None:
                        logger.info("Backtest cancelled")
                        sys.exit(0)

                    symbol = backtest_params['symbol']
                    timeframe = backtest_params['timeframe']
                    start_date = backtest_params['start_date']
                    end_date = backtest_params['end_date']

                # Fetch historical data from exchange
                exchange_id = config.get('exchange', 'binance')

                # Map exchange names to ccxt IDs
                exchange_map = {
                    'binance_us': 'binanceus',
                    'coinbase': 'coinbasepro',
                    'coinbase_pro': 'coinbasepro'
                }
                ccxt_exchange_id = exchange_map.get(exchange_id, exchange_id)

                try:
                    fetcher = HistoricalDataFetcher(ccxt_exchange_id)
                    historical_data = fetcher.fetch_ohlcv(symbol, timeframe, start_date, end_date)
                except Exception as e:
                    logger.error(f"Failed to fetch historical data: {e}")
                    logger.info("You can provide a CSV file with --backtest-data instead")
                    sys.exit(1)

            # Interactive backtest parameter setup
            from colorama import Fore, Style

            print()
            print("=" * 70)
            print(f"{Fore.CYAN}{'BACKTEST PARAMETERS':^70}{Style.RESET_ALL}")
            print("=" * 70)

            # Get defaults from config
            risk_config = config.get('risk', {})
            default_balance = risk_config.get('max_position_size') or risk_config.get('initial_balance', 10000.0)

            strategy_params = config.get('strategy_params', {})
            default_amount = strategy_params.get('amount_usd', 100)
            default_profit = strategy_params.get('min_profit_percent', 0.5)

            # Ask for initial balance
            print(f"\n{Fore.GREEN}Initial Balance{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Default: ${default_balance:,.2f}{Style.RESET_ALL}")
            balance_input = input(f"{Fore.CYAN}Enter initial balance (or press Enter for default):{Style.RESET_ALL} ").strip()
            initial_balance = float(balance_input) if balance_input else default_balance

            # Ask for amount per trade
            print(f"\n{Fore.GREEN}Amount Per Trade{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Default: ${default_amount:,.2f}{Style.RESET_ALL}")
            amount_input = input(f"{Fore.CYAN}Enter amount per trade (or press Enter for default):{Style.RESET_ALL} ").strip()
            amount_usd = float(amount_input) if amount_input else default_amount

            # Ask for profit percentage
            print(f"\n{Fore.GREEN}Minimum Profit Percentage{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Default: {default_profit}%{Style.RESET_ALL}")
            profit_input = input(f"{Fore.CYAN}Enter minimum profit % (or press Enter for default):{Style.RESET_ALL} ").strip()
            min_profit_percent = float(profit_input) if profit_input else default_profit

            # Update strategy params with backtest values
            backtest_strategy_params = strategy_params.copy()
            backtest_strategy_params['amount_usd'] = amount_usd
            backtest_strategy_params['min_profit_percent'] = min_profit_percent

            # Show summary
            print()
            print("=" * 70)
            print(f"{Fore.GREEN}{'BACKTEST CONFIGURATION':^70}{Style.RESET_ALL}")
            print("=" * 70)
            print(f"Initial Balance:      {Fore.CYAN}${initial_balance:,.2f}{Style.RESET_ALL}")
            print(f"Amount Per Trade:     {Fore.CYAN}${amount_usd:,.2f}{Style.RESET_ALL}")
            print(f"Min Profit %:         {Fore.CYAN}{min_profit_percent}%{Style.RESET_ALL}")
            print("=" * 70)
            print()

            backtest_config = {
                'symbol': symbol,
                'start_date': start_date,
                'end_date': end_date,
                'initial_balance': initial_balance,
                'strategy': config.get('strategy'),
                'strategy_params': backtest_strategy_params
            }

            # Create backtest engine
            backtest = BacktestEngine(backtest_config)

            # Set strategy using auto-discovery
            from plugins.strategies import get_strategy_class

            strategy_name = config.get('strategy', 'grid_trading')
            strategy_params = config.get('strategy_params', {})

            try:
                strategy_class = get_strategy_class(strategy_name)
                strategy = strategy_class({'name': strategy_name, 'params': strategy_params})
            except ValueError as e:
                logger.error(str(e))
                sys.exit(1)

            backtest.set_strategy(strategy)

            # Run backtest
            results = backtest.run(historical_data)

            # Display results
            BacktestResults.display_summary(results)
            BacktestResults.display_trade_log(results)
            BacktestResults.display_equity_curve(results)

            # Save results
            safe_symbol = symbol.replace('/', '-')
            output_file = f"backtest_results_{safe_symbol}_{start_date}_{end_date}.json"
            BacktestResults.save_to_file(results, output_file)

        else:
            logger.info("Starting bot...")
            bot.start()

            # Run in interactive mode (with status display) or simple mode
            if not args.no_interactive:
                # Interactive mode with status display and keyboard controls
                status_display = StatusDisplay()
                run_interactive_mode(bot, status_display)
            else:
                # Simple mode - just keep main thread alive
                logger.info("Running in non-interactive mode (use Ctrl+C to stop)")
                while bot.running:
                    import time
                    time.sleep(1)

    except KeyboardInterrupt:
        logger.info("\nShutting down bot...")
        bot.stop()
        logger.info("Bot stopped successfully")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        bot.stop()
        sys.exit(1)


if __name__ == '__main__':
    main()

