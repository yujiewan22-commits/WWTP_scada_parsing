from app.ai.prompts import FACILITY_AGENT_BASE_PROMPT
from app.ai.provider import ScadaAIProvider
from app.ai.schemas import ScadaFacilityResult
from app.domain.facility_catalog import facility_catalog_prompt_text


class ScadaFacilityAgent:
    """Agent 1：判断SCADA截图所属设施。"""

    def __init__(self, provider: ScadaAIProvider):
        self.provider = provider

    def analyze(self, file_path: str, filename: str) -> ScadaFacilityResult:
        prompt = FACILITY_AGENT_BASE_PROMPT.replace(
            "{facility_catalog}",
            facility_catalog_prompt_text(),
        )
        result = self.provider.analyze_facility(
            file_path=file_path,
            filename=filename,
            prompt=prompt,
        )

        allowed = {"FACILITY", "PLANT_OVERVIEW", "DATA_SCREEN", "UNKNOWN"}
        if result.page_category not in allowed:
            result.page_category = "UNKNOWN"
            result.facility_candidates = []
            result.uncertainties.append("模型返回了非法page_category，已转为UNKNOWN")

        return result
