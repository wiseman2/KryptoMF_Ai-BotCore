"""
KryptoMF Bot Core - Source Package

This package contains all the core functionality for the trading bot.
"""

__version__ = '0.2.0-dev'
__author__ = 'KryptoMF Team'

# Make subpackages easily importable
from . import core
from . import plugins
from . import cli
from . import backtesting
from . import security
from . import utils

__all__ = [
    'core',
    'plugins',
    'cli',
    'backtesting',
    'security',
    'utils',
]

