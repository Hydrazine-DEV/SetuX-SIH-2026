"""
SetuX / VeriX — Milestone ORM Model
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    planned_date = Column(String(50), nullable=False)
    actual_date = Column(String(50), nullable=True)
    status = Column(String(50), default="PENDING")  # PENDING, IN_PROGRESS, COMPLETED, DELAYED
    completion_percentage = Column(Float, default=0.0)  # 0.0 to 100.0
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="milestones")
