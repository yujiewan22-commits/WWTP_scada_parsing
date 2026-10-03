from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.deps import get_db
from app.models.process_system import ProcessSystem
from app.schemas.entities import ProcessSystemCreate, ProcessSystemOut

router = APIRouter()

@router.post("", response_model=ProcessSystemOut)
def create_process_system(payload: ProcessSystemCreate, db: Session = Depends(get_db)):
    obj = ProcessSystem(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("", response_model=list[ProcessSystemOut])
def list_process_systems(plant_id: int | None = None, db: Session = Depends(get_db)):
    stmt = select(ProcessSystem)
    if plant_id is not None:
        stmt = stmt.where(ProcessSystem.plant_id == plant_id)
    return db.scalars(stmt.order_by(ProcessSystem.id)).all()
