from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from geoalchemy2.elements import WKTElement

from app.database import get_db
from app.models import User, Barbershop, UserRole
from app.schemas.barbershops import (
    BarbershopCreate,
    BarbershopUpdate,
    BarbershopSocialsUpdate,
    BarbershopResponse
)
from app.utils.security import get_current_active_user

router = APIRouter(prefix="/barbershops", tags=["Barbershops"])


@router.post("/", response_model=BarbershopResponse, status_code=status.HTTP_201_CREATED)
def create_barbershop(
    shop_in: BarbershopCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    point = WKTElement(f"POINT({shop_in.longitude} {shop_in.latitude})", srid=4326)
    barbershop = Barbershop(
        owner_id=current_user.id,
        name=shop_in.name,
        description=shop_in.description,
        address=shop_in.address,
        phone=shop_in.phone,
        instagram_url=shop_in.instagram_url,
        tiktok_url=shop_in.tiktok_url,
        facebook_url=shop_in.facebook_url,
        website_url=shop_in.website_url,
        latitude=shop_in.latitude,
        longitude=shop_in.longitude,
        location=point
    )

    db.add(barbershop)
    db.commit()
    db.refresh(barbershop)
    return barbershop


@router.get("/my-shops", response_model=List[BarbershopResponse])
def get_my_barbershops(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return db.query(Barbershop).filter(Barbershop.owner_id == current_user.id).all()


@router.patch("/{barbershop_id}/socials", response_model=BarbershopResponse)
def update_barbershop_socials(
    barbershop_id: int,
    socials: BarbershopSocialsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    shop = db.query(Barbershop).filter(Barbershop.id == barbershop_id).first()
    if not shop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Barbería no encontrada")

    if shop.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para modificar esta barbería")

    update_data = socials.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(shop, field, value)

    db.commit()
    db.refresh(shop)
    return shop


@router.patch("/{barbershop_id}", response_model=BarbershopResponse)
def update_barbershop(
    barbershop_id: int,
    shop_update: BarbershopUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    shop = db.query(Barbershop).filter(Barbershop.id == barbershop_id).first()
    if not shop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Barbería no encontrada")

    if shop.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para modificar esta barbería")

    update_data = shop_update.model_dump(exclude_unset=True)

    lat = update_data.get("latitude", shop.latitude)
    lon = update_data.get("longitude", shop.longitude)
    if "latitude" in update_data or "longitude" in update_data:
        shop.location = WKTElement(f"POINT({lon} {lat})", srid=4326)

    for field, value in update_data.items():
        setattr(shop, field, value)

    db.commit()
    db.refresh(shop)
    return shop


@router.get("/{barbershop_id}", response_model=BarbershopResponse)
def get_barbershop_by_id(barbershop_id: int, db: Session = Depends(get_db)):
    shop = db.query(Barbershop).filter(Barbershop.id == barbershop_id).first()
    if not shop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Barbería no encontrada")
    return shop


@router.get("/", response_model=List[BarbershopResponse])
def list_barbershops(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return db.query(Barbershop).offset(skip).limit(limit).all()