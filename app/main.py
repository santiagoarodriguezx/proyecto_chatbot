"""
Main FastAPI Application
"""
from scalar_fastapi import get_scalar_api_reference
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
from app.api.v1.routers import api_router
from app.api.v1.routers.webhooks import router as webhooks_router
from app.config.config import settings
import logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info(f"🚀 {settings.app_name} v{settings.version} iniciando...")
    logger.info(f"📅 Fecha: {datetime.now().isoformat()}")

    # Verificar conexión a Supabase
    try:
        from app.services.database import _client
        result = _client.table("prompts").select(
            "count", count="exact").limit(1).execute()
        logger.info("✅ Conexión a Supabase exitosa")
    except Exception as e:
        logger.warning(f"⚠️ Error conectando a Supabase: {e}")

    yield

    # Shutdown
    logger.info(f"👋 {settings.app_name} finalizando...")


# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Include webhooks router SIN prefijo (Evolution espera rutas exactas)
app.include_router(webhooks_router, tags=["Evolution Webhooks"])

# Include API routers con prefijo
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "app": settings.app_name,
        "version": settings.version,
        "status": "online",
        "docs": "/docs",
        "webhook_endpoints": [
            "/messages-upsert",
            "/chats-update",
            "/messages-update",
            "/send-message"
        ]
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.version,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
