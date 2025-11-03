"""
Plugin System - Open Source

Base classes for all plugins:
- Exchange plugins
- Strategy plugins
- Indicator plugins
- Signal plugins
"""

from .indicators import TechnicalIndicators

__all__ = [
    'TechnicalIndicators',
]
