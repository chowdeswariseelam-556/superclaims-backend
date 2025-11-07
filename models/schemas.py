"""
models/schemas.py - Pydantic models for data validation and API responses
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class BillDocument(BaseModel):
    """Medical bill document structure"""
    type: Literal["bill"] = "bill"
    hospital_name: str = Field(..., description="Hospital name")
    total_amount: float = Field(..., description="Total bill amount")
    date_of_service: str = Field(..., description="Date (YYYY-MM-DD)")
    patient_name: Optional[str] = None
    bill_items: Optional[List[str]] = None

class DischargeSummaryDocument(BaseModel):
    """Discharge summary document structure"""
    type: Literal["discharge_summary"] = "discharge_summary"
    patient_name: str = Field(..., description="Patient name")
    diagnosis: str = Field(..., description="Primary diagnosis")
    admission_date: str = Field(..., description="Admission date (YYYY-MM-DD)")
    discharge_date: str = Field(..., description="Discharge date (YYYY-MM-DD)")
    treating_doctor: Optional[str] = None
    procedures: Optional[List[str]] = None

class IDCardDocument(BaseModel):
    """Insurance ID card document structure"""
    type: Literal["id_card"] = "id_card"
    patient_name: str = Field(..., description="Patient name")
    policy_number: str = Field(..., description="Policy number")
    member_id: str = Field(..., description="Member ID")
    insurance_provider: Optional[str] = None

class ValidationResult(BaseModel):
    """Data validation results"""
    missing_documents: List[str] = Field(default_factory=list)
    discrepancies: List[str] = Field(default_factory=list)

class ClaimDecision(BaseModel):
    """Final claim decision"""
    status: Literal["approved", "rejected", "pending_review"]
    reason: str = Field(..., description="Decision reason")
    confidence_score: Optional[float] = None

class ClaimProcessingResponse(BaseModel):
    """Complete API response"""
    documents: List[BillDocument | DischargeSummaryDocument | IDCardDocument]
    validation: ValidationResult
    claim_decision: ClaimDecision
    processing_metadata: Optional[dict] = None