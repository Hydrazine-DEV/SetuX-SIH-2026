"""
SetuX / VeriX — Progress Updates ORM Model (Historical Timeline)
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class ProgressUpdate(Base):
    __tablename__ = "progress_updates"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    reported_by = Column(String(255), nullable=False)
    report_date = Column(String(50), nullable=False)
    physical_progress = Column(Float, nullable=False)   # 0 to 100
    financial_progress = Column(Float, nullable=False)  # 0 to 100
    expenditure = Column(Float, default=0.0)            # In Lakhs
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="progress_updates")
