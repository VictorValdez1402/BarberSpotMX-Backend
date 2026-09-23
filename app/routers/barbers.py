from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from geoalchemy2.elements import WKTElement
from app.database import get_db
from app.models import Barber, ServiceCatalog, PackageCatalog, User, RoleEnum
from app.schemas.barbers import (
    BarberProfileCreate,
    BarberProfileResponse,
    BarberPackageItem
)

router = APIRouter(prefix="/api/v1/barbers", tags=["Barberos Independientes"])


@router.post("/profile/{user_id}", response_model=BarberProfileResponse, status_code=status.HTTP_201_CREATED)
def create_barber_profile(user_id: int, payload: BarberProfileCreate, db: Session = Depends(get_db)):
    # 1. Validar existencia del usuario y su rol
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if user.role != RoleEnum.INDEPENDENT_BARBER:
        raise HTTPException(status_code=400, detail="El rol del usuario debe ser INDEPENDENT_BARBER")

    # 2. Evitar perfiles duplicados
    existing_barber = db.query(Barber).filter(Barber.user_id == user_id).first()
    if existing_barber:
        raise HTTPException(status_code=400, detail="El perfil del barbero ya existe")

    # 3. Formatear coordenadas geográficas para PostGIS (WGS 84) si se indicaron
    location_geom = None
    if payload.longitude is not None and payload.latitude is not None:
        location_geom = WKTElement(f"POINT({payload.longitude} {payload.latitude})", srid=4326)

    # 4. Crear entidad Barbero
    new_barber = Barber(
        user_id=user_id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        stage_name=payload.stage_name,
        age=payload.age,
        phone=payload.phone,
        bio=payload.bio,
        location=location_geom
    )
    db.add(new_barber)
    db.flush()

    # 5. Insertar precio obligatorio del corte base
    base_cut = ServiceCatalog(
        barber_id=new_barber.id,
        service_name="Corte",
        price=payload.base_cut_price,
        is_base_cut=True
    )
    db.add(base_cut)

    db.commit()
    db.refresh(new_barber)
    return new_barber


@router.post("/{barber_id}/packages", status_code=status.HTTP_201_CREATED)
def add_package(barber_id: int, payload: BarberPackageItem, db: Session = Depends(get_db)):
    barber = db.query(Barber).filter(Barber.id == barber_id).first()
    if not barber:
        raise HTTPException(status_code=404, detail="Barbero no encontrado")

    # Validar límite de negocio: Máximo 3 paquetes para independientes
    current_packages = db.query(PackageCatalog).filter(PackageCatalog.barber_id == barber_id).count()
    if current_packages >= 3:
        raise HTTPException(
            status_code=400,
            detail="Los barberos independientes solo pueden agregar hasta 3 paquetes o combos"
        )

    package = PackageCatalog(
        barber_id=barber_id,
        title=payload.title,
        description=payload.description,
        price=payload.price
    )
    db.add(package)
    db.commit()
    return {"message": "Paquete agregado con éxito"}