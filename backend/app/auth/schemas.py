"""
SetuX / VeriX — Auth Schemas
Re-exports from app.schemas.auth for backward compatibility.
"""
from app.schemas.auth import (
    UserSignUp,
    UserLogin,
    DepartmentResponse,
    UserResponse,
    TokenResponse,
    TokenPayload,
)

__all__ = [
    "UserSignUp",
    "UserLogin",
    "DepartmentResponse",
    "UserResponse",
    "TokenResponse",
    "TokenPayload",
]
