"""
SetuX / VeriX — Departments API Router
Complete CRUD endpoints for government departments.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_officer
from app.models.user import Department, User
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse

router = APIRouter(prefix="/api/departments", tags=["Departments"])


@router.get("", response_model=List[DepartmentResponse])
@router.get("/", response_model=List[DepartmentResponse])
def list_departments(
    db: Session = Depends(get_db),
    search: Optional[str] = None,
):
    """List all available government departments."""
    q = db.query(Department)
    if search and isinstance(search, str):
        search_pattern = f"%{search.strip()}%"
        q = q.filter(Department.name.ilike(search_pattern) | Department.code.ilike(search_pattern))
    return q.order_by(Department.id.asc()).all()


@router.get("/{dept_id}", response_model=DepartmentResponse)
def get_department(dept_id: int, db: Session = Depends(get_db)):
    """Retrieve a single department by its ID."""
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department with ID {dept_id} not found.",
        )
    return dept


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(
    req: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer),
):
    """Create a new department (Officer authorized)."""
    code_clean = req.code.upper().strip()
    name_clean = req.name.strip()

    existing = db.query(Department).filter(Department.code == code_clean).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Department with code '{code_clean}' already exists.",
        )

    dept = Department(
        name=name_clean,
        code=code_clean,
        description=req.description.strip() if req.description else None,
    )
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


@router.put("/{dept_id}", response_model=DepartmentResponse)
def update_department(
    dept_id: int,
    req: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer),
):
    """Update department details (Officer authorized)."""
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department with ID {dept_id} not found.",
        )

    if req.code:
        code_clean = req.code.upper().strip()
        existing = db.query(Department).filter(Department.code == code_clean, Department.id != dept_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Another department with code '{code_clean}' already exists.",
            )
        dept.code = code_clean

    if req.name is not None:
        dept.name = req.name.strip()
    if req.description is not None:
        dept.description = req.description.strip() if req.description else None

    db.commit()
    db.refresh(dept)
    return dept


@router.delete("/{dept_id}")
def delete_department(
    dept_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer),
):
    """Delete a department (Officer authorized)."""
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department with ID {dept_id} not found.",
        )

    # Check for associated projects
    if dept.projects and len(dept.projects) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete department '{dept.name}' because {len(dept.projects)} project(s) are associated with it.",
        )

    db.delete(dept)
    db.commit()
    return {"success": True, "message": f"Department '{dept.name}' deleted successfully."}
