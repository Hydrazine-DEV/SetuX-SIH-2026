"""
SetuX / VeriX — Reports ORM Model
SIH26103: Integrated Government Project Monitoring & Intelligence Platform
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    generated_by = Column(String(255), nullable=False)
    report_type = Column(String(100), default="PROJECT_SUMMARY", nullable=False)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=True)
    file_size = Column(Integer, default=0)
    status = Column(String(50), default="GENERATED", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="reports")
