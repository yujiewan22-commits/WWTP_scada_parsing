from pydantic import BaseModel, Field

class EvidenceItem(BaseModel):
    text: str
    region: str | None = None
    page: int | None = None

class SystemCandidate(BaseModel):
    name: str
    system_type: str | None = None
    confidence: float = 0.5
    evidence: list[EvidenceItem] = Field(default_factory=list)

class FacilityUnitCandidate(BaseModel):
    name: str
    unit_type: str | None = None
    quantity: int | None = None
    confidence: float = 0.5
    evidence: list[EvidenceItem] = Field(default_factory=list)

class FacilityCandidate(BaseModel):
    name: str
    facility_type: str | None = None
    confidence: float = 0.5
    process_system_name: str | None = None
    units: list[FacilityUnitCandidate] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)

class DocumentStructureResult(BaseModel):
    document_type: str | None = None
    title: str | None = None
    drawing_no: str | None = None
    discipline: str | None = None
    year: int | None = None
    process_systems: list[SystemCandidate] = Field(default_factory=list)
    facilities: list[FacilityCandidate] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
