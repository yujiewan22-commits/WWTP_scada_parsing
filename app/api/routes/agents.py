import json

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models import (
    ScadaDocument,
    ScadaFacilityAnalysis,
    ScadaFacilityUnitAnalysis,
)

from app.services.scada_analysis_service import (
    ScadaAnalysisService,
)


router = APIRouter(
    tags=["SCADA Agents"]
)


# ================================================================
# Agent 1
# 一张 SCADA 图 -> 0~N 个 Facility
# ================================================================

@router.post(
    "/agents/documents/{document_id}/facility"
)
def run_facility_agent(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = db.get(
        ScadaDocument,
        document_id,
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    service = ScadaAnalysisService(
        db
    )

    try:
        result = service.run_facility_agent(
            document
        )

        return result.model_dump()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ================================================================
# Agent 2
#
# 不允许用户再输入 facility_code
#
# 自动读取 Agent 1 最新结果
# 自动遍历所有 facility_candidates
# ================================================================

@router.post(
    "/agents/documents/{document_id}/facility-units"
)
def run_facility_unit_agents(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = db.get(
        ScadaDocument,
        document_id,
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    service = ScadaAnalysisService(
        db
    )

    try:
        return service.run_facility_unit_agents(
            document
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ================================================================
# 查询 Agent 1 最近一次结果
# ================================================================

@router.get(
    "/agents/documents/{document_id}/facility/latest"
)
def latest_facility_analysis(
    document_id: int,
    db: Session = Depends(get_db),
):
    row = db.scalar(
        select(
            ScadaFacilityAnalysis
        )
        .where(
            ScadaFacilityAnalysis.document_id
            == document_id
        )
        .order_by(
            ScadaFacilityAnalysis.id.desc()
        )
    )

    if not row:
        raise HTTPException(
            status_code=404,
            detail="No facility analysis",
        )

    return {
        "id": row.id,
        "status": row.status,
        "provider": row.provider,
        "result": (
            json.loads(row.result_json)
            if row.result_json
            else None
        ),
        "error_message": row.error_message,
    }


# ================================================================
# 查询 Agent 2 历史结果
# ================================================================

@router.get(
    "/agents/documents/{document_id}/facility-units"
)
def list_facility_unit_analyses(
    document_id: int,
    db: Session = Depends(get_db),
):
    rows = list(
        db.scalars(
            select(
                ScadaFacilityUnitAnalysis
            )
            .where(
                ScadaFacilityUnitAnalysis.document_id
                == document_id
            )
            .order_by(
                ScadaFacilityUnitAnalysis.id.desc()
            )
        )
    )

    return [
        {
            "id": row.id,
            "facility_code": (
                row.facility_code
            ),
            "facility_standard_name": (
                row.facility_standard_name
            ),
            "status": row.status,
            "provider": row.provider,
            "result": (
                json.loads(
                    row.result_json
                )
                if row.result_json
                else None
            ),
            "error_message": (
                row.error_message
            ),
        }
        for row in rows
    ]