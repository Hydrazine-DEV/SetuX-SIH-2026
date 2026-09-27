"""
SetuX / VeriX — Department Schemas
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=2, description="Department name, e.g. Public Works Department")
    code: str = Field(..., min_length=2, max_length=50, description="Department code, e.g. PWD")
    description: Optional[str] = Field(None, description="Department functional description")


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2)
    code: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = None


class DepartmentResponse(DepartmentBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
