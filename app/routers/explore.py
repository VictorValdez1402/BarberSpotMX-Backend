from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.schemas.explore import NearbySearchResponse, NearbyResultItem

router = APIRouter(prefix="/api/v1/explore", tags=["Exploración Geoespacial"])


@router.get("/nearby", response_model=NearbySearchResponse)
def get_nearby_places(
    lat: float = Query(..., ge=-90, le=90, description="Latitud actual del usuario"),
    lng: float = Query(..., ge=-180, le=180, description="Longitud actual del usuario"),
    radius_km: float = Query(10.0, gt=0, le=50, description="Radio de búsqueda en kilómetros"),
    only_active: bool = Query(True, description="Filtrar únicamente perfiles con suscripción activa (ACTIVE)"),
    db: Session = Depends(get_db)
):
    radius_meters = radius_km * 1000.0

    # 1. Consulta espacial para Barberos Independientes (con filtro de suscripción)
    barbers_query = text("""
        SELECT 
            b.id,
            b.stage_name,
            b.phone,
            b.avatar_url,
            b.approved_medals_count,
            ROUND((ST_Distance(b.location::geography, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography) / 1000.0)::numeric, 2) AS distance_km,
            s.price AS base_cut_price
        FROM barbers b
        LEFT JOIN service_catalog s ON s.barber_id = b.id AND s.is_base_cut = true
        WHERE b.location IS NOT NULL
          AND (:only_active = false OR b.subscription_status = 'ACTIVE')
          AND ST_DWithin(b.location::geography, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography, :radius_meters)
    """)

    barbers_res = db.execute(
        barbers_query,
        {
            "lng": lng,
            "lat": lat,
            "radius_meters": radius_meters,
            "only_active": only_active
        }
    ).mappings().all()

    # 2. Consulta espacial para Barberías (con filtro de suscripción)
    shops_query = text("""
        SELECT 
            s.id,
            s.name,
            s.phone,
            s.avatar_url,
            s.years_in_service,
            ROUND((ST_Distance(s.location::geography, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography) / 1000.0)::numeric, 2) AS distance_km,
            sc.price AS base_cut_price
        FROM barbershops s
        LEFT JOIN service_catalog sc ON sc.barbershop_id = s.id AND sc.is_base_cut = true
        WHERE s.location IS NOT NULL
          AND (:only_active = false OR s.subscription_status = 'ACTIVE')
          AND ST_DWithin(s.location::geography, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography, :radius_meters)
    """)

    shops_res = db.execute(
        shops_query,
        {
            "lng": lng,
            "lat": lat,
            "radius_meters": radius_meters,
            "only_active": only_active
        }
    ).mappings().all()

    results = []

    for row in barbers_res:
        results.append(
            NearbyResultItem(
                id=row["id"],
                entity_type="BARBER",
                name=row["stage_name"],
                phone=row["phone"],
                avatar_url=row["avatar_url"],
                distance_km=float(row["distance_km"]),
                base_cut_price=row["base_cut_price"],
                approved_medals_count=row["approved_medals_count"]
            )
        )

    for row in shops_res:
        results.append(
            NearbyResultItem(
                id=row["id"],
                entity_type="BARBERSHOP",
                name=row["name"],
                phone=row["phone"],
                avatar_url=row["avatar_url"],
                distance_km=float(row["distance_km"]),
                base_cut_price=row["base_cut_price"],
                years_in_service=row["years_in_service"]
            )
        )

    # Ordenar por cercanía en km
    results.sort(key=lambda item: item.distance_km)

    return {
        "latitude": lat,
        "longitude": lng,
        "radius_km": radius_km,
        "total_found": len(results),
        "results": results
    }