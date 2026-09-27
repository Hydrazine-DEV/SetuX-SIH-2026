"""
SetuX / VeriX — Issue Schemas
Pydantic models for issue creation, update, and response serialization.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class IssueCreate(BaseModel):
    """Schema for creating a new issue on a project."""
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=5)
    severity: str = Field(default="MEDIUM", pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    reported_by: Optional[str] = None
    reported_date: Optional[str] = None


class IssueUpdate(BaseModel):
    """Schema for partial issue updates."""
    title: Optional[str] = Field(default=None, min_length=3, max_length=255)
    description: Optional[str] = Field(default=None, min_length=5)
    severity: Optional[str] = Field(default=None, pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    status: Optional[str] = Field(default=None, pattern="^(OPEN|IN_PROGRESS|RESOLVED|CLOSED)$")
    resolved_date: Optional[str] = None


class IssueResponse(BaseModel):
    """Schema for issue API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    reported_by: str
    title: str
    description: str
    severity: str
    status: str
    reported_date: Optional[str] = None
    resolved_date: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class IssueSummaryResponse(BaseModel):
    """Schema for project issue summary metrics."""
    project_id: str
    total_issues: int = 0
    open_issues: int = 0
    in_progress_issues: int = 0
    resolved_issues: int = 0
    closed_issues: int = 0
    critical_issues: int = 0
    high_severity_issues: int = 0

