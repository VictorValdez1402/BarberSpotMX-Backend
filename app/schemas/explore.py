from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel


class NearbyResultItem(BaseModel):
    id: int
    entity_type: str  # "BARBER" o "BARBERSHOP"
    name: str
    phone: str
    avatar_url: Optional[str] = None
    distance_km: float
    base_cut_price: Optional[Decimal] = None
    approved_medals_count: Optional[int] = None
    years_in_service: Optional[int] = None


class NearbySearchResponse(BaseModel):
    latitude: float
    longitude: float
    radius_km: float
    total_found: int
    results: List[NearbyResultItem]