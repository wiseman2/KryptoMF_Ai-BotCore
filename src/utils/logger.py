"""
Logging Utilities

Provides console logging with color support and automatic secret redaction.

CRITICAL: This code MUST redact ALL sensitive information from logs.

Sensitive data includes:
- API keys and secrets
- Passwords and tokens
- Private keys and signatures
- Any data that could compromise security

This prevents:
- Accidental exposure in log files
- Credential leakage in error messages
- Security breaches from log analysis
"""

import logging
import sys
import re
from typing import Optional, List, Pattern
from pathlib import Path
from logging.handlers import RotatingFileHandler
from colorama import Fore, Style, init

# Initialize colorama for Windows support
init(autoreset=True)


# Sensitive keys that should never be logged
SENSITIVE_KEYS = [
    'api_key', 'apikey', 'api_secret', 'apisecret', 'secret',
    'password', 'passwd', 'pwd',
    'private_key', 'privatekey', 'priv_key',
    'signature', 'sign',
    'token', 'access_token', 'refresh_token', 'auth_token',
    'auth', 'authorization',
    'passphrase', 'pass_phrase',
    'key', 'secret_key', 'secretkey',
    'credential', 'credentials',
]

# Patterns for detecting sensitive data in strings
SENSITIVE_PATTERNS: List[Pattern] = [
    # API keys (long alphanumeric strings)
    re.compile(r'["\']?(?:api[_-]?key|apikey)["\']?\s*[:=]\s*["\']?([A-Za-z0-9_\-]{20,})["\']?', re.IGNORECASE),

    # Secrets (long alphanumeric strings)
    re.compile(r'["\']?(?:api[_-]?secret|apisecret|secret)["\']?\s*[:=]\s*["\']?([A-Za-z0-9_\-/+=]{20,})["\']?', re.IGNORECASE),

    # Tokens (JWT-like patterns)
    re.compile(r'["\']?(?:token|access[_-]?token|auth[_-]?token)["\']?\s*[:=]\s*["\']?([A-Za-z0-9_\-\.]{20,})["\']?', re.IGNORECASE),

    # Passwords
    re.compile(r'["\']?(?:password|passwd|pwd)["\']?\s*[:=]\s*["\']?([^\s"\']{6,})["\']?', re.IGNORECASE),

    # Private keys (PEM format)
    re.compile(r'-----BEGIN (?:RSA |EC )?PRIVATE KEY-----.*?-----END (?:RSA |EC )?PRIVATE KEY-----', re.DOTALL),

    # Signatures (hex strings)
    re.compile(r'["\']?signature["\']?\s*[:=]\s*["\']?([A-Fa-f0-9]{32,})["\']?', re.IGNORECASE),

    # Authorization headers
    re.compile(r'Authorization:\s*(?:Bearer|Basic)\s+([A-Za-z0-9_\-\.=/+]+)', re.IGNORECASE),
]


class SecureFilter(logging.Filter):
    """
    Logging filter that redacts sensitive information.

    This filter is applied to ALL log records to ensure
    no sensitive data is ever written to logs.
    """

    def filter(self, record):
        """
        Filter and redact sensitive information from log record.

        Args:
            record: Log record

        Returns:
            True (always allow the record, but redact it first)
        """
        # Redact message
        if hasattr(record, 'msg'):
            record.msg = redact_secrets(str(record.msg))

        # Redact args (if any)
        if hasattr(record, 'args') and record.args:
            if isinstance(record.args, dict):
                record.args = {k: redact_secrets(str(v)) for k, v in record.args.items()}
            elif isinstance(record.args, (list, tuple)):
                record.args = tuple(redact_secrets(str(arg)) for arg in record.args)

        return True


def redact_secrets(message: str) -> str:
    """
    Redact sensitive information from a string.

    This function uses multiple strategies:
    1. Pattern matching for common secret formats
    2. Key-value pair detection
    3. Dictionary/JSON detection

    Args:
        message: String that may contain sensitive data

    Returns:
        String with sensitive data redacted
    """
    if not message:
        return message

    # Strategy 1: Pattern-based redaction
    for pattern in SENSITIVE_PATTERNS:
        message = pattern.sub(lambda m: m.group(0).replace(m.group(1), '****REDACTED****'), message)

    # Strategy 2: Key-value pair redaction
    # Look for patterns like "api_key: value" or "api_key=value"
    for key in SENSITIVE_KEYS:
        # Match key followed by : or = and capture the value
        patterns = [
            # JSON-style: "key": "value"
            re.compile(rf'["\']?{re.escape(key)}["\']?\s*:\s*["\']([^"\']+)["\']', re.IGNORECASE),
            # Assignment style: key=value
            re.compile(rf'{re.escape(key)}\s*=\s*["\']?([^\s,\)}}]+)["\']?', re.IGNORECASE),
            # Dictionary style: 'key': 'value'
            re.compile(rf"'{re.escape(key)}':\s*'([^']+)'", re.IGNORECASE),
        ]

        for pattern in patterns:
            message = pattern.sub(lambda m: m.group(0).replace(m.group(1), '****'), message)

    # Strategy 3: Detect and redact long alphanumeric strings that look like secrets
    # (Only if they appear after certain keywords)
    secret_context_pattern = re.compile(
        r'(?:key|secret|token|password|auth|signature|credential)[\s:=]+([A-Za-z0-9_\-/+=]{32,})',
        re.IGNORECASE
    )
    message = secret_context_pattern.sub(lambda m: m.group(0).replace(m.group(1), '****REDACTED****'), message)

    return message


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter with colors and secret redaction.

    This formatter adds color to log levels and ensures
    all messages are redacted before being formatted.
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

        # Note: Redaction is handled by SecureFilter, not here
        # This ensures redaction happens before any formatting

        return super().format(record)


def setup_logger(verbose: bool = False, log_file: Optional[str] = None) -> logging.Logger:
    """
    Setup the root logger with console output and optional file logging.

    Args:
        verbose: Enable verbose (DEBUG) logging
        log_file: Optional path to log file. If None, uses default 'logs/bot.log'

    Returns:
        Configured logger
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Remove existing handlers
    logger.handlers.clear()

    # Add secure filter to prevent credential leakage
    secure_filter = SecureFilter()

    # Console handler (with colors)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    console_handler.addFilter(secure_filter)

    # Colored formatter for console
    console_formatter = ColoredFormatter(
        fmt='[%(asctime)s] %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (without colors, with rotation)
    if log_file is None:
        # Default log directory
        log_dir = Path(__file__).parent.parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / 'bot.log'
    else:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

    # Rotating file handler: 10MB max, keep 10 backup files
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=10,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)  # Always log DEBUG to file
    file_handler.addFilter(secure_filter)

    # Plain formatter for file (no colors)
    file_formatter = logging.Formatter(
        fmt='[%(asctime)s] %(levelname)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    logger.info(f"Logging to file: {log_file}")

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


def setup_session_logger(mode: str, symbol: str = None, strategy: str = None) -> Path:
    """
    Setup a session-specific log file for backtest, live, or paper trading.

    Creates a dedicated log file with timestamp and session details.

    Args:
        mode: Trading mode ('backtest', 'live', 'paper')
        symbol: Trading symbol (e.g., 'BTC/USD')
        strategy: Strategy name (e.g., 'advanced_dca')

    Returns:
        Path to the session log file
    """
    from datetime import datetime

    # Create logs directory
    log_dir = Path(__file__).parent.parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)

    # Create session-specific subdirectory
    session_dir = log_dir / mode
    session_dir.mkdir(exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Build filename parts
    parts = [mode, timestamp]
    if symbol:
        parts.append(symbol.replace('/', '-'))
    if strategy:
        parts.append(strategy)

    filename = '_'.join(parts) + '.log'
    log_file = session_dir / filename

    # Add file handler to root logger
    logger = logging.getLogger()

    # Create session file handler
    session_handler = RotatingFileHandler(
        log_file,
        maxBytes=50 * 1024 * 1024,  # 50 MB for session logs
        backupCount=5,
        encoding='utf-8'
    )
    session_handler.setLevel(logging.DEBUG)
    session_handler.addFilter(SecureFilter())

    # Plain formatter for file
    session_formatter = logging.Formatter(
        fmt='[%(asctime)s] %(levelname)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    session_handler.setFormatter(session_formatter)
    logger.addHandler(session_handler)

    logger.info(f"Session log created: {log_file}")

    return log_file

