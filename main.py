"""
Aura Backend - FastAPI Application
"""
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from src.config.env import settings
from src.config.supabase import supabase_client
from src.middleware.auth import AuthMiddleware
from src.middleware.error_handler import ErrorHandlerMiddleware
from src.routes import api_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager"""
    # Startup
    print("🚀 Starting Aura Backend Server...")
    print(f"🌐 Environment: {settings.ENVIRONMENT}")
    print(f"📊 Supabase URL: {settings.SUPABASE_URL}")

    # Test Supabase connection
    try:
        # Simple health check for Supabase
        supabase_client.table('profiles').select('count').limit(1).execute()
        print("✅ Supabase connection successful")
    except Exception as e:
        print(f"⚠️  Supabase connection warning: {e}")

    yield

    # Shutdown
    print("🔻 Shutting down Aura Backend Server...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""

    app = FastAPI(
        title="Aura Backend API",
        description="Backend API for Aura astrology and fortune telling app",
        version="1.0.0",
        docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
        lifespan=lifespan
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Security Middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"] if settings.ENVIRONMENT == "development" else ["localhost", "127.0.0.1"]
    )

    # Custom Middleware
    app.add_middleware(AuthMiddleware)
    app.add_middleware(ErrorHandlerMiddleware)

    # Routes
    app.include_router(api_router, prefix="/api/v1")

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        """Health check endpoint"""
        return {
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
            "version": "1.0.0"
        }

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level="info"
    )
