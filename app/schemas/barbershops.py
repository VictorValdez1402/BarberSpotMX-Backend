from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class BarbershopBase(BaseModel):
    name: str
    description: Optional[str] = None
    address: str
    phone: Optional[str] = None
    instagram_url: Optional[str] = None
    tiktok_url: Optional[str] = None
    facebook_url: Optional[str] = None
    website_url: Optional[str] = None
    latitude: float
    longitude: float


class BarbershopCreate(BarbershopBase):
    pass


class BarbershopSocialsUpdate(BaseModel):
    instagram_url: Optional[str] = None
    tiktok_url: Optional[str] = None
    facebook_url: Optional[str] = None
    website_url: Optional[str] = None


class BarbershopUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    instagram_url: Optional[str] = None
    tiktok_url: Optional[str] = None
    facebook_url: Optional[str] = None
    website_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class BarbershopResponse(BarbershopBase):
    id: int
    owner_id: int
    max_barbers: int
    is_verified: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True