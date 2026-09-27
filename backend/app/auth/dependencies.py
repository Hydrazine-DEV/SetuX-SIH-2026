"""
SetuX / VeriX — Auth Dependencies & Middleware
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import User
from app.auth.security import decode_access_token

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Retrieve authenticated user from JWT Bearer token."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email = payload["sub"]
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_authenticated_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency ensuring user is logged in."""
    return current_user


def require_officer(current_user: User = Depends(get_current_user)) -> User:
    """Dependency ensuring logged-in user is an Officer."""
    if current_user.role.lower() != "officer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Officer access required. You are not authorized for officer operations.",
        )
    return current_user


def require_citizen(current_user: User = Depends(get_current_user)) -> User:
    """Dependency ensuring logged-in user is a Citizen."""
    if current_user.role.lower() != "citizen":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Citizen access required. You are not authorized for citizen operations.",
        )
    return current_user


def require_roles(*allowed_roles: str):
    """Dependency factory ensuring logged-in user belongs to one of the specified roles."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        normalized_roles = [r.lower().strip() for r in allowed_roles]
        if current_user.role.lower().strip() not in normalized_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden. Required role: {', '.join(allowed_roles)}. Your role is '{current_user.role}'.",
            )
        return current_user
    return role_checker
