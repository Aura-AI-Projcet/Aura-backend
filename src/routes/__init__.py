"""
Main API Router

Combines all route modules into a single router.
"""
from fastapi import APIRouter

from ..controllers.chat import router as chat_router
from ..controllers.compatibility import router as compatibility_router
from ..controllers.fortune import router as fortune_router
from ..controllers.onboarding import router as onboarding_router

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(onboarding_router)
api_router.include_router(chat_router)
api_router.include_router(fortune_router)
api_router.include_router(compatibility_router)


# Health check for API
@api_router.get("/health")
async def api_health_check() -> dict[str, str]:
    """API-level health check"""
    return {"status": "healthy", "message": "API is running"}
