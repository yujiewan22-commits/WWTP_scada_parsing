from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.deps import get_db
from app.models.plant import Plant
from app.models.process_system import ProcessSystem
from app.models.facility import Facility
from app.models.facility_unit import FacilityUnit

router = APIRouter()

@router.get("/plants/{plant_id}")
def get_plant_structure(plant_id: int, db: Session = Depends(get_db)):
    plant = db.get(Plant, plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    systems = db.scalars(
        select(ProcessSystem)
        .where(ProcessSystem.plant_id == plant_id)
        .order_by(ProcessSystem.id)
    ).all()

    result = {
        "plant": {
            "id": plant.id,
            "name": plant.name,
            "phase": plant.phase,
        },
        "systems": []
    }

    for system in systems:
        facilities = db.scalars(
            select(Facility)
            .where(Facility.process_system_id == system.id)
            .order_by(Facility.id)
        ).all()

        facility_list = []
        for facility in facilities:
            units = db.scalars(
                select(FacilityUnit)
                .where(FacilityUnit.facility_id == facility.id)
                .order_by(FacilityUnit.id)
            ).all()

            facility_list.append({
                "id": facility.id,
                "name": facility.canonical_name,
                "facility_type": facility.facility_type,
                "status": facility.status,
                "units": [
                    {
                        "id": unit.id,
                        "name": unit.name,
                        "unit_type": unit.unit_type,
                        "sequence_no": unit.sequence_no,
                        "quantity": unit.quantity,
                        "status": unit.status,
                    }
                    for unit in units
                ]
            })

        result["systems"].append({
            "id": system.id,
            "name": system.name,
            "system_type": system.system_type,
            "status": system.status,
            "facilities": facility_list,
        })

    # 允许 facility 暂时没有 process_system
    orphan_facilities = db.scalars(
        select(Facility)
        .where(
            Facility.plant_id == plant_id,
            Facility.process_system_id.is_(None)
        )
        .order_by(Facility.id)
    ).all()

    if orphan_facilities:
        result["unassigned_facilities"] = []
        for facility in orphan_facilities:
            units = db.scalars(
                select(FacilityUnit)
                .where(FacilityUnit.facility_id == facility.id)
                .order_by(FacilityUnit.id)
            ).all()
            result["unassigned_facilities"].append({
                "id": facility.id,
                "name": facility.canonical_name,
                "facility_type": facility.facility_type,
                "status": facility.status,
                "units": [
                    {
                        "id": unit.id,
                        "name": unit.name,
                        "unit_type": unit.unit_type,
                        "sequence_no": unit.sequence_no,
                        "quantity": unit.quantity,
                        "status": unit.status,
                    }
                    for unit in units
                ]
            })

    return result

@router.post("/plants/{plant_id}/discover")
def discover_plant_structure_placeholder(plant_id: int, db: Session = Depends(get_db)):
    plant = db.get(Plant, plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    return {
        "plant_id": plant_id,
        "status": "NOT_IMPLEMENTED",
        "message": "AI结构发现接口已预留，下一步接入PDF/SCADA多模态分析。"
    }
