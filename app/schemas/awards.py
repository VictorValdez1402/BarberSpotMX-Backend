from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models import VerificationStatusEnum


class AwardSubmitRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=150)
    proof_document_url: str = Field(..., max_length=500)


class AwardReviewRequest(BaseModel):
    status: VerificationStatusEnum = Field(..., description="APPROVED o REJECTED")
    review_notes: Optional[str] = None


class AwardResponse(BaseModel):
    id: int
    barber_id: int
    title: str
    proof_document_url: str
    status: VerificationStatusEnum
    reviewed_at: Optional[datetime]
    review_notes: Optional[str]

    class Config:
        from_attributes = True


class PortfolioImageAdd(BaseModel):
    image_url: str = Field(..., max_length=500)
    display_order: int = Field(0, ge=0)