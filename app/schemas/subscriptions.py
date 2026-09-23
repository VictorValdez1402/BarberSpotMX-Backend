from typing import Optional
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field
from app.models import SubscriptionStatusEnum


class BarberSubscriptionUpdate(BaseModel):
    barber_id: int
    status: SubscriptionStatusEnum = Field(..., description="ACTIVE, SUSPENDED, TRIAL, PAST_DUE")
    plan_name: str = Field(default="PRO_INDEPENDENT")
    amount_paid: Decimal = Field(default=299.00, gt=0)


class BarbershopSubscriptionUpdate(BaseModel):
    barbershop_id: int
    status: SubscriptionStatusEnum
    plan_name: str = Field(default="SHOP_BASE_3")
    amount_paid: Decimal = Field(default=799.00, gt=0)
    extra_barbers_to_add: int = Field(default=0, ge=0, description="Cantidad de barberos extra a sumar al cupo base")
    cost_per_extra_barber: Decimal = Field(default=150.00, gt=0)


class SubscriptionResponse(BaseModel):
    entity_id: int
    entity_type: str
    status: SubscriptionStatusEnum
    allowed_barbers_count: Optional[int] = None
    message: str
    updated_at: datetime