from fastapi import APIRouter
from app.api.routes import (
    organizations,
    project_types,
    projects,
    plants,
    process_systems,
    facilities,
    facility_units,
    documents,
    document_links,
    structure,
    ai,
)

api_router = APIRouter()
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(project_types.router, prefix="/project-types", tags=["project-types"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(plants.router, prefix="/plants", tags=["plants"])
api_router.include_router(process_systems.router, prefix="/process-systems", tags=["process-systems"])
api_router.include_router(facilities.router, prefix="/facilities", tags=["facilities"])
api_router.include_router(facility_units.router, prefix="/facility-units", tags=["facility-units"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(document_links.router, prefix="/document-links", tags=["document-links"])
api_router.include_router(structure.router, prefix="/structure", tags=["structure"])

api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
