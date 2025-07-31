"""
Main API Router

Combines all route modules into a single router.
"""
from fastapi import APIRouter

from ..controllers.onboarding import router as onboarding_router

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(onboarding_router)

# Health check for API
@api_router.get("/health")
async def api_health_check() -> dict[str, str]:
    """API-level health check"""
    return {"status": "healthy", "message": "API is running"}
