from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.deps import get_db
from app.models.document_link import DocumentStructureLink
from app.schemas.entities import DocumentLinkCreate, DocumentLinkOut

router = APIRouter()

@router.post("", response_model=DocumentLinkOut)
def create_document_link(payload: DocumentLinkCreate, db: Session = Depends(get_db)):
    obj = DocumentStructureLink(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("", response_model=list[DocumentLinkOut])
def list_document_links(
    document_id: int | None = None,
    entity_type: str | None = None,
    entity_id: int | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(DocumentStructureLink)
    if document_id is not None:
        stmt = stmt.where(DocumentStructureLink.document_id == document_id)
    if entity_type is not None:
        stmt = stmt.where(DocumentStructureLink.entity_type == entity_type)
    if entity_id is not None:
        stmt = stmt.where(DocumentStructureLink.entity_id == entity_id)
    return db.scalars(stmt.order_by(DocumentStructureLink.id)).all()
