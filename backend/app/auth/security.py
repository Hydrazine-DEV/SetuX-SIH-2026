"""
SetuX / VeriX — Security & JWT Utilities
Shim re-exporting from app.core.security for backward compatibility.
"""
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "SECRET_KEY",
    "ALGORITHM",
    "ACCESS_TOKEN_EXPIRE_MINUTES",
]
