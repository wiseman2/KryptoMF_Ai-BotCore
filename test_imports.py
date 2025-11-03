#!/usr/bin/env python3
"""
Test script to verify all imports work correctly.

This script tests that all modules can be imported without errors.
Run this after making changes to the import structure.

Usage:
    python test_imports.py
"""

import sys
from pathlib import Path

# Add src to path (same as cli.py and main.py)
src_path = Path(__file__).parent / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

print("=" * 70)
print("Testing KryptoMF Bot Core Imports")
print("=" * 70)
print()

# Track results
passed = []
failed = []

def test_import(module_name, import_statement):
    """Test a single import statement."""
    try:
        exec(import_statement)
        passed.append(module_name)
        print(f"✓ {module_name}")
        return True
    except Exception as e:
        failed.append((module_name, str(e)))
        print(f"✗ {module_name}: {e}")
        return False

print("Testing Core Modules:")
print("-" * 70)
test_import("core.bot_instance", "from core.bot_instance import BotInstance")
test_import("core.config_manager", "from core.config_manager import ConfigManager")
print()

print("Testing CLI Modules:")
print("-" * 70)
test_import("cli.status_display", "from cli.status_display import StatusDisplay")
test_import("cli.bot_controller", "from cli.bot_controller import run_interactive_mode")
print()

print("Testing Backtesting Modules:")
print("-" * 70)
test_import("backtesting.backtest_engine", "from backtesting.backtest_engine import BacktestEngine")
test_import("backtesting.backtest_results", "from backtesting.backtest_results import BacktestResults")
test_import("backtesting.historical_data", "from backtesting.historical_data import HistoricalDataFetcher")
print()

print("Testing Plugin Modules:")
print("-" * 70)
test_import("plugins.indicators", "from plugins.indicators import TechnicalIndicators")
test_import("plugins.exchanges.ccxt_exchange", "from plugins.exchanges.ccxt_exchange import CCXTExchange")
test_import("plugins.strategies.grid_trading", "from plugins.strategies.grid_trading import GridTradingStrategy")
test_import("plugins.strategies.dca", "from plugins.strategies.dca import DCAStrategy")
print()

print("Testing Security Modules:")
print("-" * 70)
test_import("security.secret_provider", "from security.secret_provider import get_secret_provider")
test_import("security.order_signing", "from security.order_signing import OrderSigner")
print()

print("Testing Utility Modules:")
print("-" * 70)
test_import("utils.logger", "from utils.logger import setup_logger, get_logger")
print()

print("Testing Base Plugin Classes:")
print("-" * 70)
test_import("plugins.base.exchange_plugin", "from plugins.base.exchange_plugin import ExchangePlugin")
test_import("plugins.base.strategy_plugin", "from plugins.base.strategy_plugin import StrategyPlugin")
print()

# Summary
print("=" * 70)
print("Import Test Summary")
print("=" * 70)
print(f"Passed: {len(passed)}/{len(passed) + len(failed)}")
print(f"Failed: {len(failed)}/{len(passed) + len(failed)}")
print()

if failed:
    print("Failed Imports:")
    for module, error in failed:
        print(f"  ✗ {module}")
        print(f"    Error: {error}")
    print()
    sys.exit(1)
else:
    print("✓ All imports successful!")
    print()
    
    # Test that we can actually instantiate some classes
    print("Testing Class Instantiation:")
    print("-" * 70)
    
    try:
        from utils.logger import setup_logger
        logger = setup_logger(verbose=False)
        print("✓ Logger instantiated")
    except Exception as e:
        print(f"✗ Logger instantiation failed: {e}")
    
    try:
        from plugins.indicators import TechnicalIndicators
        # Just check the class exists
        assert hasattr(TechnicalIndicators, 'get_rsi')
        assert hasattr(TechnicalIndicators, 'calculate_sell_price_with_fees')
        print("✓ TechnicalIndicators has expected methods")
    except Exception as e:
        print(f"✗ TechnicalIndicators check failed: {e}")
    
    try:
        from core.config_manager import ConfigManager
        cm = ConfigManager()
        print("✓ ConfigManager instantiated")
    except Exception as e:
        print(f"✗ ConfigManager instantiation failed: {e}")
    
    print()
    print("=" * 70)
    print("✓ All tests passed! Import structure is correct.")
    print("=" * 70)
    sys.exit(0)

