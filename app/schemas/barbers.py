from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator


class BarberProfileCreate(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    stage_name: str = Field(..., min_length=2, max_length=100, description="Nombre artístico")
    age: int = Field(..., ge=16, le=100)
    phone: str = Field(..., min_length=10, max_length=20)
    bio: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    base_cut_price: Decimal = Field(..., gt=0, description="Precio obligatorio del corte base")

    @field_validator("bio")
    @classmethod
    def validate_bio_word_count(cls, v: Optional[str]):
        if v:
            words = v.strip().split()
            if len(words) > 450:
                raise ValueError(f"La biografía excede el límite de 450 palabras (palabras actuales: {len(words)})")
        return v


class BarberServiceItem(BaseModel):
    service_name: str  # e.g., 'Barba', 'Ceja', 'Exfoliación'
    price: Decimal = Field(..., gt=0)


class BarberPackageItem(BaseModel):
    title: str = Field(..., max_length=120)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)


class BarberProfileResponse(BaseModel):
    id: int
    user_id: int
    first_name: str
    last_name: str
    stage_name: str
    age: int
    phone: str
    bio: Optional[str]
    avatar_url: Optional[str]
    approved_medals_count: int
    subscription_status: str

    class Config:
        from_attributes = True