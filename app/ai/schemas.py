from pydantic import BaseModel, Field


class ScadaEvidence(BaseModel):
    text: str
    region: str | None = None


class ScadaFacilityCandidate(BaseModel):
    facility_code: str
    facility_standard_name: str
    facility_raw_name: str | None = None
    confidence: float = 0.5
    evidence: list[ScadaEvidence] = Field(default_factory=list)
    reason: str | None = None


class ScadaFacilityResult(BaseModel):
    page_title: str | None = None
    page_category: str = "UNKNOWN"
    facility_candidates: list[ScadaFacilityCandidate] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)


class ScadaFacilityUnitResult(BaseModel):
    facility_code: str
    facility_standard_name: str
    primary_unit: str
    unit_count: int | None = None
    layout: str | None = None
    unit_style: str | None = None
    confidence: float = 0.5
    evidence: list[ScadaEvidence] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
