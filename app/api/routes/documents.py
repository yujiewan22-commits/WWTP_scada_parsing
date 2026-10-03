from pathlib import Path
from uuid import uuid4
import shutil

from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.config import settings
from app.db.deps import get_db
from app.models.document import Document
from app.schemas.entities import DocumentOut

router = APIRouter()

@router.post("/upload", response_model=DocumentOut)
def upload_document(
    project_id: int = Form(...),
    plant_id: int = Form(...),
    document_type: str | None = Form(None),
    title: str | None = Form(None),
    drawing_no: str | None = Form(None),
    revision: str | None = Form(None),
    year: int | None = Form(None),
    discipline: str | None = Form(None),
    notes: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    suffix = Path(file.filename or "").suffix
    stored_filename = f"{uuid4().hex}{suffix}"
    target = upload_dir / stored_filename

    try:
        with target.open("wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件保存失败: {e}")

    obj = Document(
        project_id=project_id,
        plant_id=plant_id,
        original_filename=file.filename or stored_filename,
        stored_filename=stored_filename,
        storage_path=str(target),
        document_type=document_type,
        title=title,
        drawing_no=drawing_no,
        revision=revision,
        year=year,
        discipline=discipline,
        notes=notes,
        ai_status="UNANALYZED",
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("", response_model=list[DocumentOut])
def list_documents(
    plant_id: int | None = None,
    project_id: int | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(Document)
    if plant_id is not None:
        stmt = stmt.where(Document.plant_id == plant_id)
    if project_id is not None:
        stmt = stmt.where(Document.project_id == project_id)
    return db.scalars(stmt.order_by(Document.id.desc())).all()
