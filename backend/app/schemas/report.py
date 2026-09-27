"""
SetuX / VeriX — Report Pydantic Schemas
SIH26103: Integrated Government Project Monitoring & Intelligence Platform
"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, field_validator
from app.services.report_config import ReportType


class ReportCreate(BaseModel):
    report_type: str = Field(
        ReportType.PROJECT_SUMMARY.value,
        description="Type of report: PROJECT_SUMMARY, RISK_ASSESSMENT, EARLY_WARNING, EXECUTIVE_PROJECT_REPORT",
    )

    @field_validator("report_type")
    def validate_report_type(cls, v: str) -> str:
        valid_types = [t.value for t in ReportType]
        v_upper = v.upper().strip()
        if v_upper not in valid_types:
            raise ValueError(f"Invalid report_type '{v}'. Allowed types: {', '.join(valid_types)}")
        return v_upper


class ReportResponse(BaseModel):
    id: int
    project_id: Optional[int] = None
    project_code: Optional[str] = None
    report_type: str
    file_name: Optional[str] = None
    file_size: Optional[int] = 0
    status: str = "GENERATED"
    generated_by: str
    created_at: datetime
    download_url: Optional[str] = None

    class Config:
        from_attributes = True


class ReportListResponse(BaseModel):
    total: int
    items: List[ReportResponse]
