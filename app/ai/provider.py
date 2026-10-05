import json
import re

import httpx

from app.core.config import settings
from app.ai.schemas import ScadaFacilityResult, ScadaFacilityUnitResult
from app.services.image_media import image_file_to_data_url


class AIProviderError(RuntimeError):
    pass


def safe_json_loads(text: str) -> dict:
    text = (text or "").strip()

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()

    start = text.find("{")
    if start < 0:
        raise ValueError(f"模型返回中未找到JSON对象: {text[:500]}")

    decoder = json.JSONDecoder()
    obj, _ = decoder.raw_decode(text[start:])

    if not isinstance(obj, dict):
        raise ValueError("模型返回JSON顶层不是object")

    return obj


class ScadaAIProvider:
    def analyze_facility(self, file_path: str, filename: str, prompt: str) -> ScadaFacilityResult:
        raise NotImplementedError

    def analyze_facility_unit(
        self,
        file_path: str,
        filename: str,
        prompt: str,
    ) -> ScadaFacilityUnitResult:
        raise NotImplementedError


class OpenAICompatibleScadaProvider(ScadaAIProvider):
    def _post(self, content: list[dict]) -> dict:
        if not settings.ai_base_url or not settings.ai_api_key or not settings.ai_model:
            raise AIProviderError("AI_BASE_URL / AI_API_KEY / AI_MODEL 未配置")

        payload = {
            "model": settings.ai_model,
            "messages": [
                {
                    "role": "user",
                    "content": content,
                }
            ],
            "temperature": 0.1,
        }

        if settings.ai_json_mode:
            payload["response_format"] = {"type": "json_object"}

        url = settings.ai_base_url.rstrip("/") + "/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.ai_api_key}",
            "Content-Type": "application/json",
        }

        with httpx.Client(timeout=settings.ai_timeout_seconds) as client:
            response = client.post(url, headers=headers, json=payload)

        if response.status_code >= 400:
            raise AIProviderError(
                f"模型接口错误 {response.status_code}: {response.text[:1500]}"
            )

        return response.json()

    @staticmethod
    def _extract_text(response_json: dict) -> str:
        try:
            return response_json["choices"][0]["message"]["content"]
        except Exception as e:
            raise AIProviderError(f"无法读取模型message.content: {e}")

    def analyze_facility(self, file_path: str, filename: str, prompt: str) -> ScadaFacilityResult:
        data_url = image_file_to_data_url(file_path)

        content = [
            {
                "type": "text",
                "text": (
                    prompt
                    + f"\n\n当前文件名：{filename}"
                    + "\n下面是SCADA截图。只执行Agent 1的页面分类和设施识别任务。"
                ),
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": data_url,
                    "detail": "original",
                },
            },
        ]

        response_json = self._post(content)
        text = self._extract_text(response_json)

        print("\n========== AGENT 1 / SCADA FACILITY RAW ==========")
        print(text)
        print("==================================================\n")

        try:
            return ScadaFacilityResult.model_validate(safe_json_loads(text))
        except Exception as e:
            raise AIProviderError(
                f"Agent 1结果解析失败: {e}; raw={text[:2000]}"
            )

    def analyze_facility_unit(
        self,
        file_path: str,
        filename: str,
        prompt: str,
    ) -> ScadaFacilityUnitResult:
        data_url = image_file_to_data_url(file_path)

        content = [
            {
                "type": "text",
                "text": (
                    prompt
                    + f"\n\n当前文件名：{filename}"
                    + "\n下面是同一张SCADA截图。只执行Agent 2的构筑物单元识别任务。"
                ),
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": data_url,
                    "detail": "original",
                },
            },
        ]

        response_json = self._post(content)
        text = self._extract_text(response_json)

        print("\n========== AGENT 2 / SCADA FACILITY UNIT RAW ==========")
        print(text)
        print("=======================================================\n")

        try:
            return ScadaFacilityUnitResult.model_validate(safe_json_loads(text))
        except Exception as e:
            raise AIProviderError(
                f"Agent 2结果解析失败: {e}; raw={text[:2000]}"
            )


def get_scada_provider() -> ScadaAIProvider:
    provider = settings.ai_provider.lower().strip()

    if provider == "openai_compatible":
        return OpenAICompatibleScadaProvider()

    raise AIProviderError(
        f"正式版仅保留 openai_compatible Provider，当前AI_PROVIDER={settings.ai_provider}"
    )
