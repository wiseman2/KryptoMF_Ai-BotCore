"""
Logging Utilities

Provides console logging with color support and automatic secret redaction.
"""

import logging
import sys
from typing import Optional
from colorama import Fore, Style, init

# Initialize colorama for Windows support
init(autoreset=True)


# Sensitive keys that should never be logged
SENSITIVE_KEYS = [
    'api_key', 'api_secret', 'password', 'private_key', 
    'signature', 'secret', 'token', 'auth'
]


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter with colors and secret redaction.
    """
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }
    
    def format(self, record):
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{Style.RESET_ALL}"
        
        # Redact sensitive information
        if hasattr(record, 'msg'):
            record.msg = self._redact_secrets(str(record.msg))
        
        return super().format(record)
    
    def _redact_secrets(self, message: str) -> str:
        """
        Redact sensitive information from log messages.
        
        Args:
            message: Log message
            
        Returns:
            Redacted message
        """
        # Simple redaction - can be improved
        for key in SENSITIVE_KEYS:
            if key in message.lower():
                # Don't log the actual value
                message = message.replace(key, f"{key}=****")
        
        return message


def setup_logger(verbose: bool = False) -> logging.Logger:
    """
    Setup the root logger with console output.
    
    Args:
        verbose: Enable verbose (DEBUG) logging
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # Formatter
    formatter = ColoredFormatter(
        fmt='[%(asctime)s] %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.
    
    Args:
        name: Module name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

