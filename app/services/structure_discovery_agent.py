from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from app.models.document import Document
from app.models.document_analysis import DocumentAnalysis
from app.models.structure_candidate import StructureCandidate
from app.models.candidate_evidence import CandidateEvidence
from app.ai.provider import get_structure_provider
import json

def _norm_name(name: str) -> str:
    return name.strip().replace(" ", "").replace("　", "").replace("系统系统", "系统")

def _merge_key(entity_type: str, name: str, parent_name: str | None = None) -> str:
    key = f"{entity_type}:{_norm_name(name)}"
    return key + (f":{_norm_name(parent_name)}" if parent_name else "")

class StructureDiscoveryAgent:
    def __init__(self, db: Session):
        self.db = db
        self.provider = get_structure_provider()

    def analyze_document(self, document: Document):
        analysis = self.db.scalar(select(DocumentAnalysis).where(DocumentAnalysis.document_id == document.id))
        if not analysis:
            analysis = DocumentAnalysis(document_id=document.id)
            self.db.add(analysis)
            self.db.flush()
        analysis.analysis_status = "RUNNING"
        self.db.commit()
        try:
            result = self.provider.analyze(document.storage_path, document.original_filename)
            analysis.analysis_status = "SUCCEEDED"
            analysis.provider = type(self.provider).__name__
            analysis.document_type = result.document_type
            analysis.title = result.title
            analysis.drawing_no = result.drawing_no
            analysis.discipline = result.discipline
            analysis.year = result.year
            analysis.raw_result_json = json.dumps(result.model_dump(),ensure_ascii=False)
            analysis.error_message = None
            document.ai_status = "ANALYZED"
            if result.document_type: document.document_type = result.document_type
            if result.title: document.title = result.title
            if result.drawing_no: document.drawing_no = result.drawing_no
            if result.discipline: document.discipline = result.discipline
            if result.year: document.year = result.year
            self.db.commit()
            return result
        except Exception as e:
            analysis.analysis_status = "FAILED"
            analysis.error_message = str(e)
            document.ai_status = "FAILED"
            self.db.commit()
            raise

    def discover_plant(self, plant_id: int, reset_candidates: bool = True) -> dict:
        documents = self.db.scalars(select(Document).where(Document.plant_id == plant_id).order_by(Document.id)).all()
        if reset_candidates:
            ids = self.db.scalars(select(StructureCandidate.id).where(StructureCandidate.plant_id == plant_id)).all()
            if ids:
                self.db.execute(delete(CandidateEvidence).where(CandidateEvidence.candidate_id.in_(ids)))
            self.db.execute(delete(StructureCandidate).where(StructureCandidate.plant_id == plant_id))
            self.db.commit()

        results, failures = [], []
        for doc in documents:
            try:
                results.append((doc, self.analyze_document(doc)))
            except Exception as e:
                failures.append({"document_id": doc.id, "filename": doc.original_filename, "error": str(e)})

        buckets = {"process_system": {}, "facility": {}, "facility_unit": {}}

        def get_or_create(entity_type, name, confidence, subtype=None, quantity=None, parent=None):
            parent_name = parent.name if parent else None
            key = _merge_key(entity_type, name, parent_name)
            if key in buckets[entity_type]:
                obj = buckets[entity_type][key]
                obj.confidence = max(obj.confidence or 0, confidence)
                if quantity and not obj.quantity: obj.quantity = quantity
                return obj
            obj = StructureCandidate(
                plant_id=plant_id, entity_type=entity_type, name=name, canonical_name=name,
                entity_subtype=subtype, quantity=quantity,
                parent_candidate_id=parent.id if parent else None,
                confidence=confidence, status="CANDIDATE", merge_key=key
            )
            self.db.add(obj); self.db.flush()
            buckets[entity_type][key] = obj
            return obj

        for doc, result in results:
            local_systems = {}
            for s in result.process_systems:
                obj = get_or_create("process_system", s.name, s.confidence, s.system_type)
                local_systems[_norm_name(s.name)] = obj
                for ev in s.evidence:
                    self.db.add(CandidateEvidence(candidate_id=obj.id, document_id=doc.id, confidence=s.confidence,
                        evidence_text=ev.text, source_region=ev.region, source_page=ev.page))
            for f in result.facilities:
                parent = local_systems.get(_norm_name(f.process_system_name)) if f.process_system_name else None
                if f.process_system_name and not parent:
                    parent = get_or_create("process_system", f.process_system_name, max(0.5, f.confidence - 0.1))
                fobj = get_or_create("facility", f.name, f.confidence, f.facility_type, parent=parent)
                for ev in f.evidence:
                    self.db.add(CandidateEvidence(candidate_id=fobj.id, document_id=doc.id, confidence=f.confidence,
                        evidence_text=ev.text, source_region=ev.region, source_page=ev.page))
                for u in f.units:
                    uobj = get_or_create("facility_unit", u.name, u.confidence, u.unit_type, u.quantity, fobj)
                    for ev in u.evidence:
                        self.db.add(CandidateEvidence(candidate_id=uobj.id, document_id=doc.id, confidence=u.confidence,
                            evidence_text=ev.text, source_region=ev.region, source_page=ev.page))
        self.db.commit()
        candidates = self.db.scalars(select(StructureCandidate).where(StructureCandidate.plant_id == plant_id).order_by(StructureCandidate.id)).all()
        return {
            "plant_id": plant_id,
            "document_count": len(documents),
            "analyzed_count": len(results),
            "failed_count": len(failures),
            "failures": failures,
            "candidates": [{
                "id": c.id, "entity_type": c.entity_type, "name": c.name,
                "entity_subtype": c.entity_subtype, "quantity": c.quantity,
                "parent_candidate_id": c.parent_candidate_id,
                "confidence": c.confidence, "status": c.status
            } for c in candidates]
        }
