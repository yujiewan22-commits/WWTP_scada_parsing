from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
import app.models  # noqa: F401


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="正式版：基于SCADA截图的设施识别Agent + 构筑物单元识别Agent",
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(api_router)
