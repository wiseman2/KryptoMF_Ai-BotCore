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

    Supports multiple credential formats:
    - API Key + Secret (Binance, Kraken, etc.)
    - API Key + Secret + Passphrase (Coinbase Pro, KuCoin, etc.)
    """

    @abstractmethod
    def store_key(
        self,
        exchange_id: str,
        api_key: str,
        api_secret: str,
        passphrase: Optional[str] = None
    ):
        """
        Store API credentials securely.

        Args:
            exchange_id: Exchange identifier (e.g., 'binance_us', 'coinbase_pro')
            api_key: API key
            api_secret: API secret
            passphrase: API passphrase (optional, required by some exchanges)
        """
        pass

    @abstractmethod
    def get_key(self, exchange_id: str) -> Optional[Tuple[str, str, Optional[str]]]:
        """
        Retrieve API credentials.

        Args:
            exchange_id: Exchange identifier

        Returns:
            Tuple of (api_key, api_secret, passphrase) or None if not found
            passphrase will be None if not stored
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

    Supports exchanges that require:
    - API Key + Secret (Binance, Kraken, etc.)
    - API Key + Secret + Passphrase (Coinbase Pro, KuCoin, etc.)
    """

    SERVICE_NAME = 'KryptoMF_Bot'

    def store_key(
        self,
        exchange_id: str,
        api_key: str,
        api_secret: str,
        passphrase: Optional[str] = None
    ):
        """
        Store API credentials in OS keychain.

        Args:
            exchange_id: Exchange identifier
            api_key: API key
            api_secret: API secret
            passphrase: API passphrase (optional, for Coinbase Pro, KuCoin, etc.)
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

        # Store passphrase if provided
        if passphrase:
            keyring.set_password(
                self.SERVICE_NAME,
                f"{exchange_id}_passphrase",
                passphrase
            )
            logger.debug(f"Stored passphrase for {exchange_id}")

        # Add to exchanges list
        self._add_to_exchanges_list(exchange_id)

        logger.info(f"✓ Credentials stored securely for {exchange_id}")

    def get_key(self, exchange_id: str) -> Optional[Tuple[str, str, Optional[str]]]:
        """
        Retrieve API credentials from OS keychain.

        Returns:
            Tuple of (api_key, api_secret, passphrase) or None if not found
            passphrase will be None if not stored
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

        # Try to get passphrase (may not exist for all exchanges)
        passphrase = keyring.get_password(
            self.SERVICE_NAME,
            f"{exchange_id}_passphrase"
        )

        if api_key and api_secret:
            logger.debug(f"✓ Credentials retrieved for {exchange_id}")
            return (api_key, api_secret, passphrase)
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

            # Try to delete passphrase (may not exist)
            try:
                keyring.delete_password(
                    self.SERVICE_NAME,
                    f"{exchange_id}_passphrase"
                )
            except keyring.errors.PasswordDeleteError:
                pass  # Passphrase didn't exist, that's OK

            # Remove from exchanges list
            self._remove_from_exchanges_list(exchange_id)

            logger.info(f"✓ Credentials deleted for {exchange_id}")
        except keyring.errors.PasswordDeleteError:
            logger.warning(f"No credentials found to delete for {exchange_id}")
    
    def list_exchanges(self) -> list:
        """
        List exchanges with stored credentials.

        Note: Keyring doesn't provide a way to list all stored credentials,
        so we maintain a list in a separate key.
        """
        try:
            exchanges_str = keyring.get_password(
                self.SERVICE_NAME,
                "_exchanges_list"
            )
            if exchanges_str:
                return exchanges_str.split(',')
            return []
        except Exception as e:
            logger.error(f"Error listing exchanges: {e}")
            return []

    def _add_to_exchanges_list(self, exchange_id: str):
        """Add exchange to the list of stored exchanges."""
        exchanges = self.list_exchanges()
        if exchange_id not in exchanges:
            exchanges.append(exchange_id)
            keyring.set_password(
                self.SERVICE_NAME,
                "_exchanges_list",
                ','.join(exchanges)
            )

    def _remove_from_exchanges_list(self, exchange_id: str):
        """Remove exchange from the list of stored exchanges."""
        exchanges = self.list_exchanges()
        if exchange_id in exchanges:
            exchanges.remove(exchange_id)
            if exchanges:
                keyring.set_password(
                    self.SERVICE_NAME,
                    "_exchanges_list",
                    ','.join(exchanges)
                )
            else:
                try:
                    keyring.delete_password(self.SERVICE_NAME, "_exchanges_list")
                except:
                    pass


class EncryptedFileProvider(SecretProvider):
    """
    Fallback provider using encrypted local file storage.

    Uses Fernet (symmetric encryption) with a key derived from the machine.
    This is less secure than OS keychain but works everywhere.

    ⚠️ WARNING: This is a fallback. Use OS keychain when possible.
    """

    def __init__(self, storage_path: str = None):
        """
        Initialize encrypted file provider.

        Args:
            storage_path: Path to store encrypted credentials file
        """
        from cryptography.fernet import Fernet
        import json
        from pathlib import Path

        self.json = json
        self.Fernet = Fernet

        if storage_path is None:
            # Use user's home directory
            home = Path.home()
            storage_path = home / '.kryptomf' / 'credentials.enc'

        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Get or create encryption key
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)

        logger.warning("Using encrypted file storage (fallback)")
        logger.warning("For better security, install keyring support for your OS")

    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key."""
        key_path = self.storage_path.parent / '.key'

        if key_path.exists():
            with open(key_path, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            key = self.Fernet.generate_key()
            with open(key_path, 'wb') as f:
                f.write(key)
            # Set restrictive permissions (Unix only)
            try:
                import os
                os.chmod(key_path, 0o600)
            except:
                pass
            return key

    def _load_credentials(self) -> dict:
        """Load and decrypt credentials file."""
        if not self.storage_path.exists():
            return {}

        try:
            with open(self.storage_path, 'rb') as f:
                encrypted_data = f.read()

            decrypted_data = self.cipher.decrypt(encrypted_data)
            return self.json.loads(decrypted_data.decode())
        except Exception as e:
            logger.error(f"Error loading credentials: {e}")
            return {}

    def _save_credentials(self, credentials: dict):
        """Encrypt and save credentials file."""
        try:
            json_data = self.json.dumps(credentials).encode()
            encrypted_data = self.cipher.encrypt(json_data)

            with open(self.storage_path, 'wb') as f:
                f.write(encrypted_data)

            # Set restrictive permissions (Unix only)
            try:
                import os
                os.chmod(self.storage_path, 0o600)
            except:
                pass
        except Exception as e:
            logger.error(f"Error saving credentials: {e}")
            raise

    def store_key(
        self,
        exchange_id: str,
        api_key: str,
        api_secret: str,
        passphrase: Optional[str] = None
    ):
        """
        Store API credentials in encrypted file.

        Args:
            exchange_id: Exchange identifier
            api_key: API key
            api_secret: API secret
            passphrase: API passphrase (optional)
        """
        logger.info(f"Storing credentials for {exchange_id} in encrypted file")

        credentials = self._load_credentials()
        credentials[exchange_id] = {
            'api_key': api_key,
            'api_secret': api_secret
        }

        if passphrase:
            credentials[exchange_id]['passphrase'] = passphrase

        self._save_credentials(credentials)

        logger.info(f"✓ Credentials stored for {exchange_id}")

    def get_key(self, exchange_id: str) -> Optional[Tuple[str, str, Optional[str]]]:
        """
        Retrieve API credentials from encrypted file.

        Returns:
            Tuple of (api_key, api_secret, passphrase) or None if not found
        """
        logger.debug(f"Retrieving credentials for {exchange_id}")

        credentials = self._load_credentials()

        if exchange_id in credentials:
            creds = credentials[exchange_id]
            logger.debug(f"✓ Credentials retrieved for {exchange_id}")
            return (
                creds['api_key'],
                creds['api_secret'],
                creds.get('passphrase')  # May be None
            )
        else:
            logger.warning(f"No credentials found for {exchange_id}")
            return None

    def delete_key(self, exchange_id: str):
        """Delete API credentials from encrypted file."""
        logger.info(f"Deleting credentials for {exchange_id}")

        credentials = self._load_credentials()

        if exchange_id in credentials:
            del credentials[exchange_id]
            self._save_credentials(credentials)
            logger.info(f"✓ Credentials deleted for {exchange_id}")
        else:
            logger.warning(f"No credentials found to delete for {exchange_id}")

    def list_exchanges(self) -> list:
        """List exchanges with stored credentials."""
        credentials = self._load_credentials()
        return list(credentials.keys())


def get_secret_provider(use_fallback: bool = False) -> SecretProvider:
    """
    Get the appropriate secret provider for the current OS.

    Args:
        use_fallback: Force use of encrypted file fallback

    Returns:
        SecretProvider instance
    """
    system = platform.system()

    logger.info(f"Initializing secret provider for {system}")

    if use_fallback:
        logger.warning("Using fallback encrypted file storage")
        return EncryptedFileProvider()

    try:
        # Try to use OS keychain
        provider = KeyringSecretProvider()

        # Test if keyring is working
        test_key = "_test_keyring"
        try:
            keyring.set_password(provider.SERVICE_NAME, test_key, "test")
            keyring.delete_password(provider.SERVICE_NAME, test_key)
            logger.info(f"✓ Using OS keychain for {system}")
            return provider
        except Exception as e:
            logger.warning(f"OS keychain not available: {e}")
            logger.warning("Falling back to encrypted file storage")
            return EncryptedFileProvider()

    except Exception as e:
        logger.error(f"Error initializing keyring: {e}")
        logger.warning("Falling back to encrypted file storage")
        return EncryptedFileProvider()

