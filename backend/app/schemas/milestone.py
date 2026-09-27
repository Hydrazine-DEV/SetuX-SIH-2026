"""
SetuX / VeriX — Milestone Pydantic Schemas
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
import re

DATE_REGEX = r"^\d{4}-\d{2}-\d{2}$"


def validate_date_format(v: Optional[str]) -> Optional[str]:
    if v is None or v == "":
        return None
    val = v.strip()
    if not re.match(DATE_REGEX, val):
        raise ValueError("Date must be in YYYY-MM-DD format.")
    try:
        datetime.strptime(val, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"'{val}' is not a valid calendar date.")
    return val


class MilestoneBase(BaseModel):
    name: str = Field(..., min_length=2, description="Milestone title / stage name")
    description: Optional[str] = Field(None, description="Scope of work in this milestone")
    planned_date: str = Field(..., description="Target planned completion date (YYYY-MM-DD)")
    actual_date: Optional[str] = Field(None, description="Actual completion date (YYYY-MM-DD)")
    status: Optional[str] = Field("PENDING", description="Status: NOT_STARTED, PENDING, IN_PROGRESS, COMPLETED, DELAYED")
    completion_percentage: Optional[float] = Field(0.0, ge=0.0, le=100.0, description="Stage progress (0-100%)")

    @field_validator("planned_date", mode="before")
    @classmethod
    def check_planned_date(cls, v):
        if not v:
            raise ValueError("planned_date is required and cannot be empty.")
        return validate_date_format(v)

    @field_validator("actual_date", mode="before")
    @classmethod
    def check_actual_date(cls, v):
        return validate_date_format(v)

    @field_validator("status", mode="before")
    @classmethod
    def check_status(cls, v):
        if not v:
            return "PENDING"
        val = str(v).upper().strip()
        allowed = {"NOT_STARTED", "PENDING", "IN_PROGRESS", "COMPLETED", "DELAYED"}
        if val not in allowed:
            raise ValueError(f"Status '{v}' is invalid. Allowed: {', '.join(allowed)}")
        return val


class MilestoneCreate(MilestoneBase):
    pass


class MilestoneUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2)
    description: Optional[str] = None
    planned_date: Optional[str] = None
    actual_date: Optional[str] = None
    status: Optional[str] = None
    completion_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)

    @field_validator("planned_date", "actual_date", mode="before")
    @classmethod
    def check_dates(cls, v):
        return validate_date_format(v)

    @field_validator("status", mode="before")
    @classmethod
    def check_status(cls, v):
        if v is None:
            return None
        val = str(v).upper().strip()
        allowed = {"NOT_STARTED", "PENDING", "IN_PROGRESS", "COMPLETED", "DELAYED"}
        if val not in allowed:
            raise ValueError(f"Status '{v}' is invalid. Allowed: {', '.join(allowed)}")
        return val


class MilestoneResponse(BaseModel):
    id: int
    project_id: int
    name: str
    description: Optional[str] = None
    planned_date: str
    actual_date: Optional[str] = None
    status: str
    completion_percentage: float
    is_delayed: bool = False
    delay_days: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
