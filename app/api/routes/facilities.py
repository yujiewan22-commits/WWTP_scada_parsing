from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.deps import get_db
from app.models.facility import Facility
from app.schemas.entities import FacilityCreate, FacilityOut

router = APIRouter()

@router.post("", response_model=FacilityOut)
def create_facility(payload: FacilityCreate, db: Session = Depends(get_db)):
    obj = Facility(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("", response_model=list[FacilityOut])
def list_facilities(
    plant_id: int | None = None,
    process_system_id: int | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(Facility)
    if plant_id is not None:
        stmt = stmt.where(Facility.plant_id == plant_id)
    if process_system_id is not None:
        stmt = stmt.where(Facility.process_system_id == process_system_id)
    return db.scalars(stmt.order_by(Facility.id)).all()
