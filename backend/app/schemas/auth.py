"""
SetuX / VeriX — Auth Schemas
Pydantic models for authentication, registration, user profile, and RBAC.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class UserSignUp(BaseModel):
    full_name: str = Field(..., min_length=1, description="Full Name")
    email: str = Field(..., description="Valid Email Address")
    phone: Optional[str] = Field(None, description="Phone Number")
    password: str = Field(..., min_length=8, description="Password (min 8 chars)")
    confirm_password: str = Field(..., description="Password Confirmation")
    role: str = Field("officer", description="User Role ('officer' or 'citizen')")
    department_id: Optional[int] = Field(None, description="Department ID for Officers")


class UserLogin(BaseModel):
    email: str = Field(..., description="Email Address")
    password: str = Field(..., description="Password")
    role: str = Field("officer", description="Selected Role ('officer' or 'citizen')")


class DepartmentResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    role: str
    is_active: bool = True
    is_verified: bool = False
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    department: Optional[DepartmentResponse] = None
    designation: Optional[str] = None
    district: Optional[str] = None
    employee_id: Optional[str] = None
    last_login: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenPayload(BaseModel):
    sub: str
    role: str
    name: Optional[str] = None
    exp: Optional[int] = None
