from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from geoalchemy2.elements import WKTElement
from app.database import get_db
from app.models import (
    Barbershop,
    BarbershopSchedule,
    Barber,
    ServiceCatalog,
    PackageCatalog,
    User,
    RoleEnum
)
from app.schemas.barbershops import (
    BarbershopCreate,
    BarbershopResponse,
    BarbershopPackageItem,
    AddBarberToShopRequest
)

router = APIRouter(prefix="/api/v1/barbershops", tags=["Barberías"])


@router.post("/register/{owner_id}", response_model=BarbershopResponse, status_code=status.HTTP_201_CREATED)
def create_barbershop(owner_id: int, payload: BarbershopCreate, db: Session = Depends(get_db)):
    # 1. Validar usuario dueño
    owner = db.query(User).filter(User.id == owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Usuario dueño no encontrado")
    if owner.role != RoleEnum.SHOP_OWNER:
        raise HTTPException(status_code=400, detail="El rol del usuario debe ser SHOP_OWNER")

    # 2. Comprobar que no tenga ya una barbería registrada
    existing_shop = db.query(Barbershop).filter(Barbershop.owner_id == owner_id).first()
    if existing_shop:
        raise HTTPException(status_code=400, detail="Este usuario ya cuenta con una barbería registrada")

    # 3. Formatear punto geográfico para PostGIS
    location_geom = WKTElement(f"POINT({payload.longitude} {payload.latitude})", srid=4326)

    # 4. Crear registro de barbería (3 barberos base incluidos)
    new_shop = Barbershop(
        owner_id=owner_id,
        name=payload.name,
        bio=payload.bio,
        years_in_service=payload.years_in_service,
        phone=payload.phone,
        location=location_geom,
        address_text=payload.address_text,
        allowed_barbers_count=3
    )
    db.add(new_shop)
    db.flush()

    # 5. Insertar horarios de apertura y cierre
    for sch in payload.schedules:
        schedule_entry = BarbershopSchedule(
            barbershop_id=new_shop.id,
            day_of_week=sch.day_of_week,
            is_closed=sch.is_closed,
            open_time=sch.open_time,
            close_time=sch.close_time
        )
        db.add(schedule_entry)

    # 6. Insertar precio obligatorio de corte base
    base_cut = ServiceCatalog(
        barbershop_id=new_shop.id,
        service_name="Corte",
        price=payload.base_cut_price,
        is_base_cut=True
    )
    db.add(base_cut)

    db.commit()
    db.refresh(new_shop)
    return new_shop


@router.post("/{barbershop_id}/barbers", status_code=status.HTTP_201_CREATED)
def add_barber_to_shop(barbershop_id: int, payload: AddBarberToShopRequest, db: Session = Depends(get_db)):
    shop = db.query(Barbershop).filter(Barbershop.id == barbershop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Barbería no encontrada")

    # Validar cupo disponible de barberos
    current_barbers_count = db.query(Barber).filter(Barber.barbershop_id == barbershop_id).count()
    if current_barbers_count >= shop.allowed_barbers_count:
        raise HTTPException(
            status_code=400,
            detail=f"Has alcanzado el límite de {shop.allowed_barbers_count} barberos permitidos. Amplía tu plan para registrar más."
        )

    # Registrar barbero asociado a la barbería (hereda la ubicación del local)
    new_barber = Barber(
        user_id=payload.user_id,
        barbershop_id=shop.id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        stage_name=payload.stage_name,
        age=payload.age,
        phone=payload.phone,
        bio=payload.bio,
        location=shop.location
    )
    db.add(new_barber)
    db.commit()
    return {"message": "Barbero asignado exitosamente a la barbería", "barber_stage_name": payload.stage_name}


@router.post("/{barbershop_id}/packages", status_code=status.HTTP_201_CREATED)
def add_barbershop_package(barbershop_id: int, payload: BarbershopPackageItem, db: Session = Depends(get_db)):
    shop = db.query(Barbershop).filter(Barbershop.id == barbershop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Barbería no encontrada")

    # Límite: Máximo 5 paquetes para barberías
    current_packages = db.query(PackageCatalog).filter(PackageCatalog.barbershop_id == barbershop_id).count()
    if current_packages >= 5:
        raise HTTPException(status_code=400, detail="Las barberías solo pueden agregar hasta 5 paquetes o combos")

    package = PackageCatalog(
        barbershop_id=barbershop_id,
        title=payload.title,
        description=payload.description,
        price=payload.price
    )
    db.add(package)
    db.commit()
    return {"message": "Paquete de barbería agregado con éxito"}