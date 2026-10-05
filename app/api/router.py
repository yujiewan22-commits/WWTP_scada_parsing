from fastapi import APIRouter

from app.api.routes import agents, documents, master_data

api_router = APIRouter(prefix="/api")
api_router.include_router(master_data.router)
api_router.include_router(documents.router)
api_router.include_router(agents.router)
