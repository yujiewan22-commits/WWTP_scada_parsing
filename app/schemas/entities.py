from pydantic import BaseModel, ConfigDict

class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class OrganizationCreate(BaseModel):
    name: str
    short_name: str | None = None
    org_type: str | None = None
    parent_id: int | None = None

class OrganizationOut(ORMBase):
    id: int
    name: str
    short_name: str | None
    org_type: str | None
    parent_id: int | None
    status: str

class ProjectTypeCreate(BaseModel):
    name: str
    code: str
    category: str | None = None
    description: str | None = None

class ProjectTypeOut(ORMBase):
    id: int
    name: str
    code: str
    category: str | None
    description: str | None
    status: str

class PlantCreate(BaseModel):
    organization_id: int | None = None
    name: str
    phase: str | None = None
    code: str | None = None
    location: str | None = None
    design_capacity: float | None = None
    capacity_unit: str | None = "m3/d"

class PlantOut(ORMBase):
    id: int
    organization_id: int | None
    name: str
    phase: str | None
    code: str | None
    location: str | None
    design_capacity: float | None
    capacity_unit: str | None
    status: str

class ProjectCreate(BaseModel):
    name: str
    project_type_id: int
    plant_id: int
    lead_organization_id: int | None = None
    year: int | None = None
    status: str = "in_progress"

class ProjectOut(ORMBase):
    id: int
    name: str
    project_type_id: int
    plant_id: int
    lead_organization_id: int | None
    year: int | None
    status: str

class ProcessSystemCreate(BaseModel):
    plant_id: int
    name: str
    system_type: str | None = None
    aliases: str | None = None
    status: str = "CANDIDATE"
    source: str = "AI"

class ProcessSystemOut(ORMBase):
    id: int
    plant_id: int
    name: str
    system_type: str | None
    aliases: str | None
    status: str
    source: str

class FacilityCreate(BaseModel):
    plant_id: int
    process_system_id: int | None = None
    canonical_name: str
    facility_type: str | None = None
    aliases: str | None = None
    status: str = "CANDIDATE"
    source: str = "AI"

class FacilityOut(ORMBase):
    id: int
    plant_id: int
    process_system_id: int | None
    canonical_name: str
    facility_type: str | None
    aliases: str | None
    status: str
    source: str

class FacilityUnitCreate(BaseModel):
    facility_id: int
    name: str
    unit_type: str | None = None
    sequence_no: int | None = None
    quantity: int | None = None
    status: str = "CANDIDATE"
    source: str = "AI"

class FacilityUnitOut(ORMBase):
    id: int
    facility_id: int
    name: str
    unit_type: str | None
    sequence_no: int | None
    quantity: int | None
    status: str
    source: str

class DocumentOut(ORMBase):
    id: int
    project_id: int
    plant_id: int
    original_filename: str
    stored_filename: str
    storage_path: str
    document_type: str | None
    title: str | None
    drawing_no: str | None
    revision: str | None
    year: int | None
    discipline: str | None
    notes: str | None
    ai_status: str

class DocumentLinkCreate(BaseModel):
    document_id: int
    entity_type: str
    entity_id: int
    confidence: float | None = None
    match_status: str = "CANDIDATE"
    evidence_text: str | None = None
    source_region: str | None = None

class DocumentLinkOut(ORMBase):
    id: int
    document_id: int
    entity_type: str
    entity_id: int
    confidence: float | None
    match_status: str
    evidence_text: str | None
    source_region: str | None
