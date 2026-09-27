"""
SetuX / VeriX — Evidence, Verification, and Inspection ORM Models
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Evidence(Base):
    __tablename__ = "evidences"

    id = Column(Integer, primary_key=True, index=True)
    evidence_id = Column(String(100), unique=True, index=True, nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=True, index=True)
    
    uploaded_by = Column(String(255), default="Aarav Patil")
    file_name = Column(String(255), nullable=True)        # Original filename
    file_path = Column(String(500), nullable=True)        # Relative or absolute path on disk
    file_type = Column(String(50), default="image")       # image, document, video
    description = Column(Text, nullable=True)
    
    # Evidence metadata & verification fields
    evidence_type = Column(String(100), default="Current / After Work")
    stored_filename = Column(String(255), nullable=True)
    file_url = Column(String(500), nullable=True)
    file_size = Column(Integer, default=0)
    mime_type = Column(String(100), default="image/jpeg")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    timestamp = Column(String(100), nullable=True)
    exif_metadata = Column(Text, nullable=True)           # JSON string
    reported_progress = Column(Integer, default=0)
    remarks = Column(Text, nullable=True)
    work_status = Column(String(100), default="In Progress")
    verification_status = Column(String(100), default="Pending")
    ai_result = Column(Text, nullable=True)               # JSON string
    submitted_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="evidences")
    issue = relationship("Issue", back_populates="evidence_items")

    # Compatibility property: filename mapping
    @property
    def filename(self) -> str:
        return self.file_name or ""

    @filename.setter
    def filename(self, val: str):
        self.file_name = val


class Verification(Base):
    __tablename__ = "verifications"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    reported_progress = Column(Integer, default=0)
    estimated_progress = Column(Integer, default=0)
    gps_verified = Column(Boolean, default=False)
    gps_distance_m = Column(Float, default=0.0)
    timestamp_verified = Column(Boolean, default=True)
    duplicate_image = Column(Boolean, default=False)
    manipulation_risk = Column(String(50), default="LOW")
    anomaly_score = Column(Integer, default=0)
    risk_level = Column(String(50), default="LOW")
    recommendation = Column(String(100), default="APPROVE")
    infrastructure_detected = Column(Text, default="[]")  # JSON string
    explanation = Column(Text, nullable=True)
    is_demo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="verifications")


class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    officer_name = Column(String(255), nullable=False)
    inspection_date = Column(String(50), nullable=False)
    remarks = Column(Text, nullable=True)
    actual_progress = Column(Integer, default=0)
    result = Column(String(100), default="Confirmed")  # Confirmed, Disputed, Escalated
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="inspections")
