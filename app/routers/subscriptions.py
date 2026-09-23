from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Barber, Barbershop
from app.schemas.subscriptions import (
    BarberSubscriptionUpdate,
    BarbershopSubscriptionUpdate,
    SubscriptionResponse
)

router = APIRouter(prefix="/api/v1/subscriptions", tags=["Suscripciones SaaS"])


@router.post("/barber/activate", response_model=SubscriptionResponse)
def activate_barber_subscription(payload: BarberSubscriptionUpdate, db: Session = Depends(get_db)):
    barber = db.query(Barber).filter(Barber.id == payload.barber_id).first()
    if not barber:
        raise HTTPException(status_code=404, detail="Barbero no encontrado")

    barber.subscription_status = payload.status
    db.commit()
    db.refresh(barber)

    return SubscriptionResponse(
        entity_id=barber.id,
        entity_type="BARBER",
        status=barber.subscription_status,
        allowed_barbers_count=None,
        message=f"Suscripción de barbero actualizada a {payload.status.value}",
        updated_at=datetime.utcnow()
    )


@router.post("/barbershop/activate", response_model=SubscriptionResponse)
def activate_barbershop_subscription(payload: BarbershopSubscriptionUpdate, db: Session = Depends(get_db)):
    shop = db.query(Barbershop).filter(Barbershop.id == payload.barbershop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Barbería no encontrada")

    shop.subscription_status = payload.status

    if payload.extra_barbers_to_add > 0:
        shop.allowed_barbers_count += payload.extra_barbers_to_add

    db.commit()
    db.refresh(shop)

    total_cost = payload.amount_paid + (payload.extra_barbers_to_add * payload.cost_per_extra_barber)

    return SubscriptionResponse(
        entity_id=shop.id,
        entity_type="BARBERSHOP",
        status=shop.subscription_status,
        allowed_barbers_count=shop.allowed_barbers_count,
        message=f"Plan de barbería actualizado a {payload.status.value}. Cupo total: {shop.allowed_barbers_count} barberos. Total: ${total_cost:.2f} MXN",
        updated_at=datetime.utcnow()
    )