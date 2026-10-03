from fastapi import FastAPI
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.api.router import api_router

app = FastAPI(
    title=settings.app_name,
    version="0.3.0",
    description="水厂基础信息 AI 治理平台 V2",
)

Base.metadata.create_all(bind=engine)
app.include_router(api_router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.3.0"}
