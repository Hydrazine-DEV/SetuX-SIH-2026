"""
SetuX / VeriX — Early Warning Alerts ORM Model
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    alert_type = Column(String(100), nullable=False)  # SCHEDULE_DELAY, COST_OVERRUN, LOW_PROGRESS, MILESTONE_DELAY, HIGH_RISK, etc.
    severity = Column(String(50), default="MEDIUM", nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(50), default="UNREAD", nullable=False)  # UNREAD, READ, RESOLVED, DISMISSED
    source = Column(String(100), default="RULE_ENGINE", nullable=False)  # RULE_ENGINE, COST_PREDICTOR, TIME_PREDICTOR, RISK_INTELLIGENCE, DATA_QUALITY
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    risk_score = Column(Integer, default=0)
    metadata_json = Column(Text, nullable=True)  # JSON-serialized evidence, metrics, model probabilities
    is_read = Column(Boolean, default=False, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="alerts")
