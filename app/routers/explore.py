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
    only_active: bool = Query(True, description="Filtrar perfiles activos"),
    db: Session = Depends(get_db)
):
    radius_meters = radius_km * 1000.0

    # Consulta espacial para Barberías (usando las columnas existentes en Neon)
    shops_query = text("""
        SELECT 
            s.id,
            s.name,
            s.phone,
            s.avatar_url,
            COALESCE(s.address_text, '') AS address_text,
            COALESCE(s.years_in_service, 0) AS years_in_service,
            ST_Y(s.location::geometry) AS latitude,
            ST_X(s.location::geometry) AS longitude,
            ROUND((ST_Distance(s.location::geography, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography) / 1000.0)::numeric, 2) AS distance_km
        FROM barbershops s
        WHERE s.location IS NOT NULL
          AND ST_DWithin(s.location::geography, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography, :radius_meters)
    """)

    shops_res = db.execute(
        shops_query,
        {
            "lng": lng,
            "lat": lat,
            "radius_meters": radius_meters
        }
    ).mappings().all()

    results = []

    for row in shops_res:
        results.append(
            NearbyResultItem(
                id=row["id"],
                entity_type="BARBERSHOP",
                name=row["name"],
                phone=row["phone"],
                avatar_url=row["avatar_url"],
                distance_km=float(row["distance_km"]),
                base_cut_price=None,
                years_in_service=row["years_in_service"],
                address_text=row["address_text"],
                latitude=float(row["latitude"]) if row["latitude"] is not None else None,
                longitude=float(row["longitude"]) if row["longitude"] is not None else None
            )
        )

    results.sort(key=lambda item: item.distance_km)

    return {
        "latitude": lat,
        "longitude": lng,
        "radius_km": radius_km,
        "total_found": len(results),
        "results": results
    }