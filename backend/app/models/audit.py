"""
SetuX / VeriX — Audit Log ORM Model
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(100), nullable=True, index=True)
    user_name = Column(String(255), default="System")
    action = Column(String(100), nullable=False)  # SIGNUP, LOGIN, UPLOAD_EVIDENCE, VERIFICATION_RUN, etc.
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
