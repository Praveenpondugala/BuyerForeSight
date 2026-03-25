# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from app.core.config import settings
from app.core.logging import logger
from app.db.database import init_db, close_db
from app.api.v1.router import api_router
from app.middleware.exception_handlers import register_exception_handlers
from app.middleware.request_logger import RequestLoggerMiddleware
from app.utils.seeder import seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    await init_db()
    await seed()
    logger.info("Database ready")
    yield
    await close_db()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION + """

## Overview
**User Management REST API** built with **FastAPI** and **SQLite**.

## Features
- Full CRUD operations for users
- Search by name, email, or department
- Sort by any field (asc/desc)
- Pagination support
- Role-based filtering
- Input validation with detailed error messages
- Consistent JSON response envelope
- Request logging with response times
- CORS enabled

## Response Format
All responses follow a consistent envelope:
```json
{
  "success": true,
  "message": "...",
  "data": { ... },
  "timestamp": "2024-01-01T00:00:00"
}
```
        """,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )
    app.add_middleware(RequestLoggerMiddleware)

    # Exception Handlers
    register_exception_handlers(app)

    # Routes
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    # Health & Root 
    @app.get("/", include_in_schema=False)
    async def root():
        return JSONResponse({
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "running",
            "docs": "/docs",
            "health": "/health",
            "api": settings.API_V1_PREFIX,
        })

    @app.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "healthy",
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    return app


app = create_app()
