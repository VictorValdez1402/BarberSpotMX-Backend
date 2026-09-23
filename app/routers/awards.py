from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Barber, BarberAward, BarberPortfolioImage, VerificationStatusEnum
from app.schemas.awards import (
    AwardSubmitRequest,
    AwardReviewRequest,
    AwardResponse,
    PortfolioImageAdd
)

router = APIRouter(prefix="/api/v1/barbers", tags=["Medallas y Portafolio"])


# --- PORTAFOLIO (MÁXIMO 6 FOTOS PARA BARBEROS) ---
@router.post("/{barber_id}/portfolio", status_code=status.HTTP_201_CREATED)
def add_portfolio_image(barber_id: int, payload: PortfolioImageAdd, db: Session = Depends(get_db)):
    barber = db.query(Barber).filter(Barber.id == barber_id).first()
    if not barber:
        raise HTTPException(status_code=404, detail="Barbero no encontrado")

    current_photos = db.query(BarberPortfolioImage).filter(BarberPortfolioImage.barber_id == barber_id).count()
    if current_photos >= 6:
        raise HTTPException(status_code=400, detail="Límite alcanzado: máximo 6 imágenes para portafolio de barbero")

    new_img = BarberPortfolioImage(
        barber_id=barber_id,
        image_url=payload.image_url,
        display_order=payload.display_order
    )
    db.add(new_img)
    db.commit()
    return {"message": "Imagen agregada al portafolio exitosamente"}


# --- POSTULACIÓN DE RECONOCIMIENTO / MEDALLA ---
@router.post("/{barber_id}/awards", response_model=AwardResponse, status_code=status.HTTP_201_CREATED)
def submit_award(barber_id: int, payload: AwardSubmitRequest, db: Session = Depends(get_db)):
    barber = db.query(Barber).filter(Barber.id == barber_id).first()
    if not barber:
        raise HTTPException(status_code=404, detail="Barbero no encontrado")

    new_award = BarberAward(
        barber_id=barber_id,
        title=payload.title,
        proof_document_url=payload.proof_document_url,
        status=VerificationStatusEnum.PENDING
    )
    db.add(new_award)
    db.commit()
    db.refresh(new_award)
    return new_award


# --- REVISIÓN ADMINISTRATIVA (APROBAR / RECHAZAR MEDALLA) ---
@router.patch("/awards/{award_id}/review", response_model=AwardResponse)
def review_award(award_id: int, payload: AwardReviewRequest, db: Session = Depends(get_db)):
    award = db.query(BarberAward).filter(BarberAward.id == award_id).first()
    if not award:
        raise HTTPException(status_code=404, detail="Solicitud de medalla no encontrada")

    barber = db.query(Barber).filter(Barber.id == award.barber_id).first()

    # Si pasa a APROBADA y antes no lo estaba, suma la medalla al barbero
    if payload.status == VerificationStatusEnum.APPROVED and award.status != VerificationStatusEnum.APPROVED:
        barber.approved_medals_count += 1
    # Si fue aprobada previamente y se revoca a RECHAZADA, resta el conteo
    elif payload.status == VerificationStatusEnum.REJECTED and award.status == VerificationStatusEnum.APPROVED:
        barber.approved_medals_count = max(0, barber.approved_medals_count - 1)

    award.status = payload.status
    award.review_notes = payload.review_notes
    award.reviewed_at = datetime.utcnow()

    db.commit()
    db.refresh(award)
    return award