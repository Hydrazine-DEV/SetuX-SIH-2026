"""
SetuX / VeriX — Schemas Package
"""
from app.schemas.auth import (
    UserSignUp,
    UserLogin,
    DepartmentResponse,
    UserResponse,
    TokenResponse,
    TokenPayload,
)
from app.schemas.department import (
    DepartmentBase,
    DepartmentCreate,
    DepartmentUpdate,
)
from app.schemas.contractor import (
    ContractorBase,
    ContractorCreate,
    ContractorUpdate,
    ContractorResponse,
)
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectStatusUpdate,
    ProjectResponse,
    PaginatedProjects,
)
from app.schemas.milestone import (
    MilestoneBase,
    MilestoneCreate,
    MilestoneUpdate,
    MilestoneResponse,
)
from app.schemas.progress import (
    ProgressUpdateBase,
    ProgressUpdateCreate,
    ProgressUpdateResponse,
)
from app.schemas.alert import (
    AlertBase,
    AlertCreate,
    AlertStatusUpdate,
    AlertResponse,
    AlertListResponse,
    AlertGenerateResponse,
)
from app.schemas.report import (
    ReportCreate,
    ReportResponse,
    ReportListResponse,
)

__all__ = [
    "UserSignUp",
    "UserLogin",
    "DepartmentResponse",
    "UserResponse",
    "TokenResponse",
    "TokenPayload",
    "DepartmentBase",
    "DepartmentCreate",
    "DepartmentUpdate",
    "ContractorBase",
    "ContractorCreate",
    "ContractorUpdate",
    "ContractorResponse",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectStatusUpdate",
    "ProjectResponse",
    "PaginatedProjects",
    "MilestoneBase",
    "MilestoneCreate",
    "MilestoneUpdate",
    "MilestoneResponse",
    "ProgressUpdateBase",
    "ProgressUpdateCreate",
    "ProgressUpdateResponse",
    "AlertBase",
    "AlertCreate",
    "AlertStatusUpdate",
    "AlertResponse",
    "AlertListResponse",
    "AlertGenerateResponse",
    "ReportCreate",
    "ReportResponse",
    "ReportListResponse",
]
