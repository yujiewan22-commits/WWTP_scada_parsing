from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.deps import get_db
from app.models.project_type import ProjectType
from app.schemas.entities import ProjectTypeCreate, ProjectTypeOut

router = APIRouter()

@router.post("", response_model=ProjectTypeOut)
def create_project_type(payload: ProjectTypeCreate, db: Session = Depends(get_db)):
    obj = ProjectType(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("", response_model=list[ProjectTypeOut])
def list_project_types(db: Session = Depends(get_db)):
    return db.scalars(select(ProjectType).order_by(ProjectType.id)).all()
