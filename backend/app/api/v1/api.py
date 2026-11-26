from fastapi import APIRouter
from app.api.v1.endpoints import (
    health,
    auth,
    users,
    imports,
    analysis,
    map,
    hotspots,
    dashboard,
    notifications,
    reports,
    assistant,
    accidents
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(accidents.router)
api_router.include_router(imports.router)
api_router.include_router(analysis.router)
api_router.include_router(map.router)
api_router.include_router(hotspots.router)
api_router.include_router(dashboard.router)
api_router.include_router(notifications.router)
api_router.include_router(reports.router)
api_router.include_router(assistant.router)
