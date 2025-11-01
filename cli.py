#!/usr/bin/env python3
"""
KryptoMF Bot Core - CLI Entry Point

This is the main entry point for the open source CLI bot.
Run this file to start the bot from your code editor.
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.bot_engine import BotEngine
from core.config_manager import ConfigManager
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
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
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
        config = config_manager.load_config(args.config)
    else:
        logger.info("No configuration file specified")
        config = config_manager.interactive_setup()
    
    # Override with CLI flags
    if args.paper_trading:
        config['paper_trading'] = True
        logger.info("Paper trading mode enabled")
    
    # Create and start bot
    bot = BotEngine(config)
    
    try:
        if args.backtest:
            logger.info("Starting backtest...")
            bot.run_backtest()
        else:
            logger.info("Starting bot...")
            bot.run()
    except KeyboardInterrupt:
        logger.info("\nShutting down bot...")
        bot.stop()
        logger.info("Bot stopped successfully")
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

