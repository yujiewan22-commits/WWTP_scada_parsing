from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.deps import get_db
from app.models.document import Document
from app.models.plant import Plant
from app.models.structure_candidate import StructureCandidate
from app.models.candidate_evidence import CandidateEvidence
from app.services.structure_discovery_agent import StructureDiscoveryAgent

router = APIRouter()

@router.post("/documents/{document_id}/analyze")
def analyze_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    try:
        return StructureDiscoveryAgent(db).analyze_document(doc).model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/plants/{plant_id}/discover-structure")
def discover_plant_structure(plant_id: int, db: Session = Depends(get_db)):
    if not db.get(Plant, plant_id):
        raise HTTPException(status_code=404, detail="Plant not found")
    try:
        return StructureDiscoveryAgent(db).discover_plant(plant_id, True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plants/{plant_id}/discovery-result")
def get_discovery_result(plant_id: int, db: Session = Depends(get_db)):
    candidates = db.scalars(select(StructureCandidate).where(StructureCandidate.plant_id == plant_id).order_by(StructureCandidate.id)).all()
    out = []
    for c in candidates:
        evs = db.scalars(select(CandidateEvidence).where(CandidateEvidence.candidate_id == c.id).order_by(CandidateEvidence.id)).all()
        out.append({
            "id": c.id, "entity_type": c.entity_type, "name": c.name,
            "entity_subtype": c.entity_subtype, "quantity": c.quantity,
            "parent_candidate_id": c.parent_candidate_id,
            "confidence": c.confidence, "status": c.status,
            "evidence": [{"document_id": e.document_id, "confidence": e.confidence, "text": e.evidence_text,
                          "region": e.source_region, "page": e.source_page} for e in evs]
        })
    return {"plant_id": plant_id, "candidates": out}
