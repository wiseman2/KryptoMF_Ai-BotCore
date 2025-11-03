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

            amount_usd = float(input(f"  Amount per purchase (USD) [{Fore.CYAN}100{Style.RESET_ALL}]: ").strip() or "100")

            if dca_mode == "2":
                # Indicator-based DCA
                print()
                print(f"  {Fore.YELLOW}Configure Technical Indicators:{Style.RESET_ALL}")
                indicators = self._configure_indicators()

                config['strategy_params'] = {
                    'use_indicators': True,
                    'amount_usd': amount_usd,
                    'indicators': indicators
                }
            else:
                # Time-based DCA
                interval_hours = int(input(f"  DCA interval (hours) [{Fore.CYAN}24{Style.RESET_ALL}]: ").strip() or "24")
                config['strategy_params'] = {
                    'interval_hours': interval_hours,
                    'amount_usd': amount_usd
                }
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

        # Paper trading
        print()
        print(f"{Fore.GREEN}Step 10: Trading Mode{Style.RESET_ALL}")
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
            # Multiple indicators (recommended)
            print()
            print(f"  {Fore.YELLOW}Using recommended multi-indicator setup:{Style.RESET_ALL}")
            print("    • RSI (14 period, 30/70 thresholds)")
            print("    • Stochastic RSI (14 period, 20/80 thresholds)")
            print("    • EMA crossover (12/26 periods)")
            print()

            use_defaults = input(f"  Use default settings? (y/n) [{Fore.CYAN}y{Style.RESET_ALL}]: ").strip().lower()

            if use_defaults != 'n':
                # Use defaults
                indicators = {
                    'rsi': {
                        'enabled': True,
                        'period': 14,
                        'oversold': 30,
                        'overbought': 70,
                        'check_rising': True
                    },
                    'stoch_rsi': {
                        'enabled': True,
                        'period': 14,
                        'oversold': 20,
                        'overbought': 80
                    },
                    'ema': {
                        'enabled': True,
                        'short_period': 12,
                        'long_period': 26
                    }
                }
            else:
                # Custom configuration for each
                indicators = {}

                # RSI
                print()
                print(f"  {Fore.YELLOW}RSI Configuration:{Style.RESET_ALL}")
                rsi_period = input(f"    Period [{Fore.CYAN}14{Style.RESET_ALL}]: ").strip()
                rsi_oversold = input(f"    Oversold [{Fore.CYAN}30{Style.RESET_ALL}]: ").strip()
                rsi_overbought = input(f"    Overbought [{Fore.CYAN}70{Style.RESET_ALL}]: ").strip()
                rsi_rising = input(f"    Check if RSI is rising? (y/n) [{Fore.CYAN}y{Style.RESET_ALL}]: ").strip().lower() or "y"
                indicators['rsi'] = {
                    'enabled': True,
                    'period': int(rsi_period or "14"),
                    'oversold': float(rsi_oversold or "30"),
                    'overbought': float(rsi_overbought or "70"),
                    'check_rising': rsi_rising == 'y'
                }

                # Stochastic RSI
                print()
                print(f"  {Fore.YELLOW}Stochastic RSI Configuration:{Style.RESET_ALL}")
                stoch_period = input(f"    Period [{Fore.CYAN}14{Style.RESET_ALL}]: ").strip()
                stoch_oversold = input(f"    Oversold [{Fore.CYAN}20{Style.RESET_ALL}]: ").strip()
                stoch_overbought = input(f"    Overbought [{Fore.CYAN}80{Style.RESET_ALL}]: ").strip()
                indicators['stoch_rsi'] = {
                    'enabled': True,
                    'period': int(stoch_period or "14"),
                    'oversold': float(stoch_oversold or "20"),
                    'overbought': float(stoch_overbought or "80")
                }

                # EMA
                print()
                print(f"  {Fore.YELLOW}EMA Configuration:{Style.RESET_ALL}")
                ema_short = input(f"    Short period [{Fore.CYAN}12{Style.RESET_ALL}]: ").strip()
                ema_long = input(f"    Long period [{Fore.CYAN}26{Style.RESET_ALL}]: ").strip()
                indicators['ema'] = {
                    'enabled': True,
                    'short_period': int(ema_short or "12"),
                    'long_period': int(ema_long or "26")
                }

        return indicators

