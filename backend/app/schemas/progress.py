"""
SetuX / VeriX — Historical Progress Tracking Schemas
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
import re

DATE_REGEX = r"^\d{4}-\d{2}-\d{2}$"


def validate_date_format(v: str) -> str:
    if not v:
        raise ValueError("report_date is required.")
    val = v.strip()
    if not re.match(DATE_REGEX, val):
        raise ValueError("report_date must be in YYYY-MM-DD format.")
    try:
        datetime.strptime(val, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"'{val}' is not a valid calendar date.")
    return val


class ProgressUpdateBase(BaseModel):
    report_date: str = Field(..., description="Date of physical verification/report (YYYY-MM-DD)")
    physical_progress: float = Field(..., ge=0.0, le=100.0, description="Cumulative physical progress (0-100%)")
    financial_progress: float = Field(..., ge=0.0, le=100.0, description="Cumulative financial progress (0-100%)")
    expenditure: float = Field(0.0, ge=0.0, description="Cumulative expenditure in Lakhs")
    remarks: Optional[str] = Field(None, description="Site observation or update remarks")

    @field_validator("report_date", mode="before")
    @classmethod
    def check_report_date(cls, v):
        return validate_date_format(str(v))


class ProgressUpdateCreate(ProgressUpdateBase):
    reported_by: Optional[str] = Field(None, description="Reporting officer name (auto-filled if omitted)")


class ProgressUpdateResponse(ProgressUpdateBase):
    id: int
    project_id: int
    reported_by: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
