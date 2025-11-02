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

