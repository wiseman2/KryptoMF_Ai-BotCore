"""
Configuration Manager - Handle bot configuration

Supports:
- YAML/JSON config files
- Interactive setup with validation
- Environment variables
- Configuration validation with helpful error messages
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from colorama import Fore, Style
from utils.logger import get_logger

logger = get_logger(__name__)


# Exchanges that require passphrase
EXCHANGES_WITH_PASSPHRASE = [
    'coinbase', 'coinbasepro', 'coinbase_pro',
    'kucoin', 'okx', 'okex'
]

# Supported exchanges
SUPPORTED_EXCHANGES = [
    'binance', 'binance_us', 'binanceus',
    'coinbase', 'coinbasepro', 'coinbase_pro',
    'kraken', 'kucoin', 'okx', 'bitfinex', 'gemini'
]

# Supported strategies
SUPPORTED_STRATEGIES = [
    'grid_trading', 'dca', 'momentum'
]


class ConfigManager:
    """
    Manages bot configuration from files or interactive setup.
    """
    
    def __init__(self):
        self.config_dir = Path(__file__).parent.parent.parent / 'config'
        self.config_dir.mkdir(exist_ok=True)
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from file with validation.

        Args:
            config_path: Path to config file (YAML or JSON)

        Returns:
            Configuration dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config format is invalid or validation fails
        """
        path = Path(config_path)

        if not path.exists():
            raise FileNotFoundError(
                f"{Fore.RED}Config file not found: {config_path}{Style.RESET_ALL}\n"
                f"Create a config file or run without --config for interactive setup."
            )

        logger.info(f"Loading configuration from {config_path}")

        try:
            with open(path, 'r') as f:
                if path.suffix in ['.yaml', '.yml']:
                    config = yaml.safe_load(f)
                elif path.suffix == '.json':
                    config = json.load(f)
                else:
                    raise ValueError(f"Unsupported config format: {path.suffix}. Use .yaml, .yml, or .json")
        except yaml.YAMLError as e:
            raise ValueError(f"{Fore.RED}Invalid YAML format:{Style.RESET_ALL}\n{e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"{Fore.RED}Invalid JSON format:{Style.RESET_ALL}\n{e}")

        # Validate configuration
        errors = self.validate_config(config)
        if errors:
            error_msg = f"{Fore.RED}Configuration validation failed:{Style.RESET_ALL}\n"
            for error in errors:
                error_msg += f"  ❌ {error}\n"
            raise ValueError(error_msg)

        logger.info(f"{Fore.GREEN}✓ Configuration loaded and validated{Style.RESET_ALL}")
        return config

    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """
        Validate configuration and return list of errors.

        Args:
            config: Configuration dictionary

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # Required fields
        if 'exchange' not in config:
            errors.append("Missing required field: 'exchange'")
        elif config['exchange'] not in SUPPORTED_EXCHANGES:
            errors.append(
                f"Unsupported exchange: '{config['exchange']}'. "
                f"Supported: {', '.join(SUPPORTED_EXCHANGES)}"
            )

        if 'symbol' not in config:
            errors.append("Missing required field: 'symbol' (e.g., 'BTC/USD')")

        if 'strategy' not in config:
            errors.append("Missing required field: 'strategy'")
        elif config['strategy'] not in SUPPORTED_STRATEGIES:
            errors.append(
                f"Unsupported strategy: '{config['strategy']}'. "
                f"Supported: {', '.join(SUPPORTED_STRATEGIES)}"
            )

        # Strategy-specific validation
        if config.get('strategy') == 'grid_trading':
            params = config.get('strategy_params', {})
            if 'grid_spacing' not in params:
                errors.append("Grid trading requires 'grid_spacing' parameter")
            if 'grid_levels' not in params:
                errors.append("Grid trading requires 'grid_levels' parameter")

        elif config.get('strategy') == 'dca':
            params = config.get('strategy_params', {})
            if 'interval_hours' not in params and 'use_indicators' not in params:
                errors.append("DCA requires either 'interval_hours' or 'use_indicators' parameter")

        # Risk management validation
        if 'risk' in config:
            risk = config['risk']
            if 'max_position_size' in risk and risk['max_position_size'] <= 0:
                errors.append("'max_position_size' must be greater than 0")
            if 'stop_loss_percent' in risk and risk['stop_loss_percent'] <= 0:
                errors.append("'stop_loss_percent' must be greater than 0")

        return errors
    
    def interactive_setup(self) -> Dict[str, Any]:
        """
        Interactive configuration setup with improved prompts and validation.

        Prompts user for configuration if no config file exists.

        Returns:
            Configuration dictionary
        """
        print()
        print("=" * 70)
        print(f"{Fore.CYAN}{'Welcome to KryptoMF Bot!':^70}{Style.RESET_ALL}")
        print("=" * 70)
        print()
        print(f"{Fore.YELLOW}No configuration found. Let's set up your bot.{Style.RESET_ALL}")
        print()

        config = {}

        # Exchange selection
        print(f"{Fore.GREEN}Step 1: Select Exchange{Style.RESET_ALL}")
        print("-" * 70)
        print("Available exchanges:")
        print(f"  {Fore.CYAN}1.{Style.RESET_ALL} Binance US")
        print(f"  {Fore.CYAN}2.{Style.RESET_ALL} Coinbase Pro (requires passphrase)")
        print(f"  {Fore.CYAN}3.{Style.RESET_ALL} Kraken")
        print(f"  {Fore.CYAN}4.{Style.RESET_ALL} KuCoin (requires passphrase)")
        print(f"  {Fore.CYAN}5.{Style.RESET_ALL} Binance (International)")
        print()

        exchange_choice = input(f"{Fore.YELLOW}Select exchange (1-5):{Style.RESET_ALL} ").strip()

        exchange_map = {
            '1': 'binance_us',
            '2': 'coinbasepro',
            '3': 'kraken',
            '4': 'kucoin',
            '5': 'binance'
        }
        config['exchange'] = exchange_map.get(exchange_choice, 'binance_us')

        # API credentials
        print()
        print(f"{Fore.GREEN}Step 2: API Credentials{Style.RESET_ALL}")
        print("-" * 70)
        print(f"{Fore.YELLOW}⚠️  SECURITY BEST PRACTICES:{Style.RESET_ALL}")
        print("  • Your API keys will be stored securely in your OS keychain")
        print("  • Enable TRADING permissions on your API keys")
        print("  • DISABLE WITHDRAWAL permissions (important!)")
        print("  • Enable IP whitelisting if possible")
        print()

        api_key = input(f"{Fore.YELLOW}Enter API key:{Style.RESET_ALL} ").strip()
        api_secret = input(f"{Fore.YELLOW}Enter API secret:{Style.RESET_ALL} ").strip()

        config['api_key'] = api_key
        config['api_secret'] = api_secret

        # Passphrase for exchanges that require it
        if config['exchange'] in EXCHANGES_WITH_PASSPHRASE:
            print()
            print(f"{Fore.YELLOW}This exchange requires an API passphrase.{Style.RESET_ALL}")
            passphrase = input(f"{Fore.YELLOW}Enter API passphrase:{Style.RESET_ALL} ").strip()
            config['passphrase'] = passphrase
        
        # Trading pair
        print()
        print(f"{Fore.GREEN}Step 3: Trading Pair{Style.RESET_ALL}")
        print("-" * 70)
        print("Examples: BTC/USD, ETH/USD, BTC/USDT, ETH/BTC")
        config['symbol'] = input(f"{Fore.YELLOW}Enter trading pair:{Style.RESET_ALL} ").strip().upper()

        # Strategy selection
        print()
        print(f"{Fore.GREEN}Step 4: Trading Strategy{Style.RESET_ALL}")
        print("-" * 70)
        print("Available strategies:")
        print(f"  {Fore.CYAN}1.{Style.RESET_ALL} Grid Trading - Place buy/sell orders at regular intervals")
        print(f"  {Fore.CYAN}2.{Style.RESET_ALL} DCA (Dollar Cost Averaging) - Buy at regular intervals or based on indicators")
        print(f"  {Fore.CYAN}3.{Style.RESET_ALL} Momentum - Trade based on price momentum (coming soon)")
        print()
        strategy_choice = input(f"{Fore.YELLOW}Select strategy (1-3):{Style.RESET_ALL} ").strip()

        strategy_map = {
            '1': 'grid_trading',
            '2': 'dca',
            '3': 'momentum'
        }
        config['strategy'] = strategy_map.get(strategy_choice, 'grid_trading')

        # Strategy parameters
        print()
        print(f"{Fore.GREEN}Step 5: Strategy Parameters{Style.RESET_ALL}")
        print("-" * 70)

        if config['strategy'] == 'grid_trading':
            print("Grid Trading Configuration:")
            grid_spacing = input(f"  Grid spacing (%) [{Fore.CYAN}2.5{Style.RESET_ALL}]: ").strip()
            grid_levels = input(f"  Number of grid levels [{Fore.CYAN}10{Style.RESET_ALL}]: ").strip()
            position_size = input(f"  Position size per level (USD) [{Fore.CYAN}100{Style.RESET_ALL}]: ").strip()

            config['strategy_params'] = {
                'grid_spacing': float(grid_spacing or "2.5"),
                'grid_levels': int(grid_levels or "10"),
                'position_size': float(position_size or "100")
            }

        elif config['strategy'] == 'dca':
            print("DCA Configuration:")
            print(f"  {Fore.YELLOW}Choose DCA mode:{Style.RESET_ALL}")
            print(f"    {Fore.CYAN}1.{Style.RESET_ALL} Time-based (buy at regular intervals)")
            print(f"    {Fore.CYAN}2.{Style.RESET_ALL} Indicator-based (buy when indicators signal)")
            dca_mode = input(f"  Select mode (1-2) [{Fore.CYAN}1{Style.RESET_ALL}]: ").strip() or "1"

            if dca_mode == "2":
                config['strategy_params'] = {
                    'use_indicators': True,
                    'amount_usd': float(input(f"  Amount per purchase (USD) [{Fore.CYAN}100{Style.RESET_ALL}]: ").strip() or "100")
                }
            else:
                config['strategy_params'] = {
                    'interval_hours': int(input(f"  DCA interval (hours) [{Fore.CYAN}24{Style.RESET_ALL}]: ").strip() or "24"),
                    'amount_usd': float(input(f"  Amount per purchase (USD) [{Fore.CYAN}100{Style.RESET_ALL}]: ").strip() or "100")
                }
        else:
            config['strategy_params'] = {}

        # Risk management
        print()
        print(f"{Fore.GREEN}Step 6: Risk Management{Style.RESET_ALL}")
        print("-" * 70)
        max_position = input(f"Max total position size (USD) [{Fore.CYAN}1000{Style.RESET_ALL}]: ").strip()
        stop_loss = input(f"Stop loss (%) [{Fore.CYAN}5{Style.RESET_ALL}]: ").strip()

        config['risk'] = {
            'max_position_size': float(max_position or "1000"),
            'stop_loss_percent': float(stop_loss or "5")
        }

        # Paper trading
        print()
        print(f"{Fore.GREEN}Step 7: Trading Mode{Style.RESET_ALL}")
        print("-" * 70)
        paper_trading = input(f"Enable paper trading mode? (y/n) [{Fore.CYAN}y{Style.RESET_ALL}]: ").strip().lower()
        config['paper_trading'] = paper_trading != 'n'

        if config['paper_trading']:
            print(f"{Fore.YELLOW}⚠️  Paper trading enabled - No real orders will be placed{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}⚠️  LIVE TRADING ENABLED - Real orders will be placed!{Style.RESET_ALL}")

        # Save configuration
        print()
        print("=" * 70)
        print(f"{Fore.GREEN}Configuration Summary:{Style.RESET_ALL}")
        print(f"  Exchange: {config['exchange']}")
        print(f"  Symbol: {config['symbol']}")
        print(f"  Strategy: {config['strategy']}")
        print(f"  Paper Trading: {config['paper_trading']}")
        print("=" * 70)
        print()

        save_config = input(f"{Fore.YELLOW}Save this configuration? (y/n):{Style.RESET_ALL} ").strip().lower()

        if save_config == 'y':
            config_path = self.config_dir / 'bot_config.yaml'
            self.save_config(config, str(config_path))
            print(f"{Fore.GREEN}✓ Configuration saved to {config_path}{Style.RESET_ALL}")

        print()
        return config
    
    def save_config(self, config: Dict[str, Any], config_path: str):
        """
        Save configuration to file.
        
        Args:
            config: Configuration dictionary
            config_path: Path to save config file
        """
        path = Path(config_path)
        
        with open(path, 'w') as f:
            if path.suffix in ['.yaml', '.yml']:
                yaml.dump(config, f, default_flow_style=False)
            elif path.suffix == '.json':
                json.dump(config, f, indent=2)
            else:
                raise ValueError(f"Unsupported config format: {path.suffix}")
        
        logger.info(f"Configuration saved to {config_path}")

