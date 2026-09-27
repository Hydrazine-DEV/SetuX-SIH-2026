"""
SetuX / VeriX — Auth API Router
POST /api/auth/signup    — Register new officer or citizen
POST /api/auth/login     — Login user and return JWT
GET  /api/auth/me        — Get current user profile
POST /api/auth/logout    — Logout user
GET  /api/departments    — List available departments
"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import User, Department, AuditLog
from app.auth.schemas import (
    UserSignUp,
    UserLogin,
    UserResponse,
    DepartmentResponse,
    TokenResponse,
)
from app.auth.security import hash_password, verify_password, create_access_token
from app.auth.dependencies import get_current_user

router = APIRouter(tags=["Authentication"])


@router.post("/api/auth/signup", response_model=TokenResponse)
def sign_up(req: UserSignUp, db: Session = Depends(get_db)):
    """Register a new officer or citizen user account."""
    email_clean = req.email.lower().strip()

    # Password validation
    if len(req.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters.",
        )

    if req.password != req.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match.",
        )

    role_clean = req.role.lower().strip()
    if role_clean not in ["officer", "citizen"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role specified. Must be 'officer' or 'citizen'.",
        )

    # Email uniqueness check
    existing_user = db.query(User).filter(User.email == email_clean).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    # Department handling
    dept_id = None
    dept_name = None
    if role_clean == "officer":
        if req.department_id:
            dept = db.query(Department).filter(Department.id == req.department_id).first()
            if dept:
                dept_id = dept.id
                dept_name = dept.name
            else:
                first_dept = db.query(Department).first()
                if first_dept:
                    dept_id = first_dept.id
                    dept_name = first_dept.name
        else:
            first_dept = db.query(Department).first()
            if first_dept:
                dept_id = first_dept.id
                dept_name = first_dept.name

    # Create User
    user = User(
        full_name=req.full_name.strip(),
        email=email_clean,
        phone=req.phone.strip() if req.phone else None,
        password_hash=hash_password(req.password),
        role=role_clean,
        department_id=dept_id,
        department_name=dept_name,
        is_active=True,
        is_verified=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Audit log
    audit = AuditLog(
        user_name=user.full_name,
        action=f"{role_clean.upper()}_SIGNUP",
        details=f"Account created for {user.full_name} ({user.email}) as {role_clean}",
        timestamp=datetime.utcnow(),
    )
    db.add(audit)
    db.commit()

    token = create_access_token(data={"sub": user.email, "role": user.role, "name": user.full_name})
    return TokenResponse(access_token=token, token_type="bearer", user=user)


@router.post("/api/auth/login", response_model=TokenResponse)
def login(req: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user credentials, check role authorization, and return JWT."""
    email_clean = req.email.lower().strip()
    role_requested = req.role.lower().strip()

    user = db.query(User).filter(User.email == email_clean).first()

    # 1. Verification of credentials (email existence + password match + active state)
    if not user or not verify_password(req.password, user.password_hash) or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    # 2. Verification of role match
    if user.role.lower() != role_requested:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to login as this role.",
        )

    # Update last login timestamp
    user.last_login = datetime.utcnow().isoformat()
    db.commit()

    # Record Audit log
    audit = AuditLog(
        user_name=user.full_name,
        action=f"{user.role.upper()}_LOGIN",
        details=f"{user.full_name} logged in as {user.role}",
        timestamp=datetime.utcnow(),
    )
    db.add(audit)
    db.commit()

    token = create_access_token(data={"sub": user.email, "role": user.role, "name": user.full_name})
    return TokenResponse(access_token=token, token_type="bearer", user=user)


@router.get("/api/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user profile."""
    return current_user


@router.post("/api/auth/logout")
def logout():
    """Logout current user."""
    return {"message": "Successfully logged out"}


# Re-export get_departments for backward compatibility with direct tests
from app.api.departments import list_departments as get_departments
