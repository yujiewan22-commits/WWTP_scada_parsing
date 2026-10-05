from pathlib import Path

import shutil
import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db

from app.models import (
    Plant,
    ScadaDocument,
)

from app.schemas.entities import (
    ScadaDocumentOut,
)

from app.services.image_media import (
    SUPPORTED_EXTS,
)


router = APIRouter(
    tags=["SCADA Documents"]
)


# ============================================================
# 上传 SCADA 截图
# ============================================================

@router.post(
    "/documents/upload",
    response_model=ScadaDocumentOut,
)
def upload_scada(
    plant_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    plant = db.get(
        Plant,
        plant_id,
    )

    if not plant:
        raise HTTPException(
            status_code=400,
            detail="plant_id 不存在",
        )

    suffix = Path(
        file.filename or ""
    ).suffix.lower()

    if suffix not in SUPPORTED_EXTS:
        raise HTTPException(
            status_code=400,
            detail=(
                "正式版只支持 SCADA 截图图片："
                "PNG/JPG/JPEG/WEBP/BMP，"
                "不处理 PDF/DWG"
            ),
        )

    upload_dir = Path(
        settings.upload_dir
    )

    upload_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    stored_name = (
        f"{uuid.uuid4().hex}{suffix}"
    )

    storage_path = (
        upload_dir / stored_name
    )

    with storage_path.open("wb") as f:
        shutil.copyfileobj(
            file.file,
            f,
        )

    document = ScadaDocument(
        plant_id=plant_id,
        original_filename=(
            file.filename
            or stored_name
        ),
        storage_path=str(
            storage_path
        ),
        content_type=file.content_type,
        file_size=storage_path.stat().st_size,
        ai_status="UNANALYZED",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


# ============================================================
# 查询所有 SCADA 文档
# ============================================================

@router.get(
    "/documents",
    response_model=list[ScadaDocumentOut],
)
def list_documents(
    db: Session = Depends(get_db),
):
    return list(
        db.scalars(
            select(ScadaDocument)
            .order_by(
                ScadaDocument.id.desc()
            )
        )
    )


# ============================================================
# 查询单个 SCADA 文档
# ============================================================

@router.get(
    "/documents/{document_id}",
    response_model=ScadaDocumentOut,
)
def get_document(
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

    return document