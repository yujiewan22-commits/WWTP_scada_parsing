import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.scada_facility_agent import ScadaFacilityAgent
from app.agents.scada_facility_unit_agent import ScadaFacilityUnitAgent
from app.ai.provider import get_scada_provider
from app.models import (
    ScadaDocument,
    ScadaFacilityAnalysis,
    ScadaFacilityUnitAnalysis,
)


class ScadaAnalysisService:
    def __init__(self, db: Session):
        self.db = db

        self.provider = get_scada_provider()

        self.facility_agent = ScadaFacilityAgent(
            self.provider
        )

        self.facility_unit_agent = ScadaFacilityUnitAgent(
            self.provider
        )

    # ============================================================
    # Agent 1
    # SCADA 页面设施识别
    # 一张图 -> 0~N 个 Facility
    # ============================================================

    def run_facility_agent(
        self,
        document: ScadaDocument,
    ):
        analysis = ScadaFacilityAnalysis(
            document_id=document.id,
            status="RUNNING",
            provider=type(self.provider).__name__,
        )

        self.db.add(analysis)

        document.ai_status = "FACILITY_RUNNING"

        self.db.commit()
        self.db.refresh(analysis)

        try:
            result = self.facility_agent.analyze(
                file_path=document.storage_path,
                filename=document.original_filename,
            )

            analysis.status = "SUCCEEDED"

            analysis.result_json = json.dumps(
                result.model_dump(),
                ensure_ascii=False,
            )

            document.ai_status = "FACILITY_ANALYZED"

            self.db.commit()

            return result

        except Exception as e:
            analysis.status = "FAILED"
            analysis.error_message = str(e)

            document.ai_status = "FAILED"

            self.db.commit()

            raise

    # ============================================================
    # 读取 Agent 1 最新成功结果
    # ============================================================

    def latest_facility_result(
        self,
        document_id: int,
    ) -> dict | None:

        analysis = self.db.scalar(
            select(ScadaFacilityAnalysis)
            .where(
                ScadaFacilityAnalysis.document_id == document_id,
                ScadaFacilityAnalysis.status == "SUCCEEDED",
            )
            .order_by(
                ScadaFacilityAnalysis.id.desc()
            )
        )

        if not analysis:
            return None

        if not analysis.result_json:
            return None

        return json.loads(
            analysis.result_json
        )

    # ============================================================
    # Agent 2
    # 自动遍历 Agent 1 返回的所有 Facility
    # 一个 Facility -> 一个 FacilityUnitResult
    # 最终一次返回全部结果
    # ============================================================

    def run_facility_unit_agents(
        self,
        document: ScadaDocument,
    ) -> dict:

        facility_result = self.latest_facility_result(
            document.id
        )

        if not facility_result:
            raise ValueError(
                "请先运行 Agent 1：SCADA设施识别"
            )

        page_category = facility_result.get(
            "page_category",
            "UNKNOWN",
        )

        # --------------------------------------------------------
        # 非 FACILITY 页面
        # 不运行 Agent 2
        # 直接返回空列表
        # --------------------------------------------------------

        if page_category != "FACILITY":
            return {
                "document_id": document.id,
                "page_category": page_category,
                "facility_unit_results": [],
            }

        candidates = (
            facility_result.get(
                "facility_candidates"
            )
            or []
        )

        if not candidates:
            return {
                "document_id": document.id,
                "page_category": page_category,
                "facility_unit_results": [],
            }

        facility_unit_results = []

        document.ai_status = "UNIT_RUNNING"

        self.db.commit()

        # --------------------------------------------------------
        # 对 Agent 1 返回的每个 Facility
        # 分别执行一次 Agent 2
        # --------------------------------------------------------

        for candidate in candidates:

            facility_code = str(
                candidate.get("facility_code")
            ).zfill(2)

            facility_standard_name = (
                candidate.get(
                    "facility_standard_name"
                )
            )

            if not facility_code:
                continue

            if not facility_standard_name:
                continue

            analysis = ScadaFacilityUnitAnalysis(
                document_id=document.id,
                facility_code=facility_code,
                facility_standard_name=facility_standard_name,
                status="RUNNING",
                provider=type(
                    self.provider
                ).__name__,
            )

            self.db.add(analysis)

            self.db.commit()
            self.db.refresh(analysis)

            try:
                result = (
                    self.facility_unit_agent.analyze(
                        file_path=document.storage_path,
                        filename=document.original_filename,
                        facility_code=facility_code,
                        facility_standard_name=facility_standard_name,
                    )
                )

                result_dict = result.model_dump()

                analysis.status = "SUCCEEDED"

                analysis.result_json = json.dumps(
                    result_dict,
                    ensure_ascii=False,
                )

                self.db.commit()

                facility_unit_results.append(
                    result_dict
                )

            except Exception as e:
                analysis.status = "FAILED"

                analysis.error_message = str(e)

                self.db.commit()

                # 一个 Facility 失败
                # 不阻断其他 Facility
                facility_unit_results.append(
                    {
                        "facility_code": facility_code,
                        "facility_standard_name": (
                            facility_standard_name
                        ),
                        "primary_unit": None,
                        "unit_count": None,
                        "layout": None,
                        "unit_style": None,
                        "confidence": 0.0,
                        "evidence": [],
                        "uncertainties": [
                            f"FacilityUnit识别失败：{str(e)}"
                        ],
                    }
                )

        document.ai_status = "UNIT_ANALYZED"

        self.db.commit()

        return {
            "document_id": document.id,
            "page_category": page_category,
            "facility_unit_results": (
                facility_unit_results
            ),
        }