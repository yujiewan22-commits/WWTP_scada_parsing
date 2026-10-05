from app.ai.prompts import FACILITY_UNIT_AGENT_BASE_PROMPT
from app.ai.provider import ScadaAIProvider
from app.ai.schemas import ScadaFacilityUnitResult
from app.domain.facility_catalog import facility_name_by_code
from app.domain.facility_unit_rules import get_facility_unit_rule


class ScadaFacilityUnitAgent:
    """Agent 2：判断SCADA截图中的主要构筑物单元。"""

    def __init__(self, provider: ScadaAIProvider):
        self.provider = provider

    def analyze(
        self,
        file_path: str,
        filename: str,
        facility_code: str,
        facility_standard_name: str,
    ) -> ScadaFacilityUnitResult:
        facility_code = str(facility_code).zfill(2)

        expected_name = facility_name_by_code(facility_code)
        if not expected_name:
            raise ValueError(f"未知设施编码: {facility_code}")

        if expected_name != facility_standard_name:
            raise ValueError(
                f"设施编码与名称不一致：{facility_code} 应对应“{expected_name}”，"
                f"收到“{facility_standard_name}”"
            )

        rule = get_facility_unit_rule(facility_code)
        if not rule:
            raise ValueError(f"设施 {facility_code} 未配置FacilityUnit识别规则")

        if rule["primary_unit"] == "NONE":
            return ScadaFacilityUnitResult(
                facility_code=facility_code,
                facility_standard_name=facility_standard_name,
                primary_unit="NONE",
                unit_count=None,
                confidence=1.0,
                uncertainties=["该设施类型不需要识别构筑物单元"],
            )

        prompt = (
            FACILITY_UNIT_AGENT_BASE_PROMPT
            .replace("{facility_code}", facility_code)
            .replace(
                "{facility_standard_name}",
                facility_standard_name,
            )
            .replace(
                "{primary_unit}",
                rule["primary_unit"],
            )
            .replace(
                "{recognition_goal}",
                rule["recognition_goal"],
            )
            .replace(
                "{exclude}",
                rule["exclude"],
            )
        )

        result = self.provider.analyze_facility_unit(
            file_path=file_path,
            filename=filename,
            prompt=prompt,
        )

        # Agent 1确定的Facility身份优先，禁止Agent 2改写。
        result.facility_code = facility_code
        result.facility_standard_name = facility_standard_name
        result.primary_unit = rule["primary_unit"]

        return result
