"""
Trading Strategy Plugins

Auto-discovers and registers all strategy plugins in this directory.

To add a new strategy:
1. Create a new .py file in src/plugins/strategies/
2. Define a class that inherits from StrategyPlugin
3. The class will be automatically discovered and registered

Example:
    # src/plugins/strategies/my_strategy.py
    from plugins.base.strategy_plugin import StrategyPlugin

    class MyStrategy(StrategyPlugin):
        def analyze(self, market_data):
            # Your strategy logic
            pass

The strategy will be available as 'my_strategy' in the configuration.
"""

import os
import importlib
import inspect
from pathlib import Path
from plugins.base.strategy_plugin import StrategyPlugin
from utils.logger import get_logger

logger = get_logger(__name__)

# Dictionary to store discovered strategies: {strategy_name: StrategyClass}
STRATEGIES = {}


def discover_strategies():
    """
    Auto-discover all strategy plugins in this directory.

    Scans all .py files in the strategies directory and imports any classes
    that inherit from StrategyPlugin.

    Returns:
        Dict[str, type]: Dictionary mapping strategy names to strategy classes
    """
    strategies_dir = Path(__file__).parent
    strategy_files = [f for f in os.listdir(strategies_dir)
                     if f.endswith('.py') and f != '__init__.py']

    discovered = {}

    for filename in strategy_files:
        module_name = filename[:-3]  # Remove .py extension

        try:
            # Import the module
            module = importlib.import_module(f'plugins.strategies.{module_name}')

            # Find all classes in the module that inherit from StrategyPlugin
            for name, obj in inspect.getmembers(module, inspect.isclass):
                # Check if it's a StrategyPlugin subclass (but not StrategyPlugin itself)
                if issubclass(obj, StrategyPlugin) and obj is not StrategyPlugin:
                    # Use the module name (filename) as the strategy name
                    discovered[module_name] = obj
                    logger.debug(f"Discovered strategy: {module_name} -> {name}")
                    break  # Only take the first StrategyPlugin subclass per file

        except Exception as e:
            logger.warning(f"Failed to load strategy from {filename}: {e}")

    return discovered


def get_strategy_class(strategy_name: str):
    """
    Get a strategy class by name.

    Args:
        strategy_name: Name of the strategy (e.g., 'dca', 'grid_trading', 'advanced_dca')

    Returns:
        Strategy class

    Raises:
        ValueError: If strategy not found
    """
    if strategy_name not in STRATEGIES:
        raise ValueError(
            f"Unknown strategy: {strategy_name}. "
            f"Available strategies: {', '.join(STRATEGIES.keys())}"
        )

    return STRATEGIES[strategy_name]


def list_strategies():
    """
    Get list of all available strategy names.

    Returns:
        List[str]: List of strategy names
    """
    return list(STRATEGIES.keys())


# Auto-discover strategies on module import
STRATEGIES = discover_strategies()

logger.info(f"Loaded {len(STRATEGIES)} strategies: {', '.join(STRATEGIES.keys())}")

__all__ = ['STRATEGIES', 'get_strategy_class', 'list_strategies', 'discover_strategies']

