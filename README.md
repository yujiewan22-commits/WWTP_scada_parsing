# Water Plant AI V3 - Structure Discovery Agent

本版在 V2 基础上新增第一个 AI Agent：

> 对某个 Plant 下已上传的 PDF / SCADA 图片进行分析，生成 `ProcessSystem → Facility → FacilityUnit` 候选结构。

## 新接口

- `POST /api/ai/documents/{document_id}/analyze`：分析单份资料
- `POST /api/ai/plants/{plant_id}/discover-structure`：分析该水厂全部资料并融合候选结构
- `GET /api/ai/plants/{plant_id}/discovery-result`：查看候选结构及证据

## 新表

- `document_analyses`
- `structure_candidates`
- `candidate_evidence`

AI 结果先进入候选表，不直接污染正式主数据。

## 第一次测试：Mock模式

`.env`：

```env
AI_PROVIDER=mock
```

上传一个文件名含“二沉”的 PDF 或 PNG，然后调用：

```text
POST /api/ai/plants/1/discover-structure
```

会得到候选：

```text
二沉系统
└─ 二沉池
```

Mock 只验证流程，不代表真正识别了图片内容。

## 接真实多模态模型

配置一个兼容 OpenAI Chat Completions 的多模态接口：

```env
AI_PROVIDER=openai_compatible
AI_BASE_URL=https://你的服务地址/v1
AI_API_KEY=你的KEY
AI_MODEL=你的多模态模型名
AI_MAX_PDF_PAGES=8
```

PDF 会先用 PyMuPDF 渲染为图片，再发送给多模态模型。

## 启动

建议 Python 3.12：

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Swagger：`http://127.0.0.1:8000/docs`
