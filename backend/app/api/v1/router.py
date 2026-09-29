from fastapi import APIRouter
from app.api.v1.endpoints import (
    health,
    auth,
    company,
    team,
    clients,
    projects,
    services,
    audit,
    documents,
    templates,
    ai,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(company.router, prefix="/company", tags=["Company Management"])
api_router.include_router(team.router, prefix="/team", tags=["Team Management"])
api_router.include_router(clients.router, prefix="/clients", tags=["Clients Directory"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects Portfolio"])
api_router.include_router(services.router, prefix="/services", tags=["Services Catalog"])
api_router.include_router(documents.router, prefix="/documents", tags=["Document Vault"])
api_router.include_router(templates.router, prefix="/templates", tags=["Template Engine"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI Core & Company Memory"])
api_router.include_router(audit.router, prefix="/audit", tags=["Audit & Governance"])
