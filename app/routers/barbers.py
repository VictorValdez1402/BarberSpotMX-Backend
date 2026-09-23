from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from geoalchemy2.elements import WKTElement

from app.database import get_db
from app.models import User, BarberProfile, UserRole, Barbershop
from app.schemas.barbers import (
    BarberCreate,
    BarberUpdate,
    BarberSocialsUpdate,
    BarberResponse
)
from app.utils.security import get_current_active_user

router = APIRouter(prefix="/barbers", tags=["Barbers"])


@router.post("/", response_model=BarberResponse, status_code=status.HTTP_201_CREATED)
def create_barber_profile(
    barber_in: BarberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    existing = db.query(BarberProfile).filter(BarberProfile.user_id == current_user.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya tiene un perfil de barbero asignado"
        )

    location_geom = None
    if barber_in.latitude is not None and barber_in.longitude is not None:
        location_geom = WKTElement(f"POINT({barber_in.longitude} {barber_in.latitude})", srid=4326)

    barber = BarberProfile(
        user_id=current_user.id,
        barbershop_id=barber_in.barbershop_id,
        bio=barber_in.bio,
        years_of_experience=barber_in.years_of_experience,
        specialties=barber_in.specialties,
        instagram_url=barber_in.instagram_url,
        tiktok_url=barber_in.tiktok_url,
        facebook_url=barber_in.facebook_url,
        website_url=barber_in.website_url,
        is_independent=barber_in.is_independent,
        is_available=barber_in.is_available,
        latitude=barber_in.latitude,
        longitude=barber_in.longitude,
        location=location_geom
    )

    db.add(barber)
    db.commit()
    db.refresh(barber)
    return barber


@router.get("/me", response_model=BarberResponse)
def get_my_barber_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    barber = db.query(BarberProfile).filter(BarberProfile.user_id == current_user.id).first()
    if not barber:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil de barbero no encontrado")
    return barber


@router.patch("/me/socials", response_model=BarberResponse)
def update_my_socials(
    socials: BarberSocialsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    barber = db.query(BarberProfile).filter(BarberProfile.user_id == current_user.id).first()
    if not barber:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil de barbero no encontrado")

    update_data = socials.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(barber, field, value)

    db.commit()
    db.refresh(barber)
    return barber


@router.patch("/me", response_model=BarberResponse)
def update_my_profile(
    barber_update: BarberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    barber = db.query(BarberProfile).filter(BarberProfile.user_id == current_user.id).first()
    if not barber:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil de barbero no encontrado")

    update_data = barber_update.model_dump(exclude_unset=True)

    lat = update_data.get("latitude", barber.latitude)
    lon = update_data.get("longitude", barber.longitude)
    if "latitude" in update_data or "longitude" in update_data:
        if lat is not None and lon is not None:
            barber.location = WKTElement(f"POINT({lon} {lat})", srid=4326)

    for field, value in update_data.items():
        setattr(barber, field, value)

    db.commit()
    db.refresh(barber)
    return barber


@router.get("/{barber_id}", response_model=BarberResponse)
def get_barber_by_id(barber_id: int, db: Session = Depends(get_db)):
    barber = db.query(BarberProfile).filter(BarberProfile.id == barber_id).first()
    if not barber:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Barbero no encontrado")
    return barber


@router.get("/", response_model=List[BarberResponse])
def list_barbers(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return db.query(BarberProfile).offset(skip).limit(limit).all()