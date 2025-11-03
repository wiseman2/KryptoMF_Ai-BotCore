"""
Base Plugin Classes
"""

from .exchange_plugin import ExchangePlugin
from .strategy_plugin import StrategyPlugin

__all__ = [
    'ExchangePlugin',
    'StrategyPlugin',
]
