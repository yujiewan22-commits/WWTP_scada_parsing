from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.deps import get_db
from app.models.organization import Organization
from app.schemas.entities import OrganizationCreate, OrganizationOut

router = APIRouter()

@router.post("", response_model=OrganizationOut)
def create_organization(payload: OrganizationCreate, db: Session = Depends(get_db)):
    obj = Organization(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("", response_model=list[OrganizationOut])
def list_organizations(db: Session = Depends(get_db)):
    return db.scalars(select(Organization).order_by(Organization.id)).all()
