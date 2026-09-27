"""
SetuX / VeriX — Backward Compatibility Shim for database/models.py
Re-exports all modular models from app.models.
"""
from app.models import (
    Department,
    User,
    Contractor,
    Project,
    Milestone,
    ProgressUpdate,
    Issue,
    Evidence,
    Verification,
    Inspection,
    Alert,
    Report,
    AuditLog,
)

__all__ = [
    "Department",
    "User",
    "Contractor",
    "Project",
    "Milestone",
    "ProgressUpdate",
    "Issue",
    "Evidence",
    "Verification",
    "Inspection",
    "Alert",
    "Report",
    "AuditLog",
]
