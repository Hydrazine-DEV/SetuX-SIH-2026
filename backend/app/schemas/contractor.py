"""
SetuX / VeriX — Contractor Schemas
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ContractorBase(BaseModel):
    name: str = Field(..., min_length=2, description="Contractor / Firm Name")
    registration_number: str = Field(..., min_length=3, description="Govt Registration / GST / CIN Number")
    contact_email: Optional[str] = Field(None, description="Official Contact Email")
    contact_phone: Optional[str] = Field(None, description="Contact Phone Number")


class ContractorCreate(ContractorBase):
    pass


class ContractorUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2)
    registration_number: Optional[str] = Field(None, min_length=3)
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None


class ContractorResponse(ContractorBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
