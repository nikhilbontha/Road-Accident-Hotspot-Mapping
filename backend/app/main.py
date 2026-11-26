from contextlib import asynccontextmanager
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from datetime import datetime, timezone

from app.core.config import settings
from app.core.db import engine, Base
import app.models  # load models
from app.api.v1.api import api_router

try:
    from prometheus_fastapi_instrumentator import Instrumentator
    has_prometheus = True
except ImportError:
    has_prometheus = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize all database tables
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Geospatial decision-support platform for Road Accident Hotspot Mapping (Team 12, Anurag University, BRD-RAH-001).",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Also expose /api/v1/docs redirecting to /docs
@app.get(f"{settings.API_V1_PREFIX}/docs", include_in_schema=False)
async def api_docs_redirect():
    return RedirectResponse(url="/docs")

# Root health check endpoint
@app.get("/health", tags=["Health"])
async def root_health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }

# Set CORS middleware
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Prometheus instrumentator or fallback metrics endpoint
if has_prometheus:
    Instrumentator().instrument(app).expose(app, endpoint=f"{settings.API_V1_PREFIX}/metrics")
else:
    @app.get(f"{settings.API_V1_PREFIX}/metrics", tags=["Monitoring"])
    async def fallback_metrics():
        return Response(
            content="# HELP http_requests_total Total HTTP requests\n# TYPE http_requests_total counter\nhttp_requests_total 1\n",
            media_type="text/plain",
        )


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "docs": f"{settings.API_V1_PREFIX}/docs",
        "health": f"{settings.API_V1_PREFIX}/health",
    }
