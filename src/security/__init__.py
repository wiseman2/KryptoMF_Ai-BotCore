"""
Security Module - MUST BE OPEN SOURCE FOR AUDITABILITY

This module contains all security-critical code:
- API key storage (OS keychain integration)
- Order signing (HMAC/EdDSA/ECDSA)
- Secrets handling (redaction, secure I/O)

This code MUST remain open source so users can audit how their
exchange API keys are stored and used.
"""

__all__ = ['SecretProvider', 'OrderSigner']

