"""
SetuX / VeriX — Project ORM Model
Complete with all SIH26103 core fields and backward-compatible synonyms for frontend.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship, synonym
from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    project_code = Column(String(100), unique=True, index=True, nullable=False)  # e.g. MH-PN-001
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    sector = Column(String(100), nullable=True)  # Road, Bridge, School, Water Pipeline, etc.
    ministry = Column(String(255), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    department_name = Column(String(255), nullable=True)
    
    # Geographic location
    location = Column(String(255), nullable=True)
    district = Column(String(100), nullable=True, index=True)
    taluka = Column(String(100), nullable=True, default="")
    state = Column(String(100), default="Maharashtra")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Contractor & Financials
    contractor_id = Column(Integer, ForeignKey("contractors.id"), nullable=True)
    contractor_name = Column(String(255), nullable=True)
    original_cost = Column(Float, default=0.0)      # In Lakhs
    revised_cost = Column(Float, nullable=True)     # In Lakhs
    total_expenditure = Column(Float, default=0.0)  # In Lakhs
    
    # Timeline
    start_date = Column(String(50), nullable=True)
    planned_completion_date = Column(String(50), nullable=True)
    revised_completion_date = Column(String(50), nullable=True)
    actual_completion_date = Column(String(50), nullable=True)
    
    # Progress & Risk
    physical_progress = Column(Float, default=0.0)   # 0 to 100
    financial_progress = Column(Float, default=0.0)  # 0 to 100
    ai_estimated_progress = Column(Integer, default=0)
    status = Column(String(50), default="Under Review")  # Verified, Review Required, High Risk, Delayed, Completed
    risk_level = Column(String(50), default="LOW")       # LOW, MEDIUM, HIGH, CRITICAL
    anomaly_score = Column(Integer, default=0)           # 0 to 100
    
    # Metadata
    last_evidence_date = Column(String(50), nullable=True, default="")
    is_demo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    department_rel = relationship("Department", back_populates="projects")
    contractor_rel = relationship("Contractor", back_populates="projects")
    milestones = relationship("Milestone", back_populates="project", cascade="all, delete-orphan")
    progress_updates = relationship("ProgressUpdate", back_populates="project", cascade="all, delete-orphan")
    issues = relationship("Issue", back_populates="project", cascade="all, delete-orphan")
    evidences = relationship("Evidence", back_populates="project", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="project", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="project", cascade="all, delete-orphan")
    verifications = relationship("Verification", back_populates="project", cascade="all, delete-orphan")
    inspections = relationship("Inspection", back_populates="project", cascade="all, delete-orphan")

    # ─── Backward-Compatibility Synonyms & Hybrid Properties (Queryable & Assignable) ───
    project_id = synonym("project_code")
    budget_lakh = synonym("original_cost")
    reported_progress = synonym("physical_progress")
    lat = synonym("latitude")
    lng = synonym("longitude")
    location_name = synonym("location")
    project_type = synonym("sector")
    expected_completion = synonym("planned_completion_date")

    from sqlalchemy.ext.hybrid import hybrid_property

    @hybrid_property
    def department(self) -> str:
        if self.department_rel:
            return self.department_rel.name
        return self.department_name or ""

    @department.setter
    def department(self, val: str):
        self.department_name = val

    @department.expression
    def department(cls):
        return cls.department_name

    @hybrid_property
    def contractor(self) -> str:
        if self.contractor_rel:
            return self.contractor_rel.name
        return self.contractor_name or ""

    @contractor.setter
    def contractor(self, val: str):
        self.contractor_name = val

    @contractor.expression
    def contractor(cls):
        return cls.contractor_name
