from typing import Optional, List
from decimal import Decimal
from datetime import time
from pydantic import BaseModel, Field, field_validator
from app.models import DayOfWeekEnum, SubscriptionStatusEnum


class ScheduleItem(BaseModel):
    day_of_week: DayOfWeekEnum
    is_closed: bool = False
    open_time: Optional[time] = None
    close_time: Optional[time] = None


class BarbershopCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    bio: Optional[str] = None
    years_in_service: int = Field(0, ge=0)
    phone: str = Field(..., min_length=10, max_length=20)
    latitude: float = Field(..., ge=-90, le=90, description="Ubicación obligatoria")
    longitude: float = Field(..., ge=-180, le=180, description="Ubicación obligatoria")
    address_text: Optional[str] = None
    base_cut_price: Decimal = Field(..., gt=0, description="Precio obligatorio del corte base")
    schedules: List[ScheduleItem] = []

    @field_validator("bio")
    @classmethod
    def validate_bio_word_count(cls, v: Optional[str]):
        if v:
            words = v.strip().split()
            if len(words) > 500:
                raise ValueError(f"La descripción excede el límite de 500 palabras (palabras actuales: {len(words)})")
        return v


class BarbershopPackageItem(BaseModel):
    title: str = Field(..., max_length=120)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)


class AddBarberToShopRequest(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    stage_name: str
    age: int
    phone: str
    bio: Optional[str] = None


class BarbershopResponse(BaseModel):
    id: int
    owner_id: int
    name: str
    bio: Optional[str]
    years_in_service: int
    phone: str
    allowed_barbers_count: int
    subscription_status: SubscriptionStatusEnum

    class Config:
        from_attributes = True