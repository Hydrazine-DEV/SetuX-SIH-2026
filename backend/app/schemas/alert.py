"""
SetuX / VeriX — Early Warning Alerts Pydantic Schemas
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
import json
from pydantic import BaseModel, Field, validator
from app.services.alert_config import AlertStatus, AlertSeverity, AlertType, AlertSource


class AlertBase(BaseModel):
    project_id: int
    alert_type: str
    severity: str
    status: str = "UNREAD"
    source: str = "RULE_ENGINE"
    title: str
    message: str
    risk_score: int = 0
    metadata_json: Optional[str] = None
    is_read: bool = False


class AlertCreate(BaseModel):
    project_id: int
    alert_type: str
    severity: str = "MEDIUM"
    source: str = "RULE_ENGINE"
    title: str
    message: str
    risk_score: int = 0
    metadata: Optional[Dict[str, Any]] = None


class AlertStatusUpdate(BaseModel):
    status: str
    reason: Optional[str] = None


class AlertResponse(BaseModel):
    id: int
    project_id: int
    alert_type: str
    severity: str
    status: str
    source: str
    title: str
    message: str
    risk_score: int
    metadata: Optional[Dict[str, Any]] = None
    is_read: bool
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_custom(cls, obj: Any) -> "AlertResponse":
        meta = None
        if hasattr(obj, "metadata_json") and obj.metadata_json:
            try:
                meta = json.loads(obj.metadata_json)
            except Exception:
                meta = {"raw": obj.metadata_json}

        return cls(
            id=obj.id,
            project_id=obj.project_id,
            alert_type=obj.alert_type,
            severity=obj.severity,
            status=obj.status if hasattr(obj, "status") and obj.status else ("READ" if obj.is_read else "UNREAD"),
            source=obj.source if hasattr(obj, "source") and obj.source else "RULE_ENGINE",
            title=obj.title,
            message=obj.message,
            risk_score=obj.risk_score or 0,
            metadata=meta,
            is_read=obj.is_read,
            resolved_at=getattr(obj, "resolved_at", None),
            resolved_by=getattr(obj, "resolved_by", None),
            created_at=obj.created_at or datetime.utcnow(),
        )


class AlertListResponse(BaseModel):
    total: int
    page: int
    limit: int
    pages: int
    items: List[AlertResponse]


class AlertGenerateResponse(BaseModel):
    project_id: int
    project_code: Optional[str] = None
    generated_count: int
    existing_active_count: int
    alerts: List[AlertResponse]
    summary: Dict[str, Any]
