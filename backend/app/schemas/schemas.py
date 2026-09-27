"""
SetuX / VeriX — Pydantic Schemas for API validation & serialization
Phase 2: Enhanced with real evidence uploads, audit logs, and EXIF metadata
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


# ─── Project Schemas ────────────────────────────────────────────
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectStatusUpdate,
    ProjectResponse,
    PaginatedProjects,
)


# ─── Evidence Schemas ────────────────────────────────────────────
class EvidenceCreate(BaseModel):
    project_id: str
    evidence_type: str = "Current / After Work"  # Before Work, During Work, Current / After Work
    submitted_lat: Optional[float] = None
    submitted_lng: Optional[float] = None
    reported_progress: int = 0
    remarks: Optional[str] = ""
    work_status: str = "In Progress"
    expected_completion: Optional[str] = ""
    submitted_by: Optional[str] = "Aarav Patil"


class EvidenceResponse(BaseModel):
    id: int
    evidence_id: Optional[str] = None
    project_id: Optional[Any] = None
    issue_id: Optional[int] = None
    uploaded_by: Optional[str] = "Aarav Patil"
    evidence_type: Optional[str] = "Current / After Work"
    filename: Optional[str] = None
    file_name: Optional[str] = None
    stored_filename: Optional[str] = None
    file_path: Optional[str] = None
    file_url: Optional[str] = None
    file_type: Optional[str] = "image"
    description: Optional[str] = None
    file_size: Optional[int] = 0
    mime_type: Optional[str] = "image/jpeg"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timestamp: Optional[str] = None
    exif_metadata: Optional[str] = None
    reported_progress: Optional[int] = 0
    remarks: Optional[str] = None
    work_status: Optional[str] = "In Progress"
    verification_status: Optional[str] = "Pending"
    ai_result: Optional[str] = None
    submitted_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True



# ─── Verification Schemas ─────────────────────────────────────────
class VerificationRequest(BaseModel):
    project_id: str
    reported_progress: int
    submitted_lat: Optional[float] = None
    submitted_lng: Optional[float] = None
    evidence_type: Optional[str] = "Current / After Work"


class InfrastructureItem(BaseModel):
    item: str
    detected: bool
    confidence: str  # "HIGH", "MEDIUM", "LOW"
    status: str      # "✓ Detected", "⚠ Partial", "✗ Not Detected"


class VerificationResponse(BaseModel):
    project_id: str
    reported_progress: int
    estimated_progress: int
    gps_verified: bool
    gps_distance_m: float
    timestamp_verified: bool
    duplicate_image: bool
    manipulation_risk: str
    anomaly_score: int
    risk_level: str
    recommendation: str
    infrastructure_detected: List[InfrastructureItem]
    explanation: str
    exif_metadata: Optional[Dict[str, Any]] = None
    is_demo: bool = True
    ai_demo_mode: bool = True
    disclaimer: str = "Prototype AI Output — Model validation pending"

    class Config:
        from_attributes = True


# ─── Audit Log Schemas ────────────────────────────────────────────
class AuditLogResponse(BaseModel):
    id: int
    project_id: Optional[str] = None
    user_name: str
    action: str
    details: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


# ─── Analytics Schemas ────────────────────────────────────────────
class AnalyticsSummary(BaseModel):
    total_projects: int
    verified: int
    review_required: int
    high_risk: int
    delayed: int
    completed: int
    avg_reported_progress: float
    avg_ai_estimated_progress: float
    inspection_rate: float


class DistrictStat(BaseModel):
    district: str
    total: int
    high_risk: int
    avg_progress_gap: float


class PriorityProject(BaseModel):
    project_id: str
    name: str
    district: str
    risk_score: int
    reason: str
    reported_progress: int
    ai_estimated_progress: int
