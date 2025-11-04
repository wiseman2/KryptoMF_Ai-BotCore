"""
Configuration Manager - Handle bot configuration

Supports:
- YAML/JSON config files
- Interactive setup with validation
- Environment variables
- Configuration validation with helpful error messages
"""

import os
import sys
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

    def main_menu(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Display main menu for configuration management.

        Args:
            config_path: Optional path to existing config file

        Returns:
            Configuration dictionary
        """
        while True:
            print()
            print("=" * 70)
            print(f"{Fore.CYAN}KryptoMF Bot - Main Menu{Style.RESET_ALL}")
            print("=" * 70)
            print()

            # Check if config exists
            default_config = self.config_dir / 'bot_config.yaml'
            has_config = config_path and Path(config_path).exists() or default_config.exists()

            if has_config:
                config_file = config_path if config_path else str(default_config)
                print(f"{Fore.GREEN}✓ Configuration found:{Style.RESET_ALL} {config_file}")
            else:
                print(f"{Fore.YELLOW}⚠ No configuration found{Style.RESET_ALL}")

            print()
            print(f"{Fore.CYAN}Options:{Style.RESET_ALL}")
            print(f"  {Fore.YELLOW}1.{Style.RESET_ALL} Start bot (live/paper trading)")
            print(f"  {Fore.YELLOW}2.{Style.RESET_ALL} Run backtest (test strategy on historical data)")
            print(f"  {Fore.YELLOW}3.{Style.RESET_ALL} Create new configuration (interactive setup)")
            print(f"  {Fore.YELLOW}4.{Style.RESET_ALL} Edit existing configuration")
            print(f"  {Fore.YELLOW}5.{Style.RESET_ALL} Update API credentials (keychain)")
            print(f"  {Fore.YELLOW}6.{Style.RESET_ALL} View current configuration")
            print(f"  {Fore.YELLOW}7.{Style.RESET_ALL} Delete API credentials from keychain")
            print(f"  {Fore.YELLOW}8.{Style.RESET_ALL} Exit")
            print()

            choice = input(f"{Fore.YELLOW}Select option (1-8):{Style.RESET_ALL} ").strip()

            if choice == '1':
                # Start with existing config
                if has_config:
                    config_file = config_path if config_path else str(default_config)
                    config = self.load_config(config_file)
                    config['_mode'] = 'live'  # Mark as live trading mode
                    return config
                else:
                    print(f"{Fore.RED}✗ No configuration found. Please create one first.{Style.RESET_ALL}")
                    input("Press Enter to continue...")

            elif choice == '2':
                # Run backtest
                if has_config:
                    config_file = config_path if config_path else str(default_config)
                    config = self.load_config(config_file)
                    config['_mode'] = 'backtest'  # Mark as backtest mode
                    return config
                else:
                    print(f"{Fore.RED}✗ No configuration found. Please create one first.{Style.RESET_ALL}")
                    input("Press Enter to continue...")

            elif choice == '3':
                # Create new configuration
                return self.interactive_setup()

            elif choice == '4':
                # Edit existing configuration
                if has_config:
                    config_file = config_path if config_path else str(default_config)
                    self.edit_config(config_file)
                else:
                    print(f"{Fore.RED}✗ No configuration found. Please create one first.{Style.RESET_ALL}")
                    input("Press Enter to continue...")

            elif choice == '5':
                # Update API credentials
                self.update_credentials()

            elif choice == '6':
                # View configuration
                if has_config:
                    config_file = config_path if config_path else str(default_config)
                    self.view_config(config_file)
                else:
                    print(f"{Fore.RED}✗ No configuration found.{Style.RESET_ALL}")
                input("Press Enter to continue...")

            elif choice == '7':
                # Delete credentials
                self.delete_credentials()

            elif choice == '8':
                # Exit
                print(f"{Fore.YELLOW}Exiting...{Style.RESET_ALL}")
                sys.exit(0)

            else:
                print(f"{Fore.RED}✗ Invalid option. Please select 1-8.{Style.RESET_ALL}")
                input("Press Enter to continue...")

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

        # Trading fees validation
        if 'fees' in config:
            fees = config['fees']
            if 'maker' in fees and (fees['maker'] < 0 or fees['maker'] > 10):
                errors.append("'maker' fee must be between 0 and 10 percent")
            if 'taker' in fees and (fees['taker'] < 0 or fees['taker'] > 10):
                errors.append("'taker' fee must be between 0 and 10 percent")

        # Profit target validation
        if 'profit_target' in config:
            if config['profit_target'] <= 0:
                errors.append("'profit_target' must be greater than 0")
            elif config['profit_target'] > 100:
                errors.append("'profit_target' seems unreasonably high (>100%)")

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

        # Trading mode FIRST - determines if we need API credentials
        print(f"{Fore.GREEN}Step 1: Trading Mode{Style.RESET_ALL}")
        print("-" * 70)
        print(f"{Fore.YELLOW}ℹ️  Choose your trading mode:{Style.RESET_ALL}")
        print(f"  • {Fore.CYAN}Paper Trading:{Style.RESET_ALL} Test strategies with simulated trades (no real money)")
        print(f"  • {Fore.CYAN}Live Trading:{Style.RESET_ALL} Execute real trades on the exchange")
        print()
        paper_trading = input(f"Enable paper trading mode? (y/n) [{Fore.CYAN}y{Style.RESET_ALL}]: ").strip().lower()
        config['paper_trading'] = paper_trading != 'n'

        if config['paper_trading']:
            print(f"{Fore.GREEN}✓ Paper trading enabled - No real orders will be placed{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}ℹ️  API credentials are NOT required for paper trading{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}⚠️  LIVE TRADING ENABLED - Real orders will be placed!{Style.RESET_ALL}")

        # Exchange selection
        print()
        print(f"{Fore.GREEN}Step 2: Select Exchange{Style.RESET_ALL}")
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

        # API credentials - ONLY if NOT paper trading
        if not config['paper_trading']:
            print()
            print(f"{Fore.GREEN}Step 3: API Credentials{Style.RESET_ALL}")
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
        else:
            print()
            print(f"{Fore.YELLOW}ℹ️  Skipping API credentials (not needed for paper trading){Style.RESET_ALL}")

        # Trading pair
        print()
        print(f"{Fore.GREEN}Step {'4' if not config['paper_trading'] else '3'}: Trading Pair{Style.RESET_ALL}")
        print("-" * 70)
        print("Examples: BTC/USD, ETH/USD, BTC/USDT, ETH/BTC")
        config['symbol'] = input(f"{Fore.YELLOW}Enter trading pair:{Style.RESET_ALL} ").strip().upper()

        # Strategy selection
        print()
        print(f"{Fore.GREEN}Step 4: Trading Strategy{Style.RESET_ALL}")
        print("-" * 70)
        print("Available strategies:")
        print(f"  {Fore.CYAN}1.{Style.RESET_ALL} Grid Trading - Place buy/sell orders at regular intervals")
        print(f"  {Fore.CYAN}2.{Style.RESET_ALL} DCA (Dollar Cost Averaging) - Buy based on indicators")
        print(f"  {Fore.CYAN}3.{Style.RESET_ALL} Advanced DCA - DCA with profit reinvestment to reduce cost basis")
        print(f"  {Fore.CYAN}4.{Style.RESET_ALL} Momentum - Trade based on price momentum (coming soon)")
        print()
        strategy_choice = input(f"{Fore.YELLOW}Select strategy (1-4):{Style.RESET_ALL} ").strip()

        strategy_map = {
            '1': 'grid_trading',
            '2': 'dca',
            '3': 'advanced_dca',
            '4': 'momentum'
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
            amount_usd = float(input(f"  Amount per purchase (USD) [{Fore.CYAN}100{Style.RESET_ALL}]: ").strip() or "100")

            # Indicator-based DCA (always use indicators)
            print()
            print(f"  {Fore.YELLOW}Configure Technical Indicators:{Style.RESET_ALL}")
            indicators = self._configure_indicators()

            config['strategy_params'] = {
                'amount_usd': amount_usd,
                'min_interval_hours': 0,  # No time restriction by default
                'indicators': indicators
            }

            # Add price_drop if it was configured
            if 'price_drop' in indicators:
                config['strategy_params']['price_drop'] = indicators.pop('price_drop')

        elif config['strategy'] == 'advanced_dca':
            print("Advanced DCA Configuration:")
            print(f"  {Fore.YELLOW}This strategy applies profits to reduce cost basis of previous purchases{Style.RESET_ALL}")
            print()

            amount_usd = float(input(f"  Amount per purchase (USD) [{Fore.CYAN}100{Style.RESET_ALL}]: ").strip() or "100")
            max_purchases = input(f"  Max concurrent purchases (-1 for unlimited) [{Fore.CYAN}-1{Style.RESET_ALL}]: ").strip()

            # Indicator-based
            print()
            print(f"  {Fore.YELLOW}Configure Technical Indicators:{Style.RESET_ALL}")
            indicators = self._configure_indicators()

            config['strategy_params'] = {
                'amount_usd': amount_usd,
                'max_purchases': int(max_purchases or "-1"),
                'min_interval_hours': 0,  # No time restriction by default
                'indicators': indicators
            }

            # Add price_drop if it was configured
            if 'price_drop' in indicators:
                config['strategy_params']['price_drop'] = indicators.pop('price_drop')

        else:
            config['strategy_params'] = {}

        # Trading fees
        print()
        print(f"{Fore.GREEN}Step 6: Trading Fees{Style.RESET_ALL}")
        print("-" * 70)
        print(f"{Fore.YELLOW}ℹ️  Trading fees are crucial for accurate profit calculations{Style.RESET_ALL}")
        print("  • Maker fee: When you add liquidity (limit orders)")
        print("  • Taker fee: When you remove liquidity (market orders)")
        print()
        print(f"{Fore.CYAN}Common exchange fees:{Style.RESET_ALL}")
        print("  • Binance/Binance.US: 0.1% maker, 0.1% taker")
        print("  • Coinbase Pro: 0.5% maker, 0.5% taker")
        print("  • Kraken: 0.16% maker, 0.26% taker")
        print()

        maker_fee = input(f"Maker fee (%) [{Fore.CYAN}0.1{Style.RESET_ALL}]: ").strip()
        taker_fee = input(f"Taker fee (%) [{Fore.CYAN}0.1{Style.RESET_ALL}]: ").strip()

        config['fees'] = {
            'maker': float(maker_fee or "0.1"),
            'taker': float(taker_fee or "0.1")
        }

        # Profit target
        print()
        print(f"{Fore.GREEN}Step 7: Profit Target{Style.RESET_ALL}")
        print("-" * 70)
        print(f"{Fore.YELLOW}ℹ️  Minimum profit percentage before selling{Style.RESET_ALL}")
        print("  • This is AFTER accounting for all trading fees")
        print("  • Example: 1.0% means you need 1% profit after buy+sell fees")
        print()

        profit_target = input(f"Minimum profit target (%) [{Fore.CYAN}1.0{Style.RESET_ALL}]: ").strip()

        config['profit_target'] = float(profit_target or "1.0")

        # Order types and trailing configuration
        print()
        print(f"{Fore.GREEN}Step 8: Order Types{Style.RESET_ALL}")
        print("-" * 70)
        print(f"{Fore.YELLOW}ℹ️  Configure order types for buying and selling{Style.RESET_ALL}")
        print("  • Market: Execute immediately at current price (higher fees)")
        print("  • Limit: Set your price, wait for fill (lower fees)")
        print("  • Stop: Trigger at specific price")
        print("  • Trailing: Follow price movement with percentage offset")
        print()

        print(f"{Fore.CYAN}Buy Order Type:{Style.RESET_ALL}")
        print("  1. Market")
        print("  2. Limit")
        print("  3. Trailing Market")
        print("  4. Trailing Limit")
        buy_order_type = input(f"Select buy order type (1-4) [{Fore.CYAN}2{Style.RESET_ALL}]: ").strip() or "2"

        buy_order_map = {"1": "market", "2": "limit", "3": "trailing_market", "4": "trailing_limit"}
        config['buy_order_type'] = buy_order_map.get(buy_order_type, "limit")

        # If trailing buy, ask for percentage
        if config['buy_order_type'] in ['trailing_market', 'trailing_limit']:
            print()
            print(f"{Fore.YELLOW}ℹ️  Trailing buy follows price down{Style.RESET_ALL}")
            print("  • Example: 0.25% means buy when price rises 0.25% from lowest point")
            trailing_buy_pct = input(f"Trailing buy percentage (%) [{Fore.CYAN}0.25{Style.RESET_ALL}]: ").strip()
            config['trailing_buy_percent'] = float(trailing_buy_pct or "0.25")

        print()
        print(f"{Fore.CYAN}Sell Order Type:{Style.RESET_ALL}")
        print("  1. Market")
        print("  2. Limit")
        print("  3. Trailing Market")
        print("  4. Trailing Limit")
        print("  5. Trailing Stop")
        sell_order_type = input(f"Select sell order type (1-5) [{Fore.CYAN}3{Style.RESET_ALL}]: ").strip() or "3"

        sell_order_map = {"1": "market", "2": "limit", "3": "trailing_market", "4": "trailing_limit", "5": "trailing_stop"}
        config['sell_order_type'] = sell_order_map.get(sell_order_type, "trailing_market")

        # If trailing sell, ask for percentage
        if config['sell_order_type'] in ['trailing_market', 'trailing_limit', 'trailing_stop']:
            print()
            print(f"{Fore.YELLOW}ℹ️  Trailing sell follows price up to maximize profit{Style.RESET_ALL}")
            print("  • Example: 0.25% means sell when price drops 0.25% from highest point")
            print("  • For 0.5-1% profit targets, 0.25% trailing is recommended")
            trailing_sell_pct = input(f"Trailing sell percentage (%) [{Fore.CYAN}0.25{Style.RESET_ALL}]: ").strip()
            config['trailing_sell_percent'] = float(trailing_sell_pct or "0.25")

        # Risk management
        print()
        print(f"{Fore.GREEN}Step 9: Risk Management{Style.RESET_ALL}")
        print("-" * 70)
        max_position = input(f"Max total position size (USD) [{Fore.CYAN}1000{Style.RESET_ALL}]: ").strip()
        stop_loss = input(f"Stop loss (%) [{Fore.CYAN}5{Style.RESET_ALL}]: ").strip()

        config['risk'] = {
            'max_position_size': float(max_position or "1000"),
            'stop_loss_percent': float(stop_loss or "5")
        }

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
            # Store API credentials in OS keychain BEFORE saving config
            # This ensures credentials are never written to the config file
            if 'api_key' in config and 'api_secret' in config:
                from security.secret_provider import get_secret_provider
                secret_provider = get_secret_provider()

                passphrase = config.get('passphrase')  # May be None
                secret_provider.store_key(
                    config['exchange'],
                    config['api_key'],
                    config['api_secret'],
                    passphrase
                )
                print(f"{Fore.GREEN}✓ API credentials stored securely in OS keychain{Style.RESET_ALL}")

            # Save config file (credentials will be excluded by save_config method)
            config_path = self.config_dir / 'bot_config.yaml'
            self.save_config(config, str(config_path))
            print(f"{Fore.GREEN}✓ Configuration saved to {config_path}{Style.RESET_ALL}")

        print()
        return config
    
    def save_config(self, config: Dict[str, Any], config_path: str):
        """
        Save configuration to file.

        SECURITY: API credentials are NEVER saved to the config file.
        They are stored securely in the OS keychain only.

        Args:
            config: Configuration dictionary
            config_path: Path to save config file
        """
        path = Path(config_path)

        # Create a copy of config WITHOUT sensitive credentials
        safe_config = config.copy()

        # Remove sensitive fields that should NEVER be in config files
        sensitive_fields = ['api_key', 'api_secret', 'passphrase']
        for field in sensitive_fields:
            if field in safe_config:
                del safe_config[field]
                logger.debug(f"Removed {field} from config file (stored securely in keychain)")

        with open(path, 'w') as f:
            if path.suffix in ['.yaml', '.yml']:
                yaml.dump(safe_config, f, default_flow_style=False)
            elif path.suffix == '.json':
                json.dump(safe_config, f, indent=2)
            else:
                raise ValueError(f"Unsupported config format: {path.suffix}")

        logger.info(f"Configuration saved to {config_path}")
        logger.info("✓ API credentials NOT saved to file (stored securely in OS keychain)")

    def _configure_indicators(self) -> Dict[str, Any]:
        """
        Interactive configuration for technical indicators.

        Returns:
            Dictionary of indicator configurations
        """
        print()
        print(f"  {Fore.CYAN}Available Technical Indicators:{Style.RESET_ALL}")
        print(f"    {Fore.CYAN}1.{Style.RESET_ALL} RSI (Relative Strength Index)")
        print(f"    {Fore.CYAN}2.{Style.RESET_ALL} Stochastic RSI")
        print(f"    {Fore.CYAN}3.{Style.RESET_ALL} EMA (Exponential Moving Average)")
        print(f"    {Fore.CYAN}4.{Style.RESET_ALL} MACD (Moving Average Convergence Divergence)")
        print(f"    {Fore.CYAN}5.{Style.RESET_ALL} MFI (Money Flow Index)")
        print(f"    {Fore.CYAN}6.{Style.RESET_ALL} Multiple indicators (recommended)")
        print()

        indicator_choice = input(f"  Select indicator(s) (1-6) [{Fore.CYAN}6{Style.RESET_ALL}]: ").strip() or "6"

        indicators = {}

        if indicator_choice == "1":
            # RSI only
            print()
            print(f"  {Fore.YELLOW}RSI Configuration:{Style.RESET_ALL}")
            rsi_period = input(f"    Period [{Fore.CYAN}14{Style.RESET_ALL}]: ").strip()
            rsi_oversold = input(f"    Oversold threshold [{Fore.CYAN}30{Style.RESET_ALL}]: ").strip()
            rsi_overbought = input(f"    Overbought threshold [{Fore.CYAN}70{Style.RESET_ALL}]: ").strip()
            rsi_rising = input(f"    Check if RSI is rising? (y/n) [{Fore.CYAN}y{Style.RESET_ALL}]: ").strip().lower() or "y"

            indicators['rsi'] = {
                'enabled': True,
                'period': int(rsi_period or "14"),
                'oversold': float(rsi_oversold or "30"),
                'overbought': float(rsi_overbought or "70"),
                'check_rising': rsi_rising == 'y'
            }

        elif indicator_choice == "2":
            # Stochastic RSI only
            print()
            print(f"  {Fore.YELLOW}Stochastic RSI Configuration:{Style.RESET_ALL}")
            stoch_period = input(f"    Period [{Fore.CYAN}14{Style.RESET_ALL}]: ").strip()
            stoch_oversold = input(f"    Oversold threshold [{Fore.CYAN}20{Style.RESET_ALL}]: ").strip()
            stoch_overbought = input(f"    Overbought threshold [{Fore.CYAN}80{Style.RESET_ALL}]: ").strip()

            indicators['stoch_rsi'] = {
                'enabled': True,
                'period': int(stoch_period or "14"),
                'oversold': float(stoch_oversold or "20"),
                'overbought': float(stoch_overbought or "80")
            }

        elif indicator_choice == "3":
            # EMA only
            print()
            print(f"  {Fore.YELLOW}EMA Configuration:{Style.RESET_ALL}")
            ema_short = input(f"    Short period [{Fore.CYAN}12{Style.RESET_ALL}]: ").strip()
            ema_long = input(f"    Long period [{Fore.CYAN}26{Style.RESET_ALL}]: ").strip()

            indicators['ema'] = {
                'enabled': True,
                'short_period': int(ema_short or "12"),
                'long_period': int(ema_long or "26")
            }

        elif indicator_choice == "4":
            # MACD only
            print()
            print(f"  {Fore.YELLOW}MACD Configuration:{Style.RESET_ALL}")
            macd_fast = input(f"    Fast period [{Fore.CYAN}12{Style.RESET_ALL}]: ").strip()
            macd_slow = input(f"    Slow period [{Fore.CYAN}26{Style.RESET_ALL}]: ").strip()
            macd_signal = input(f"    Signal period [{Fore.CYAN}9{Style.RESET_ALL}]: ").strip()

            indicators['macd'] = {
                'enabled': True,
                'fast_period': int(macd_fast or "12"),
                'slow_period': int(macd_slow or "26"),
                'signal_period': int(macd_signal or "9")
            }

        elif indicator_choice == "5":
            # MFI only
            print()
            print(f"  {Fore.YELLOW}MFI Configuration:{Style.RESET_ALL}")
            mfi_period = input(f"    Period [{Fore.CYAN}14{Style.RESET_ALL}]: ").strip()
            mfi_oversold = input(f"    Oversold threshold [{Fore.CYAN}20{Style.RESET_ALL}]: ").strip()
            mfi_overbought = input(f"    Overbought threshold [{Fore.CYAN}80{Style.RESET_ALL}]: ").strip()

            indicators['mfi'] = {
                'enabled': True,
                'period': int(mfi_period or "14"),
                'oversold': float(mfi_oversold or "20"),
                'overbought': float(mfi_overbought or "80")
            }

        else:
            # Multiple indicators (recommended) - Use FlexGrid proven defaults
            print()
            print(f"  {Fore.YELLOW}Using recommended multi-indicator setup (FlexGrid proven defaults):{Style.RESET_ALL}")
            print("    • RSI (14 period, 35/55 thresholds, rising check)")
            print("    • Stochastic RSI (14 period, 33/80 thresholds)")
            print("    • EMA (25 period)")
            print("    • MACD (12/26/9, rising check)")
            print("    • MFI (14 period, 25 oversold)")
            print("    • Rising Price (3 candle lookback)")
            print()

            use_defaults = input(f"  Use default settings? (y/n) [{Fore.CYAN}y{Style.RESET_ALL}]: ").strip().lower()

            if use_defaults != 'n':
                # Use FlexGrid proven defaults
                indicators = {
                    'rsi': {
                        'enabled': True,
                        'period': 14,
                        'oversold': 35,
                        'overbought': 55,
                        'check_rising': True
                    },
                    'stoch_rsi': {
                        'enabled': True,
                        'period': 14,
                        'smoothing': 3,
                        'oversold': 33,
                        'overbought': 80
                    },
                    'ema': {
                        'enabled': True,
                        'length': 25
                    },
                    'macd': {
                        'enabled': True,
                        'fast': 12,
                        'slow': 26,
                        'signal': 9,
                        'check_rising': True
                    },
                    'mfi': {
                        'enabled': True,
                        'period': 14,
                        'oversold': 25
                    },
                    'rising_price': {
                        'enabled': True,
                        'lookback_candles': 3
                    }
                }
            else:
                # Custom configuration for each
                indicators = {}

                # RSI
                print()
                print(f"  {Fore.YELLOW}RSI Configuration:{Style.RESET_ALL}")
                rsi_enabled = input(f"    Enable RSI? (y/n) [{Fore.CYAN}y{Style.RESET_ALL}]: ").strip().lower() or "y"
                if rsi_enabled == 'y':
                    rsi_period = input(f"    Period [{Fore.CYAN}14{Style.RESET_ALL}]: ").strip()
                    rsi_oversold = input(f"    Oversold [{Fore.CYAN}35{Style.RESET_ALL}]: ").strip()
                    rsi_overbought = input(f"    Overbought [{Fore.CYAN}55{Style.RESET_ALL}]: ").strip()
                    rsi_rising = input(f"    Check if RSI is rising? (y/n) [{Fore.CYAN}y{Style.RESET_ALL}]: ").strip().lower() or "y"
                    indicators['rsi'] = {
                        'enabled': True,
                        'period': int(rsi_period or "14"),
                        'oversold': float(rsi_oversold or "35"),
                        'overbought': float(rsi_overbought or "55"),
                        'check_rising': rsi_rising == 'y'
                    }

                # Stochastic RSI
                print()
                print(f"  {Fore.YELLOW}Stochastic RSI Configuration:{Style.RESET_ALL}")
                stoch_enabled = input(f"    Enable Stoch RSI? (y/n) [{Fore.CYAN}y{Style.RESET_ALL}]: ").strip().lower() or "y"
                if stoch_enabled == 'y':
                    stoch_period = input(f"    Period [{Fore.CYAN}14{Style.RESET_ALL}]: ").strip()
                    stoch_smoothing = input(f"    Smoothing [{Fore.CYAN}3{Style.RESET_ALL}]: ").strip()
                    stoch_oversold = input(f"    Oversold [{Fore.CYAN}33{Style.RESET_ALL}]: ").strip()
                    stoch_overbought = input(f"    Overbought [{Fore.CYAN}80{Style.RESET_ALL}]: ").strip()
                    indicators['stoch_rsi'] = {
                        'enabled': True,
                        'period': int(stoch_period or "14"),
                        'smoothing': int(stoch_smoothing or "3"),
                        'oversold': float(stoch_oversold or "33"),
                        'overbought': float(stoch_overbought or "80")
                    }

                # EMA
                print()
                print(f"  {Fore.YELLOW}EMA Configuration:{Style.RESET_ALL}")
                ema_enabled = input(f"    Enable EMA? (y/n) [{Fore.CYAN}y{Style.RESET_ALL}]: ").strip().lower() or "y"
                if ema_enabled == 'y':
                    ema_length = input(f"    EMA length [{Fore.CYAN}25{Style.RESET_ALL}]: ").strip()
                    indicators['ema'] = {
                        'enabled': True,
                        'length': int(ema_length or "25")
                    }

                # MACD
                print()
                print(f"  {Fore.YELLOW}MACD Configuration:{Style.RESET_ALL}")
                macd_enabled = input(f"    Enable MACD? (y/n) [{Fore.CYAN}y{Style.RESET_ALL}]: ").strip().lower() or "y"
                if macd_enabled == 'y':
                    macd_fast = input(f"    Fast period [{Fore.CYAN}12{Style.RESET_ALL}]: ").strip()
                    macd_slow = input(f"    Slow period [{Fore.CYAN}26{Style.RESET_ALL}]: ").strip()
                    macd_signal = input(f"    Signal period [{Fore.CYAN}9{Style.RESET_ALL}]: ").strip()
                    macd_rising = input(f"    Check if MACD is rising? (y/n) [{Fore.CYAN}y{Style.RESET_ALL}]: ").strip().lower() or "y"
                    indicators['macd'] = {
                        'enabled': True,
                        'fast': int(macd_fast or "12"),
                        'slow': int(macd_slow or "26"),
                        'signal': int(macd_signal or "9"),
                        'check_rising': macd_rising == 'y'
                    }

                # MFI
                print()
                print(f"  {Fore.YELLOW}MFI Configuration:{Style.RESET_ALL}")
                mfi_enabled = input(f"    Enable MFI? (y/n) [{Fore.CYAN}y{Style.RESET_ALL}]: ").strip().lower() or "y"
                if mfi_enabled == 'y':
                    mfi_period = input(f"    Period [{Fore.CYAN}14{Style.RESET_ALL}]: ").strip()
                    mfi_oversold = input(f"    Oversold [{Fore.CYAN}25{Style.RESET_ALL}]: ").strip()
                    indicators['mfi'] = {
                        'enabled': True,
                        'period': int(mfi_period or "14"),
                        'oversold': float(mfi_oversold or "25")
                    }

                # Rising Price
                print()
                print(f"  {Fore.YELLOW}Rising Price Configuration:{Style.RESET_ALL}")
                rising_price_enabled = input(f"    Enable rising price check? (y/n) [{Fore.CYAN}y{Style.RESET_ALL}]: ").strip().lower() or "y"
                if rising_price_enabled == 'y':
                    rising_price_lookback = input(f"    Lookback candles [{Fore.CYAN}3{Style.RESET_ALL}]: ").strip()
                    indicators['rising_price'] = {
                        'enabled': True,
                        'lookback_candles': int(rising_price_lookback or "3")
                    }

        # Price drop configuration
        print()
        print(f"  {Fore.YELLOW}Price Drop Configuration (OPTIONAL):{Style.RESET_ALL}")
        print("    This requires price to drop by a certain % before buying")
        price_drop_enabled = input(f"    Enable price drop requirement? (y/n) [{Fore.CYAN}n{Style.RESET_ALL}]: ").strip().lower() or "n"

        if price_drop_enabled == 'y':
            price_drop_percent = input(f"    Drop percentage required [{Fore.CYAN}0.5{Style.RESET_ALL}]: ").strip()
            price_drop_lookback = input(f"    Lookback candles [{Fore.CYAN}3{Style.RESET_ALL}]: ").strip()
            indicators['price_drop'] = {
                'enabled': True,
                'percent': float(price_drop_percent or "0.5"),
                'lookback_candles': int(price_drop_lookback or "3")
            }

        return indicators

    def update_credentials(self):
        """
        Update API credentials in the keychain.
        """
        print()
        print("=" * 70)
        print(f"{Fore.GREEN}Update API Credentials{Style.RESET_ALL}")
        print("=" * 70)
        print()
        print(f"{Fore.YELLOW}This will update the API credentials stored in your OS keychain.{Style.RESET_ALL}")
        print()

        # Select exchange
        print(f"{Fore.CYAN}Available exchanges:{Style.RESET_ALL}")
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
        exchange_id = exchange_map.get(exchange_choice, 'binance_us')

        # Get credentials
        print()
        print(f"{Fore.YELLOW}⚠️  SECURITY BEST PRACTICES:{Style.RESET_ALL}")
        print("  • Enable TRADING permissions on your API keys")
        print("  • DISABLE WITHDRAWAL permissions (important!)")
        print("  • Enable IP whitelisting if possible")
        print()

        api_key = input(f"{Fore.YELLOW}Enter API key:{Style.RESET_ALL} ").strip()
        api_secret = input(f"{Fore.YELLOW}Enter API secret:{Style.RESET_ALL} ").strip()

        passphrase = None
        if exchange_id in EXCHANGES_WITH_PASSPHRASE:
            print()
            print(f"{Fore.YELLOW}This exchange requires an API passphrase.{Style.RESET_ALL}")
            passphrase = input(f"{Fore.YELLOW}Enter API passphrase:{Style.RESET_ALL} ").strip()

        # Store in keychain
        from security.secret_provider import get_secret_provider
        secret_provider = get_secret_provider()

        secret_provider.store_key(exchange_id, api_key, api_secret, passphrase)

        print()
        print(f"{Fore.GREEN}✓ API credentials updated successfully in OS keychain{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✓ Exchange: {exchange_id}{Style.RESET_ALL}")
        print()
        input("Press Enter to continue...")

    def delete_credentials(self):
        """
        Delete API credentials from the keychain.
        """
        print()
        print("=" * 70)
        print(f"{Fore.RED}Delete API Credentials{Style.RESET_ALL}")
        print("=" * 70)
        print()
        print(f"{Fore.YELLOW}⚠️  This will delete API credentials from your OS keychain.{Style.RESET_ALL}")
        print()

        exchange_id = input(f"{Fore.YELLOW}Enter exchange ID (e.g., binance_us, coinbasepro):{Style.RESET_ALL} ").strip()

        confirm = input(f"{Fore.RED}Are you sure you want to delete credentials for {exchange_id}? (yes/no):{Style.RESET_ALL} ").strip().lower()

        if confirm == 'yes':
            from security.secret_provider import get_secret_provider
            secret_provider = get_secret_provider()

            secret_provider.delete_key(exchange_id)

            print()
            print(f"{Fore.GREEN}✓ Credentials deleted for {exchange_id}{Style.RESET_ALL}")
        else:
            print()
            print(f"{Fore.YELLOW}Cancelled.{Style.RESET_ALL}")

        print()
        input("Press Enter to continue...")

    def view_config(self, config_path: str):
        """
        Display the current configuration.
        """
        print()
        print("=" * 70)
        print(f"{Fore.GREEN}Current Configuration{Style.RESET_ALL}")
        print("=" * 70)
        print()

        try:
            config = self.load_config(config_path)

            print(f"{Fore.CYAN}Exchange:{Style.RESET_ALL} {config.get('exchange', 'N/A')}")
            print(f"{Fore.CYAN}Symbol:{Style.RESET_ALL} {config.get('symbol', 'N/A')}")
            print(f"{Fore.CYAN}Strategy:{Style.RESET_ALL} {config.get('strategy', 'N/A')}")
            print(f"{Fore.CYAN}Paper Trading:{Style.RESET_ALL} {config.get('paper_trading', 'N/A')}")

            if 'strategy_params' in config:
                print()
                print(f"{Fore.CYAN}Strategy Parameters:{Style.RESET_ALL}")
                for key, value in config['strategy_params'].items():
                    print(f"  {key}: {value}")

            if 'risk' in config:
                print()
                print(f"{Fore.CYAN}Risk Management:{Style.RESET_ALL}")
                for key, value in config['risk'].items():
                    print(f"  {key}: {value}")

            print()
            print(f"{Fore.YELLOW}Note: API credentials are stored securely in OS keychain (not shown){Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}✗ Error loading configuration: {e}{Style.RESET_ALL}")

        print()

    def edit_config(self, config_path: str):
        """
        Edit existing configuration file.
        """
        print()
        print("=" * 70)
        print(f"{Fore.GREEN}Edit Configuration{Style.RESET_ALL}")
        print("=" * 70)
        print()

        try:
            config = self.load_config(config_path)

            print(f"{Fore.CYAN}What would you like to edit?{Style.RESET_ALL}")
            print(f"  {Fore.YELLOW}1.{Style.RESET_ALL} Exchange")
            print(f"  {Fore.YELLOW}2.{Style.RESET_ALL} Trading pair (symbol)")
            print(f"  {Fore.YELLOW}3.{Style.RESET_ALL} Strategy")
            print(f"  {Fore.YELLOW}4.{Style.RESET_ALL} Paper trading mode")
            print(f"  {Fore.YELLOW}5.{Style.RESET_ALL} Cancel")
            print()

            choice = input(f"{Fore.YELLOW}Select option (1-5):{Style.RESET_ALL} ").strip()

            if choice == '1':
                print()
                print(f"{Fore.CYAN}Current exchange:{Style.RESET_ALL} {config.get('exchange', 'N/A')}")
                new_exchange = input(f"{Fore.YELLOW}Enter new exchange (e.g., binance_us, coinbasepro):{Style.RESET_ALL} ").strip()
                if new_exchange:
                    config['exchange'] = new_exchange

            elif choice == '2':
                print()
                print(f"{Fore.CYAN}Current symbol:{Style.RESET_ALL} {config.get('symbol', 'N/A')}")
                new_symbol = input(f"{Fore.YELLOW}Enter new trading pair (e.g., BTC/USD):{Style.RESET_ALL} ").strip().upper()
                if new_symbol:
                    config['symbol'] = new_symbol

            elif choice == '3':
                print()
                print(f"{Fore.CYAN}Current strategy:{Style.RESET_ALL} {config.get('strategy', 'N/A')}")
                print(f"{Fore.YELLOW}Available strategies:{Style.RESET_ALL} dca, advanced_dca, grid_trading")
                new_strategy = input(f"{Fore.YELLOW}Enter new strategy:{Style.RESET_ALL} ").strip()
                if new_strategy:
                    config['strategy'] = new_strategy

            elif choice == '4':
                print()
                print(f"{Fore.CYAN}Current paper trading:{Style.RESET_ALL} {config.get('paper_trading', 'N/A')}")
                paper_trading = input(f"{Fore.YELLOW}Enable paper trading? (y/n):{Style.RESET_ALL} ").strip().lower()
                config['paper_trading'] = (paper_trading == 'y')

            elif choice == '5':
                print(f"{Fore.YELLOW}Cancelled.{Style.RESET_ALL}")
                input("Press Enter to continue...")
                return

            # Save updated config
            if choice in ['1', '2', '3', '4']:
                self.save_config(config, config_path)
                print()
                print(f"{Fore.GREEN}✓ Configuration updated successfully{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}✗ Error editing configuration: {e}{Style.RESET_ALL}")

        print()
        input("Press Enter to continue...")

