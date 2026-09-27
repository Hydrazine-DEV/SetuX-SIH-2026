"""
SetuX / VeriX — Project Pydantic Schemas
Defines validation, creation, update, and response serialization for projects.
100% backward compatible with frontend properties (project_id, budget_lakh, etc.)
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=2, description="Project Name")
    project_code: Optional[str] = Field(None, description="Unique Project Identifier (e.g. MH-PN-001)")
    project_id: Optional[str] = Field(None, description="Compatibility alias for project_code")
    description: Optional[str] = Field(None, description="Detailed project description")
    sector: Optional[str] = Field("Roads & Highways", description="Infrastructure sector")
    project_type: Optional[str] = Field(None, description="Compatibility alias for sector")
    ministry: Optional[str] = Field(None, description="Nodal Ministry")
    department_id: Optional[int] = Field(None, description="Department FK ID")
    department_name: Optional[str] = Field(None, description="Department name")
    department: Optional[str] = Field(None, description="Compatibility alias for department_name")
    
    # Geographic location
    location: Optional[str] = Field(None, description="Project physical location")
    location_name: Optional[str] = Field(None, description="Compatibility alias for location")
    district: Optional[str] = Field(None, description="District in Maharashtra")
    taluka: Optional[str] = Field("", description="Taluka / Tehsil")
    state: Optional[str] = Field("Maharashtra", description="State")
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")
    lat: Optional[float] = Field(None, description="Compatibility alias for latitude")
    lng: Optional[float] = Field(None, description="Compatibility alias for longitude")

    # Contractor & Financials
    contractor_id: Optional[int] = Field(None, description="Contractor FK ID")
    contractor_name: Optional[str] = Field(None, description="Contractor Name")
    contractor: Optional[str] = Field(None, description="Compatibility alias for contractor_name")
    original_cost: Optional[float] = Field(0.0, ge=0.0, description="Sanctioned budget in Lakhs")
    budget_lakh: Optional[float] = Field(None, description="Compatibility alias for original_cost")
    revised_cost: Optional[float] = Field(None, ge=0.0, description="Revised budget in Lakhs")
    total_expenditure: Optional[float] = Field(0.0, ge=0.0, description="Total expenditure in Lakhs")

    # Timeline
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    planned_completion_date: Optional[str] = Field(None, description="Planned completion date")
    expected_completion: Optional[str] = Field(None, description="Compatibility alias for planned completion date")
    revised_completion_date: Optional[str] = Field(None, description="Revised completion date")
    actual_completion_date: Optional[str] = Field(None, description="Actual completion date")

    # Progress & Risk
    physical_progress: Optional[float] = Field(0.0, ge=0.0, le=100.0, description="Physical progress (0-100%)")
    reported_progress: Optional[int] = Field(None, ge=0, le=100, description="Compatibility alias for physical progress")
    financial_progress: Optional[float] = Field(0.0, ge=0.0, le=100.0, description="Financial progress (0-100%)")
    ai_estimated_progress: Optional[int] = Field(0, ge=0, le=100)
    status: Optional[str] = Field("Under Review", description="Project status")
    risk_level: Optional[str] = Field("LOW", description="Risk level: LOW, MEDIUM, HIGH, CRITICAL")
    anomaly_score: Optional[int] = Field(0, ge=0, le=100)


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2)
    description: Optional[str] = None
    sector: Optional[str] = None
    project_type: Optional[str] = None
    ministry: Optional[str] = None
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    department: Optional[str] = None
    contractor_id: Optional[int] = None
    contractor_name: Optional[str] = None
    contractor: Optional[str] = None
    location: Optional[str] = None
    location_name: Optional[str] = None
    district: Optional[str] = None
    taluka: Optional[str] = None
    state: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    original_cost: Optional[float] = Field(None, ge=0.0)
    budget_lakh: Optional[float] = None
    revised_cost: Optional[float] = Field(None, ge=0.0)
    total_expenditure: Optional[float] = Field(None, ge=0.0)
    start_date: Optional[str] = None
    planned_completion_date: Optional[str] = None
    expected_completion: Optional[str] = None
    revised_completion_date: Optional[str] = None
    actual_completion_date: Optional[str] = None
    physical_progress: Optional[float] = Field(None, ge=0.0, le=100.0)
    reported_progress: Optional[int] = Field(None, ge=0, le=100)
    financial_progress: Optional[float] = Field(None, ge=0.0, le=100.0)
    ai_estimated_progress: Optional[int] = Field(None, ge=0, le=100)
    status: Optional[str] = None
    risk_level: Optional[str] = None
    anomaly_score: Optional[int] = Field(None, ge=0, le=100)


class ProjectStatusUpdate(BaseModel):
    status: str = Field(..., description="Status: Verified, Review Required, High Risk, Delayed, Completed, Under Review")
    risk_level: Optional[str] = Field(None, description="Risk level: LOW, MEDIUM, HIGH, CRITICAL")


class ProjectResponse(BaseModel):
    id: int
    project_code: str
    project_id: str
    name: str
    description: Optional[str] = None
    sector: Optional[str] = None
    project_type: Optional[str] = None
    ministry: Optional[str] = None
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    department: Optional[str] = ""
    contractor_id: Optional[int] = None
    contractor_name: Optional[str] = None
    contractor: Optional[str] = ""
    location: Optional[str] = None
    location_name: Optional[str] = None
    district: Optional[str] = None
    taluka: Optional[str] = ""
    state: Optional[str] = "Maharashtra"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    original_cost: Optional[float] = 0.0
    budget_lakh: Optional[float] = 0.0
    revised_cost: Optional[float] = None
    total_expenditure: Optional[float] = 0.0
    start_date: Optional[str] = None
    planned_completion_date: Optional[str] = None
    expected_completion: Optional[str] = None
    revised_completion_date: Optional[str] = None
    actual_completion_date: Optional[str] = None
    physical_progress: Optional[float] = 0.0
    reported_progress: Optional[int] = 0
    financial_progress: Optional[float] = 0.0
    ai_estimated_progress: Optional[int] = 0
    status: Optional[str] = "Under Review"
    risk_level: Optional[str] = "LOW"
    anomaly_score: Optional[int] = 0
    last_evidence_date: Optional[str] = ""
    is_demo: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaginatedProjects(BaseModel):
    items: List[ProjectResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
