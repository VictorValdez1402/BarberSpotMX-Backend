from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.schemas.awards import AwardResponse


class BarberBase(BaseModel):
    bio: Optional[str] = None
    years_of_experience: int = 0
    specialties: Optional[str] = None
    instagram_url: Optional[str] = None
    tiktok_url: Optional[str] = None
    facebook_url: Optional[str] = None
    website_url: Optional[str] = None
    is_independent: bool = True
    is_available: bool = True
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class BarberCreate(BarberBase):
    barbershop_id: Optional[int] = None


class BarberSocialsUpdate(BaseModel):
    instagram_url: Optional[str] = None
    tiktok_url: Optional[str] = None
    facebook_url: Optional[str] = None
    website_url: Optional[str] = None


class BarberUpdate(BaseModel):
    bio: Optional[str] = None
    years_of_experience: Optional[int] = None
    specialties: Optional[str] = None
    instagram_url: Optional[str] = None
    tiktok_url: Optional[str] = None
    facebook_url: Optional[str] = None
    website_url: Optional[str] = None
    is_independent: Optional[bool] = None
    is_available: Optional[bool] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    barbershop_id: Optional[int] = None


class BarberResponse(BarberBase):
    id: int
    user_id: int
    barbershop_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    awards: List[AwardResponse] = []

    class Config:
        from_attributes = True