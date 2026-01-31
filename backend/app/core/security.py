"""API key hashing and verification for Agent auth."""
import hashlib
from app.core.config import settings


def hash_api_key(api_key: str) -> str:
    """Hash API key for storage. One-way."""
    return hashlib.sha256(
        (settings.api_key_secret + api_key).encode("utf-8")
    ).hexdigest()


def verify_api_key(plain: str, hashed: str) -> bool:
    """Verify plain API key against stored hash."""
    return hash_api_key(plain) == hashed
