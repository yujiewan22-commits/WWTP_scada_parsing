from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models import (
    Organization,
    Plant,
)

from app.schemas.entities import (
    OrganizationOut,
    PlantCreate,
    PlantOut,
)


router = APIRouter(
    tags=["Master Data"]
)


# ============================================================
# Organization
# 后端固定维护，只提供查询
# ============================================================

@router.get(
    "/organizations",
    response_model=list[OrganizationOut],
)
def list_organizations(
    db: Session = Depends(get_db),
):
    return list(
        db.scalars(
            select(Organization)
            .order_by(Organization.id)
        )
    )


# ============================================================
# Plant
# ============================================================

@router.post(
    "/plants",
    response_model=PlantOut,
)
def create_plant(
    payload: PlantCreate,
    db: Session = Depends(get_db),
):
    organization = db.get(
        Organization,
        payload.organization_id,
    )

    if not organization:
        raise HTTPException(
            status_code=400,
            detail="organization_id 不存在",
        )

    # plant code 如果填写，检查重复
    if payload.code:
        existing = db.scalar(
            select(Plant)
            .where(
                Plant.code == payload.code
            )
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Plant code {payload.code} 已存在",
            )

    plant = Plant(
        **payload.model_dump()
    )

    db.add(plant)
    db.commit()
    db.refresh(plant)

    return plant


@router.get(
    "/plants",
    response_model=list[PlantOut],
)
def list_plants(
    db: Session = Depends(get_db),
):
    return list(
        db.scalars(
            select(Plant)
            .order_by(Plant.id)
        )
    )


@router.get(
    "/plants/{plant_id}",
    response_model=PlantOut,
)
def get_plant(
    plant_id: int,
    db: Session = Depends(get_db),
):
    plant = db.get(
        Plant,
        plant_id,
    )

    if not plant:
        raise HTTPException(
            status_code=404,
            detail="Plant not found",
        )

    return plant