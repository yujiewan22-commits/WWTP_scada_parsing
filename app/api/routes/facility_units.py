from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.deps import get_db
from app.models.facility_unit import FacilityUnit
from app.schemas.entities import FacilityUnitCreate, FacilityUnitOut

router = APIRouter()

@router.post("", response_model=FacilityUnitOut)
def create_facility_unit(payload: FacilityUnitCreate, db: Session = Depends(get_db)):
    obj = FacilityUnit(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("", response_model=list[FacilityUnitOut])
def list_facility_units(facility_id: int | None = None, db: Session = Depends(get_db)):
    stmt = select(FacilityUnit)
    if facility_id is not None:
        stmt = stmt.where(FacilityUnit.facility_id == facility_id)
    return db.scalars(stmt.order_by(FacilityUnit.id)).all()
