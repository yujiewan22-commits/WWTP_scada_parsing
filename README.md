# Water Plant SCADA Agents V1

这是当前阶段的**正式版本**，不是补丁。

项目目标已经收敛为：

> 只基于水厂现有 SCADA 截图，为新 SCADA 画图人员提供初步标准水厂信息。

本版本不再开发设计 PDF / DWG 识别，不包含旧版 ProcessSystem 发现、设计图图签识别等实验功能。

## 两个正式智能体

### Agent 1：SCADA设施识别智能体

输入一张 SCADA 截图，输出：

- `page_title`
- `page_category`
  - `FACILITY`
  - `PLANT_OVERVIEW`
  - `DATA_SCREEN`
  - `UNKNOWN`
- `facility_candidates`
  - `facility_code`
  - `facility_standard_name`
  - `facility_raw_name`
  - `confidence`
  - `evidence`
  - `reason`
- `uncertainties`

标准设施表为 00～67，共 68 类。

厂区总平面统一识别为：

`00 厂区平面`

DATA_SCREEN 不进入构筑物单元分析。

### Agent 2：SCADA构筑物单元识别智能体

Agent 2 只分析 Agent 1 已经确认的 `FACILITY` 页面。

不同设施使用不同“主要画图单元”规则，不统一按池体计数。

示例：

- `01 粗格栅间` → 格栅通道 / 格栅布置
- `10 生化池` → 独立处理线 / 池组
- `11 二沉池` → 独立池体 / 处理单元
- `26 鼓风机房` → 风机组 / 供气单元
- `29 加药间` → 独立加药系统 / 药剂线
- `53 膜车间` → 膜处理线 / 膜组

输出：

- `primary_unit`
- `unit_count`
- `layout`
- `unit_style`
- `confidence`
- `evidence`
- `uncertainties`

## 技术栈

- Python 3.12
- FastAPI
- SQLAlchemy 2
- SQLite
- Pydantic 2
- OpenAI-compatible multimodal API

## 安装

PowerShell：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

复制配置：

```powershell
Copy-Item .env.example .env
```

编辑 `.env`：

```env
AI_PROVIDER=openai_compatible
AI_BASE_URL=https://api.deepseek.com
AI_API_KEY=你的Key
AI_MODEL=你实际使用的多模态模型名称
AI_TIMEOUT_SECONDS=120
AI_JSON_MODE=true
```

## 初始化测试基础数据

```powershell
python seed_demo.py
```

会创建：

- organization_id=1
- plant_id=1
- project_id=1

如果数据库已有数据则不会重复写入。

## 启动

```powershell
uvicorn app.main:app --reload
```

Swagger：

`http://127.0.0.1:8000/docs`

根地址：

`http://127.0.0.1:8000/`

## 使用顺序

### 1. 上传SCADA截图

接口：

`POST /api/documents/upload`

填写：

- `project_id`
- `plant_id`
- `file`

只支持：

- PNG
- JPG/JPEG
- WEBP
- BMP

正式版本明确不处理 PDF/DWG。

### 2. 运行 Agent 1

`POST /api/agents/documents/{document_id}/facility`

例如二沉池可能得到：

```json
{
  "page_title": "二三期二沉池",
  "page_category": "FACILITY",
  "facility_candidates": [
    {
      "facility_code": "11",
      "facility_standard_name": "二沉池",
      "facility_raw_name": "二三期二沉池",
      "confidence": 0.98
    }
  ],
  "uncertainties": []
}
```

### 3. 运行 Agent 2

如果 Agent 1 只有一个设施：

`POST /api/agents/documents/{document_id}/facility-unit`

Agent 2 自动使用该设施。

如果 Agent 1 识别到多个候选：

`POST /api/agents/documents/{document_id}/facility-unit?facility_code=11`

必须指定需要分析的设施编码。

### 4. 查看结果

Agent 1 最近结果：

`GET /api/agents/documents/{document_id}/facility/latest`

Agent 2 历史结果：

`GET /api/agents/documents/{document_id}/facility-units`

## 代码结构

```text
app/
├─ agents/
│  ├─ scada_facility_agent.py
│  └─ scada_facility_unit_agent.py
├─ ai/
│  ├─ prompts.py
│  ├─ provider.py
│  └─ schemas.py
├─ domain/
│  ├─ facility_catalog.py
│  └─ facility_unit_rules.py
├─ services/
│  ├─ image_media.py
│  └─ scada_analysis_service.py
├─ models/
│  └─ entities.py
├─ api/routes/
│  ├─ master_data.py
│  ├─ documents.py
│  └─ agents.py
└─ main.py
```

## Prompt 在哪里

两个正式 Prompt 都在：

`app/ai/prompts.py`

- `FACILITY_AGENT_BASE_PROMPT`
- `FACILITY_UNIT_AGENT_BASE_PROMPT`

标准设施数据不再全部硬编码进 Prompt，而是放在：

`app/domain/facility_catalog.py`

运行 Agent 1 时动态注入 Prompt。

Agent 2 的专属规则放在：

`app/domain/facility_unit_rules.py`

这样以后修改标准设施和单元规则，不需要不断重写大段 Prompt。

## 当前版本明确删除/停止的内容

- 设计PDF结构发现
- DWG解析
- 图签识别
- ProcessSystem识别
- 设计图与SCADA对照
- 旧版Mock Provider
- 旧版单阶段StructureDiscoveryAgent
- PDF渲染依赖 PyMuPDF

这些以后如果业务需要，可以作为独立模块重新接入，不影响当前正式SCADA识别链。
