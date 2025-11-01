#!/usr/bin/env python3
"""
KryptoMF Bot - Main Entry Point

This is the main entry point for the bot.

CLI Mode (Open Source):
    - Runs a single bot instance
    - Configuration via YAML file or interactive prompts
    - Console output with colored logging
    
GUI Mode (Premium - if installed):
    - Multi-bot manager
    - Add/remove/configure multiple bots
    - Dashboard with real-time stats
    - Drag and drop interface
    - Saved bot configurations

Usage:
    # CLI mode (single bot)
    python main.py --config config/bot_config.yaml
    
    # CLI mode (interactive setup)
    python main.py
    
    # GUI mode (if GUI package installed)
    python main.py --gui
    
    # Paper trading
    python main.py --paper-trading
"""

import sys
import argparse
import signal
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from utils.logger import setup_logger, get_logger
from core.config_manager import ConfigManager
from core.bot_instance import BotInstance

logger = None


def check_gui_available():
    """
    Check if the premium GUI package is installed.
    
    Returns:
        bool: True if GUI is available
    """
    try:
        import kryptomf_gui
        return True
    except ImportError:
        return False


def run_cli_mode(args):
    """
    Run in CLI mode (single bot).
    
    This is the open source mode - fully functional!
    
    Args:
        args: Command line arguments
    """
    global logger
    logger = setup_logger(verbose=args.verbose)
    
    logger.info("=" * 60)
    logger.info("KryptoMF Bot - Open Source Edition")
    logger.info("=" * 60)
    logger.info("")
    
    # Load configuration
    config_manager = ConfigManager()
    
    if args.config:
        logger.info(f"Loading configuration from {args.config}")
        config = config_manager.load_config(args.config)
    else:
        logger.info("No configuration file specified")
        config = config_manager.interactive_setup()
    
    # Override with command line args
    if args.paper_trading:
        config['paper_trading'] = True
    
    # Create bot instance
    logger.info("")
    logger.info("Creating bot instance...")
    
    bot = BotInstance(config)
    
    # Initialize
    if not bot.initialize():
        logger.error("Failed to initialize bot")
        sys.exit(1)
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        logger.info("")
        logger.info("Received shutdown signal (Ctrl+C)")
        bot.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start bot
    logger.info("")
    logger.info("=" * 60)
    logger.info("Starting Bot")
    logger.info("=" * 60)
    
    bot.start()
    
    # Keep main thread alive
    try:
        while bot.running:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        bot.stop()


def run_gui_mode(args):
    """
    Run in GUI mode (multi-bot manager).
    
    This requires the premium GUI package.
    
    Args:
        args: Command line arguments
    """
    try:
        from kryptomf_gui import launch_gui
        
        logger.info("=" * 60)
        logger.info("KryptoMF Bot - Premium GUI Edition")
        logger.info("=" * 60)
        logger.info("")
        logger.info("Launching multi-bot manager...")
        
        # Launch GUI
        launch_gui()
        
    except ImportError:
        logger.error("GUI package not installed!")
        logger.error("")
        logger.error("The premium GUI is not available in the open source version.")
        logger.error("")
        logger.error("To use the GUI:")
        logger.error("  1. Purchase a license at https://kryptomf.com/pricing")
        logger.error("  2. Install the GUI package: pip install kryptomf-gui")
        logger.error("")
        logger.error("Or continue using the fully functional CLI mode:")
        logger.error("  python main.py --config config/bot_config.yaml")
        logger.error("")
        sys.exit(1)


def main():
    """
    Main entry point.
    """
    global logger
    
    parser = argparse.ArgumentParser(
        description='KryptoMF Bot - Cryptocurrency Trading Bot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with config file (CLI mode)
  python main.py --config config/bot_config.yaml
  
  # Interactive setup (CLI mode)
  python main.py
  
  # Paper trading mode
  python main.py --paper-trading
  
  # Launch GUI (if installed)
  python main.py --gui
  
  # Verbose logging
  python main.py --config config/bot_config.yaml --verbose

For more information, visit: https://github.com/yourusername/KryptoMF_Ai-BotCore
        """
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file (YAML/JSON)'
    )
    
    parser.add_argument(
        '--gui',
        action='store_true',
        help='Launch GUI mode (requires premium package)'
    )
    
    parser.add_argument(
        '--paper-trading',
        action='store_true',
        help='Run in paper trading mode (no real orders)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='KryptoMF Bot v1.0.0 (Open Source)'
    )
    
    args = parser.parse_args()
    
    # Setup logger
    logger = setup_logger(verbose=args.verbose)
    
    # Check if GUI mode requested
    if args.gui:
        run_gui_mode(args)
    else:
        # Check if GUI is available and suggest it
        if check_gui_available():
            logger.info("💡 Tip: GUI mode is available! Run with --gui flag")
            logger.info("")
        
        # Run CLI mode
        run_cli_mode(args)


if __name__ == '__main__':
    main()

