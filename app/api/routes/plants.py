from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.deps import get_db
from app.models.plant import Plant
from app.schemas.entities import PlantCreate, PlantOut

router = APIRouter()

@router.post("", response_model=PlantOut)
def create_plant(payload: PlantCreate, db: Session = Depends(get_db)):
    obj = Plant(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("", response_model=list[PlantOut])
def list_plants(db: Session = Depends(get_db)):
    return db.scalars(select(Plant).order_by(Plant.id)).all()
