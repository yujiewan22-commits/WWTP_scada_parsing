import json, re
from pathlib import Path
import httpx
from app.core.config import settings
from app.ai.schemas import DocumentStructureResult
from app.ai.prompts import STRUCTURE_DISCOVERY_PROMPT
from app.services.document_media import load_document_images

class AIProviderError(RuntimeError):
    pass

def _safe_json_loads(text: str) -> dict:
    text = text.strip()

    # 去掉 Markdown JSON 代码块
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()

    # 找到第一个 JSON 对象开始位置
    start = text.find("{")
    if start == -1:
        raise ValueError(f"模型返回中未找到 JSON 对象: {text[:500]}")

    text = text[start:]

    # 只解析第一个完整 JSON 对象，
    # 忽略模型可能附加在后面的说明文字或额外内容
    decoder = json.JSONDecoder()
    obj, end_index = decoder.raw_decode(text)

    if not isinstance(obj, dict):
        raise ValueError("模型返回的顶层 JSON 不是 object")

    return obj

class StructureAIProvider:
    def analyze(self, file_path: str, filename: str) -> DocumentStructureResult:
        raise NotImplementedError

class MockStructureAIProvider(StructureAIProvider):
    def analyze(self, file_path: str, filename: str) -> DocumentStructureResult:
        lower = filename.lower()
        if "二沉" in filename or "secondary" in lower:
            return DocumentStructureResult.model_validate({
                "document_type": "unknown",
                "title": filename,
                "process_systems": [{
                    "name": "二沉系统",
                    "system_type": "secondary_settling",
                    "confidence": 0.70,
                    "evidence": [{"text": f"文件名包含二沉：{filename}", "region": "filename", "page": 1}]
                }],
                "facilities": [{
                    "name": "二沉池",
                    "facility_type": "二沉池",
                    "confidence": 0.75,
                    "process_system_name": "二沉系统",
                    "evidence": [{"text": f"文件名包含二沉：{filename}", "region": "filename", "page": 1}],
                    "units": []
                }]
            })
        return DocumentStructureResult(title=filename, notes=["mock provider 未从文件名识别到结构"])

class OpenAICompatibleStructureProvider(StructureAIProvider):
    def analyze(self, file_path: str, filename: str) -> DocumentStructureResult:
        if not settings.ai_base_url or not settings.ai_api_key or not settings.ai_model:
            raise AIProviderError("AI_BASE_URL / AI_API_KEY / AI_MODEL 未配置")
        images = load_document_images(file_path, settings.ai_max_pdf_pages)
        if not images:
            raise AIProviderError(f"暂不支持该文件类型：{Path(file_path).suffix}")
        content = [{"type": "text", "text": f"{STRUCTURE_DISCOVERY_PROMPT}\n\n当前文件名：{filename}"}]
        for item in images:
            content.append({"type": "text", "text": f"以下是第 {item['page']} 页："})
            content.append({"type": "image_url", "image_url": {"url": item["data_url"],"detail": "original"}})
        payload = {
            "model": settings.ai_model,
            "messages": [{"role": "user", "content": content}],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }
        url = settings.ai_base_url.rstrip("/") + "/chat/completions"
        headers = {"Authorization": f"Bearer {settings.ai_api_key}", "Content-Type": "application/json"}
        with httpx.Client(timeout=settings.ai_timeout_seconds) as client:
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code >= 400:
                raise AIProviderError(f"模型接口错误 {resp.status_code}: {resp.text[:1000]}")
            data = resp.json()
        try:
            text = data["choices"][0]["message"]["content"]

            print("\n========== DeepSeek RAW RESPONSE ==========")
            print(text)
            print("===========================================\n")

            parsed = _safe_json_loads(text)

            return DocumentStructureResult.model_validate(parsed)

        except Exception as e:
            raise AIProviderError(
                f"模型返回解析失败: {e}; "
                f"raw_response={text[:1500] if 'text' in locals() else 'N/A'}"
            )

def get_structure_provider() -> StructureAIProvider:
    provider = settings.ai_provider.lower().strip()
    if provider == "mock":
        return MockStructureAIProvider()
    if provider == "openai_compatible":
        return OpenAICompatibleStructureProvider()
    raise AIProviderError(f"未知 AI_PROVIDER: {settings.ai_provider}")
