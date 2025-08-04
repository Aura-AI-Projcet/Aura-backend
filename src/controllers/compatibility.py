"""
Compatibility Controller

Handles HTTP requests for compatibility analysis functionality.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from ..middleware.auth import get_current_user_id
from ..services.compatibility import compatibility_service
from ..types.database import (
    CompatibilityRequest,
    CompatibilityResponse,
    CreateOtherProfileRequest,
    OtherProfileResponse,
)

router = APIRouter(prefix="/compatibility", tags=["compatibility"])


@router.post("/other-profiles", response_model=OtherProfileResponse)
async def create_other_profile(
    request: CreateOtherProfileRequest, user_id: str = Depends(get_current_user_id)
) -> OtherProfileResponse:
    """Create other person profile for compatibility analysis"""
    try:
        other_profile = await compatibility_service.create_other_profile(
            user_id, request
        )
        return other_profile
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create other profile: {str(e)}",
        )


@router.get("/other-profiles", response_model=list[OtherProfileResponse])
async def get_other_profiles(
    user_id: str = Depends(get_current_user_id)
) -> list[OtherProfileResponse]:
    """Get all other profiles for the authenticated user"""
    try:
        profiles = await compatibility_service.get_other_profiles(user_id)
        return profiles
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get other profiles: {str(e)}",
        )


@router.get("/other-profiles/{profile_id}", response_model=OtherProfileResponse)
async def get_other_profile(
    profile_id: str, user_id: str = Depends(get_current_user_id)
) -> OtherProfileResponse:
    """Get specific other profile by ID"""
    try:
        profile = await compatibility_service.get_other_profile(user_id, profile_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
            )
        return profile
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get other profile: {str(e)}",
        )


@router.post("/analyze", response_model=CompatibilityResponse)
async def analyze_compatibility(
    request: CompatibilityRequest, user_id: str = Depends(get_current_user_id)
) -> CompatibilityResponse:
    """Perform compatibility analysis between user and other person"""
    try:
        analysis = await compatibility_service.analyze_compatibility(user_id, request)
        return analysis
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze compatibility: {str(e)}",
        )


@router.get("/history", response_model=list[CompatibilityResponse])
async def get_compatibility_history(
    limit: int = 10, offset: int = 0, user_id: str = Depends(get_current_user_id)
) -> list[CompatibilityResponse]:
    """Get compatibility analysis history for the authenticated user"""
    try:
        history = await compatibility_service.get_compatibility_history(
            user_id, limit, offset
        )
        return history
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get compatibility history: {str(e)}",
        )


@router.delete("/other-profiles/{profile_id}")
async def delete_other_profile(
    profile_id: str, user_id: str = Depends(get_current_user_id)
) -> dict[str, str]:
    """Delete other person profile"""
    try:
        success = await compatibility_service.delete_other_profile(user_id, profile_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
            )
        return {"message": "Profile deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete other profile: {str(e)}",
        )
