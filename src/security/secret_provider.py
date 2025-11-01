"""
Secret Provider - Secure API Key Storage

CRITICAL: This code MUST be open source for auditability.

Stores API keys securely using OS-native keychains:
- macOS: Keychain
- Windows: DPAPI/Credential Locker
- Linux: Secret Service/KWallet

Keys are NEVER transmitted to any server.
Keys are NEVER logged.
Keys are stored encrypted at rest.
"""

import platform
import keyring
from typing import Optional, Tuple
from abc import ABC, abstractmethod
from utils.logger import get_logger

logger = get_logger(__name__)


class SecretProvider(ABC):
    """
    Abstract base class for secure credential storage.
    
    All implementations MUST:
    - Store credentials encrypted
    - Use OS-native secure storage when available
    - Never transmit credentials
    - Never log credentials
    """
    
    @abstractmethod
    def store_key(self, exchange_id: str, api_key: str, api_secret: str):
        """
        Store API credentials securely.
        
        Args:
            exchange_id: Exchange identifier (e.g., 'binance_us')
            api_key: API key
            api_secret: API secret
        """
        pass
    
    @abstractmethod
    def get_key(self, exchange_id: str) -> Optional[Tuple[str, str]]:
        """
        Retrieve API credentials.
        
        Args:
            exchange_id: Exchange identifier
            
        Returns:
            Tuple of (api_key, api_secret) or None if not found
        """
        pass
    
    @abstractmethod
    def delete_key(self, exchange_id: str):
        """
        Delete stored credentials.
        
        Args:
            exchange_id: Exchange identifier
        """
        pass
    
    @abstractmethod
    def list_exchanges(self) -> list:
        """
        List exchanges with stored credentials.
        
        Returns:
            List of exchange identifiers
        """
        pass


class KeyringSecretProvider(SecretProvider):
    """
    Uses Python keyring library for OS-native secure storage.
    
    - macOS: Uses Keychain
    - Windows: Uses DPAPI/Credential Locker
    - Linux: Uses Secret Service/KWallet
    
    This is the recommended provider for most users.
    """
    
    SERVICE_NAME = 'KryptoMF_Bot'
    
    def store_key(self, exchange_id: str, api_key: str, api_secret: str):
        """
        Store API credentials in OS keychain.
        """
        logger.info(f"Storing credentials for {exchange_id} in OS keychain")
        
        # Store API key
        keyring.set_password(
            self.SERVICE_NAME,
            f"{exchange_id}_api_key",
            api_key
        )
        
        # Store API secret
        keyring.set_password(
            self.SERVICE_NAME,
            f"{exchange_id}_api_secret",
            api_secret
        )
        
        logger.info(f"✓ Credentials stored securely for {exchange_id}")
    
    def get_key(self, exchange_id: str) -> Optional[Tuple[str, str]]:
        """
        Retrieve API credentials from OS keychain.
        """
        logger.debug(f"Retrieving credentials for {exchange_id}")
        
        api_key = keyring.get_password(
            self.SERVICE_NAME,
            f"{exchange_id}_api_key"
        )
        
        api_secret = keyring.get_password(
            self.SERVICE_NAME,
            f"{exchange_id}_api_secret"
        )
        
        if api_key and api_secret:
            logger.debug(f"✓ Credentials retrieved for {exchange_id}")
            return (api_key, api_secret)
        else:
            logger.warning(f"No credentials found for {exchange_id}")
            return None
    
    def delete_key(self, exchange_id: str):
        """
        Delete API credentials from OS keychain.
        """
        logger.info(f"Deleting credentials for {exchange_id}")
        
        try:
            keyring.delete_password(
                self.SERVICE_NAME,
                f"{exchange_id}_api_key"
            )
            keyring.delete_password(
                self.SERVICE_NAME,
                f"{exchange_id}_api_secret"
            )
            logger.info(f"✓ Credentials deleted for {exchange_id}")
        except keyring.errors.PasswordDeleteError:
            logger.warning(f"No credentials found to delete for {exchange_id}")
    
    def list_exchanges(self) -> list:
        """
        List exchanges with stored credentials.
        
        Note: This is a simplified implementation.
        A full implementation would need to query the keychain.
        """
        # TODO: Implement proper keychain querying
        logger.warning("list_exchanges() not fully implemented")
        return []


def get_secret_provider() -> SecretProvider:
    """
    Get the appropriate secret provider for the current OS.
    
    Returns:
        SecretProvider instance
    """
    system = platform.system()
    
    logger.info(f"Initializing secret provider for {system}")
    
    # For now, use keyring for all platforms
    # In the future, we can add platform-specific implementations
    return KeyringSecretProvider()

