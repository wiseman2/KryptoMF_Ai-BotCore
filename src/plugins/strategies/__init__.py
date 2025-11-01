"""
Trading Strategy Plugins

Basic trading strategies included in the open source core.
"""

from .grid_trading import GridTradingStrategy
from .dca import DCAStrategy

__all__ = ['GridTradingStrategy', 'DCAStrategy']

