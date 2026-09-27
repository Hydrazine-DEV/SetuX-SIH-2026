"""
SetuX / VeriX — Centralized API Dependencies & RBAC Guards
"""
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.auth.dependencies import (
    get_current_user,
    require_authenticated_user,
    require_officer,
    require_citizen,
    require_roles,
)

__all__ = [
    "get_db",
    "get_current_user",
    "require_authenticated_user",
    "require_officer",
    "require_citizen",
    "require_roles",
    "Depends",
    "HTTPException",
    "status",
    "Session",
    "User",
]
