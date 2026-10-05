from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
)


# ============================================================
# Organization
# ============================================================

class OrganizationOut(BaseModel):
    id: int
    code: str
    name: str

    model_config = ConfigDict(
        from_attributes=True,
    )


# ============================================================
# Plant
# ============================================================

class PlantCreate(BaseModel):
    organization_id: int
    name: str
    phase: str | None = None
    code: str | None = None
    location: str | None = None


class PlantOut(PlantCreate):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
    )


# ============================================================
# SCADA Document
# ============================================================

class ScadaDocumentOut(BaseModel):
    id: int

    plant_id: int

    original_filename: str
    storage_path: str

    content_type: str | None
    file_size: int | None

    ai_status: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )