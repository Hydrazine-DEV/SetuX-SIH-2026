"""
SetuX / VeriX — Contractors API Router
Complete CRUD endpoints for government contractors and execution agencies.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_officer
from app.models.contractor import Contractor
from app.schemas.contractor import (
    ContractorCreate,
    ContractorUpdate,
    ContractorResponse,
)

router = APIRouter(prefix="/api/contractors", tags=["Contractors"])


@router.get("", response_model=List[ContractorResponse])
@router.get("/", response_model=List[ContractorResponse])
def list_contractors(
    search: Optional[str] = Query(None, description="Search by name or registration number"),
    skip: int = Query(0, ge=0, description="Offset"),
    limit: int = Query(100, ge=1, le=500, description="Limit"),
    db: Session = Depends(get_db),
):
    """List all contractors with optional search and pagination."""
    q = db.query(Contractor)
    if search:
        search_pattern = f"%{search.strip()}%"
        q = q.filter(
            Contractor.name.ilike(search_pattern)
            | Contractor.registration_number.ilike(search_pattern)
        )
    return q.order_by(Contractor.id.asc()).offset(skip).limit(limit).all()


@router.get("/{contractor_id}", response_model=ContractorResponse)
def get_contractor(contractor_id: int, db: Session = Depends(get_db)):
    """Retrieve a single contractor by ID."""
    contractor = db.query(Contractor).filter(Contractor.id == contractor_id).first()
    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contractor with ID {contractor_id} not found.",
        )
    return contractor


@router.post("", response_model=ContractorResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=ContractorResponse, status_code=status.HTTP_201_CREATED)
def create_contractor(
    req: ContractorCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_officer),
):
    """Register a new contractor (Officer authorized)."""
    reg_clean = req.registration_number.upper().strip()
    name_clean = req.name.strip()

    existing = db.query(Contractor).filter(Contractor.registration_number == reg_clean).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Contractor with registration number '{reg_clean}' already exists.",
        )

    contractor = Contractor(
        name=name_clean,
        registration_number=reg_clean,
        contact_email=req.contact_email.strip() if req.contact_email else None,
        contact_phone=req.contact_phone.strip() if req.contact_phone else None,
    )
    db.add(contractor)
    db.commit()
    db.refresh(contractor)
    return contractor


@router.put("/{contractor_id}", response_model=ContractorResponse)
def update_contractor(
    contractor_id: int,
    req: ContractorUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_officer),
):
    """Update contractor details (Officer authorized)."""
    contractor = db.query(Contractor).filter(Contractor.id == contractor_id).first()
    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contractor with ID {contractor_id} not found.",
        )

    if req.registration_number:
        reg_clean = req.registration_number.upper().strip()
        existing = (
            db.query(Contractor)
            .filter(Contractor.registration_number == reg_clean, Contractor.id != contractor_id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Another contractor with registration number '{reg_clean}' already exists.",
            )
        contractor.registration_number = reg_clean

    if req.name is not None:
        contractor.name = req.name.strip()
    if req.contact_email is not None:
        contractor.contact_email = req.contact_email.strip() if req.contact_email else None
    if req.contact_phone is not None:
        contractor.contact_phone = req.contact_phone.strip() if req.contact_phone else None

    db.commit()
    db.refresh(contractor)
    return contractor


@router.delete("/{contractor_id}")
def delete_contractor(
    contractor_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_officer),
):
    """Delete a contractor (Officer authorized)."""
    contractor = db.query(Contractor).filter(Contractor.id == contractor_id).first()
    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contractor with ID {contractor_id} not found.",
        )

    # Prevent deletion if contractor has assigned projects
    if contractor.projects and len(contractor.projects) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete contractor '{contractor.name}' because {len(contractor.projects)} project(s) are assigned to them.",
        )

    db.delete(contractor)
    db.commit()
    return {"success": True, "message": f"Contractor '{contractor.name}' deleted successfully."}
