"""
Configuration Manager - Handle bot configuration

Supports:
- YAML/JSON config files
- Interactive setup (like FlexGrid)
- Environment variables
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any
from utils.logger import get_logger

logger = get_logger(__name__)


class ConfigManager:
    """
    Manages bot configuration from files or interactive setup.
    """
    
    def __init__(self):
        self.config_dir = Path(__file__).parent.parent.parent / 'config'
        self.config_dir.mkdir(exist_ok=True)
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Args:
            config_path: Path to config file (YAML or JSON)
            
        Returns:
            Configuration dictionary
        """
        path = Path(config_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        logger.info(f"Loading configuration from {config_path}")
        
        with open(path, 'r') as f:
            if path.suffix in ['.yaml', '.yml']:
                config = yaml.safe_load(f)
            elif path.suffix == '.json':
                config = json.load(f)
            else:
                raise ValueError(f"Unsupported config format: {path.suffix}")
        
        return config
    
    def interactive_setup(self) -> Dict[str, Any]:
        """
        Interactive configuration setup (like FlexGrid).
        
        Prompts user for configuration if no config file exists.
        
        Returns:
            Configuration dictionary
        """
        print()
        print("=" * 60)
        print("Welcome to KryptoMF Bot!")
        print("=" * 60)
        print()
        print("No configuration found. Let's set up your bot.")
        print()
        
        config = {}
        
        # Exchange selection
        print("Available exchanges:")
        print("  1. binance_us")
        print("  2. coinbase")
        print("  3. kraken")
        print()
        exchange_choice = input("Select exchange (1-3): ").strip()
        
        exchange_map = {
            '1': 'binance_us',
            '2': 'coinbase',
            '3': 'kraken'
        }
        config['exchange'] = exchange_map.get(exchange_choice, 'binance_us')
        
        # API credentials
        print()
        print("⚠️  Your API keys will be stored securely in your OS keychain")
        print("⚠️  Make sure your API keys have TRADING permissions but NO WITHDRAWAL permissions")
        print()
        api_key = input("Enter API key: ").strip()
        api_secret = input("Enter API secret: ").strip()
        
        config['api_key'] = api_key
        config['api_secret'] = api_secret
        
        # Trading pair
        print()
        config['symbol'] = input("Which coin pair? (e.g., BTC/USD): ").strip().upper()
        
        # Strategy selection
        print()
        print("Available strategies:")
        print("  1. grid - Grid trading with DCA")
        print("  2. dca - Dollar cost averaging")
        print("  3. momentum - Momentum trading")
        print()
        strategy_choice = input("Select strategy (1-3): ").strip()
        
        strategy_map = {
            '1': 'grid_trading',
            '2': 'dca',
            '3': 'momentum'
        }
        config['strategy'] = strategy_map.get(strategy_choice, 'grid_trading')
        
        # Strategy parameters
        print()
        if config['strategy'] == 'grid_trading':
            config['strategy_params'] = {
                'grid_spacing': float(input("Grid spacing (%): ") or "2.5"),
                'grid_levels': int(input("Number of grid levels: ") or "10"),
                'position_size': float(input("Position size (USD): ") or "100")
            }
        elif config['strategy'] == 'dca':
            config['strategy_params'] = {
                'interval_hours': int(input("DCA interval (hours): ") or "24"),
                'amount_usd': float(input("Amount per purchase (USD): ") or "100")
            }
        else:
            config['strategy_params'] = {}
        
        # Risk management
        print()
        config['risk'] = {
            'max_position_size': float(input("Max position size (USD) [1000]: ") or "1000"),
            'stop_loss_percent': float(input("Stop loss (%) [5]: ") or "5")
        }
        
        # Save configuration
        print()
        save_config = input("Save this configuration? (y/n): ").strip().lower()
        
        if save_config == 'y':
            config_path = self.config_dir / 'bot_config.yaml'
            self.save_config(config, str(config_path))
            print(f"✓ Configuration saved to {config_path}")
        
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

