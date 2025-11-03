"""
KryptoMF Bot Core - Core Engine Module

This module contains the core bot engine and configuration management.
"""

__version__ = '0.2.0-dev'

from .bot_instance import BotInstance
from .config_manager import ConfigManager

__all__ = [
    'BotInstance',
    'ConfigManager',
]
