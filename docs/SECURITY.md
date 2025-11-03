# Security Documentation

## Overview

KryptoMF Bot Core implements security-critical features that are **100% open source** for auditability and trust. This document explains how credentials are stored, how API requests are signed, and how sensitive data is protected.

## 🔐 Credential Storage

### Supported Storage Methods

#### 1. OS Keychain (Recommended)

The bot uses your operating system's native secure storage:

- **macOS**: Keychain Access
- **Windows**: DPAPI/Credential Locker  
- **Linux**: Secret Service API (GNOME Keyring, KWallet)

**Benefits:**
- ✅ Encrypted at rest by the OS
- ✅ Protected by your system password
- ✅ Never stored in plain text
- ✅ Isolated from other applications
- ✅ Survives bot restarts

#### 2. Encrypted File (Fallback)

If OS keychain is unavailable, the bot uses encrypted file storage:

- Uses Fernet (symmetric encryption)
- Encryption key derived from machine
- Stored in `~/.kryptomf/credentials.enc`
- File permissions set to 0600 (owner only)

**⚠️ Warning:** Less secure than OS keychain. Use only if keychain is unavailable.

### Supported Credential Formats

Different exchanges require different credential formats:

#### Format 1: API Key + Secret
Used by: Binance, Binance.US, Kraken, Bitfinex, etc.

```python
from security.secret_provider import get_secret_provider

provider = get_secret_provider()
provider.store_key(
    exchange_id='binance_us',
    api_key='your_api_key_here',
    api_secret='your_api_secret_here'
)
```

#### Format 2: API Key + Secret + Passphrase
Used by: Coinbase Pro, KuCoin, OKX, etc.

```python
provider.store_key(
    exchange_id='coinbase_pro',
    api_key='your_api_key_here',
    api_secret='your_api_secret_here',
    passphrase='your_passphrase_here'
)
```

### Retrieving Credentials

```python
# Returns tuple: (api_key, api_secret, passphrase)
# passphrase will be None if not stored
credentials = provider.get_key('binance_us')

if credentials:
    api_key, api_secret, passphrase = credentials
    print(f"Retrieved credentials for exchange")
else:
    print("No credentials found")
```

### Deleting Credentials

```python
provider.delete_key('binance_us')
```

### Listing Stored Exchanges

```python
exchanges = provider.list_exchanges()
print(f"Stored credentials for: {exchanges}")
```

## 🔏 Order Signing

All API requests to exchanges must be signed to prove authenticity. The bot supports multiple signing methods.

### HMAC-SHA256 (Most Common)

Used by: Binance, Binance.US, Kraken, and most exchanges

```python
from security.order_signing import get_order_signer

signer = get_order_signer('binance_us')

# Sign a request
params = {
    'symbol': 'BTCUSD',
    'side': 'BUY',
    'type': 'LIMIT',
    'quantity': 0.001,
    'price': 50000
}

signed_params, headers = signer.sign_request(
    method='POST',
    endpoint='/api/v3/order',
    params=params,
    api_secret='your_secret_here'
)

# signed_params now includes timestamp and signature
# Use these in your API request
```

### Coinbase Pro Signing

Coinbase Pro uses a different signing format:

```python
signer = get_order_signer('coinbase_pro')

signed_params, headers = signer.sign_request(
    method='POST',
    endpoint='/orders',
    params=params,
    api_secret='your_base64_secret',
    api_passphrase='your_passphrase'
)

# Headers include:
# - CB-ACCESS-SIGN
# - CB-ACCESS-TIMESTAMP
# - CB-ACCESS-KEY
# - CB-ACCESS-PASSPHRASE
```

### Security Features

All signing implementations include:

1. **Timestamp/Nonce**: Prevents replay attacks
2. **Request Ordering**: Ensures consistent signatures
3. **HMAC Verification**: Prevents tampering
4. **Constant-Time Comparison**: Prevents timing attacks

## 🛡️ Secrets Redaction

The bot **automatically redacts** all sensitive information from logs.

### What Gets Redacted

- API keys and secrets
- Passwords and passphrases
- Private keys
- Signatures
- Tokens and authorization headers
- Any long alphanumeric strings after sensitive keywords

### Redaction Examples

```python
# Original log message:
"Storing api_key=abc123xyz456 for exchange"

# Redacted log message:
"Storing api_key=**** for exchange"
```

```python
# Original:
"Request headers: {'Authorization': 'Bearer eyJhbGc...'}"

# Redacted:
"Request headers: {'Authorization': 'Bearer ****REDACTED****'}"
```

### How It Works

1. **SecureFilter**: Applied to all log records
2. **Pattern Matching**: Detects common secret formats
3. **Key-Value Detection**: Finds sensitive key-value pairs
4. **Context Analysis**: Redacts strings that look like secrets

### Testing Redaction

```python
from utils.logger import redact_secrets

# Test redaction
message = "api_key=abc123 secret=xyz789"
redacted = redact_secrets(message)
print(redacted)  # "api_key=**** secret=****"
```

## 🔒 Best Practices

### 1. Use Read-Only API Keys When Possible

For strategies that only need to read data (not place orders):
- Create read-only API keys on the exchange
- Limits damage if credentials are compromised

### 2. Use IP Whitelisting

Many exchanges allow IP whitelisting:
- Restrict API keys to your server's IP
- Prevents use from other locations

### 3. Set Withdrawal Restrictions

On exchanges that support it:
- Disable withdrawals for API keys
- Even if compromised, funds stay on exchange

### 4. Use Separate API Keys Per Bot

- Create different API keys for each bot instance
- Makes it easier to revoke if needed
- Better tracking of which bot did what

### 5. Regularly Rotate API Keys

- Change API keys periodically (e.g., every 90 days)
- Reduces window of opportunity if compromised

### 6. Monitor API Key Usage

- Check exchange logs for unexpected activity
- Set up alerts for unusual patterns

### 7. Never Commit Credentials to Git

- Use `.gitignore` for config files with credentials
- Use environment variables or secure storage
- Never hardcode credentials in source code

## 🚨 Security Checklist

Before going live with real funds:

- [ ] API keys stored in OS keychain (not plain text files)
- [ ] API keys have IP whitelist enabled
- [ ] API keys have withdrawal disabled
- [ ] Using read-only keys for non-trading bots
- [ ] Logs are being redacted (check log files)
- [ ] Using latest version of the bot
- [ ] Reviewed all strategy configurations
- [ ] Tested with paper trading first
- [ ] Have backup of configuration
- [ ] Know how to emergency stop the bot

## 📚 Code References

### Secret Provider
- **File**: `src/security/secret_provider.py`
- **Classes**: `SecretProvider`, `KeyringSecretProvider`, `EncryptedFileProvider`
- **Function**: `get_secret_provider()`

### Order Signing
- **File**: `src/security/order_signing.py`
- **Classes**: `OrderSigner`, `HMACOrderSigner`, `BinanceOrderSigner`, `CoinbaseOrderSigner`
- **Function**: `get_order_signer(exchange)`

### Secrets Redaction
- **File**: `src/utils/logger.py`
- **Class**: `SecureFilter`
- **Function**: `redact_secrets(message)`

## ❓ FAQ

### Q: Where are my credentials stored?

**A:** On macOS: Keychain Access. On Windows: Credential Manager. On Linux: GNOME Keyring or KWallet.

### Q: Can I see my stored credentials?

**A:** Yes, using your OS's credential manager:
- macOS: Open "Keychain Access" app, search for "KryptoMF_Bot"
- Windows: Open "Credential Manager", look under "Generic Credentials"
- Linux: Use `seahorse` (GNOME) or KWallet Manager (KDE)

### Q: What if I lose my credentials?

**A:** You'll need to create new API keys on the exchange and store them again in the bot.

### Q: Are my credentials sent to any server?

**A:** **NO.** Credentials are stored locally and only sent directly to the exchange APIs. The bot does not phone home.

### Q: How do I verify the code is secure?

**A:** The entire security implementation is open source. Review:
- `src/security/secret_provider.py` - Credential storage
- `src/security/order_signing.py` - Request signing
- `src/utils/logger.py` - Log redaction

### Q: What happens if my computer is compromised?

**A:** If an attacker has access to your computer:
- OS keychain may be accessible if they have your system password
- Encrypted file storage can be decrypted if they have file access
- **Best defense**: Use IP whitelisting and withdrawal restrictions on exchange

## 🔗 Related Documentation

- [Quick Start Guide](QUICKSTART.md)
- [Configuration Guide](../config/strategy_config_example.yaml)
- [Strategy Enhancements](STRATEGY_ENHANCEMENTS.md)
- [Contributing](../CONTRIBUTING.md)

---

**Remember:** Security is only as strong as its weakest link. Follow best practices and stay vigilant!

