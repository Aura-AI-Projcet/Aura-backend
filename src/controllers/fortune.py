"""
Fortune Controller

Handles HTTP requests for fortune and divination features.
"""


from fastapi import APIRouter, Depends, HTTPException, status

from ..middleware.auth import get_current_user_id
from ..services.fortune import fortune_service
from ..types.database import (
    DailyFortune,
    DailyFortuneResponse,
    FortuneRequest,
    FortuneResponse,
)

router = APIRouter(prefix="/fortune", tags=["fortune"])


@router.get("/daily", response_model=DailyFortuneResponse)
async def get_daily_fortune(
    date: str | None = None, user_id: str = Depends(get_current_user_id)
) -> DailyFortuneResponse:
    """Get daily fortune for user"""
    try:
        response = await fortune_service.get_daily_fortune(user_id, date)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get daily fortune: {str(e)}",
        )


@router.post("/predict", response_model=FortuneResponse)
async def predict_fortune(
    request: FortuneRequest, user_id: str = Depends(get_current_user_id)
) -> FortuneResponse:
    """Predict fortune (tarot, divination, etc.)"""
    try:
        # Validate request type
        valid_types = ["daily_fortune", "tarot", "divination"]
        if request.request_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid request type. Must be one of: {', '.join(valid_types)}",
            )

        # Validate required fields based on request type
        if request.request_type == "tarot" and not request.question:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question is required for tarot reading",
            )

        if request.request_type == "divination" and not request.divination_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Divination type is required for divination",
            )

        response = await fortune_service.predict_fortune(user_id, request)
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to predict fortune: {str(e)}",
        )


@router.get("/history", response_model=list[DailyFortune])
async def get_fortune_history(
    limit: int = 30, user_id: str = Depends(get_current_user_id)
) -> list[DailyFortune] | None:
    """Get user's fortune history"""
    try:
        if limit > 100:
            limit = 100  # Cap the limit

        fortunes = await fortune_service.get_fortune_history(user_id, limit)
        return fortunes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get fortune history: {str(e)}",
        )


@router.post("/daily/generate", response_model=DailyFortuneResponse)
async def generate_daily_fortune(
    date: str | None = None, user_id: str = Depends(get_current_user_id)
) -> DailyFortuneResponse:
    """Force generate a new daily fortune (for testing or premium users)"""
    try:
        # For now, this just calls the regular daily fortune endpoint
        # In production, you might want to add rate limiting or premium checks
        response = await fortune_service.get_daily_fortune(user_id, date)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate daily fortune: {str(e)}",
        )
