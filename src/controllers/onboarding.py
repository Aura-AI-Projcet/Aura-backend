"""
Onboarding Controller

Handles HTTP requests for user onboarding flow.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status

from ..middleware.auth import get_current_user_id
from ..services.onboarding import onboarding_service
from ..types.database import (
    Avatar,
    CreateProfileRequest,
    OnboardingStatusResponse,
    ProfileResponse,
    UpdateProfileRequest,
    UserProfileAnalysis,
)

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.get("/status", response_model=OnboardingStatusResponse)
async def get_onboarding_status(
    request: Request,
    user_id: str = Depends(get_current_user_id)
) -> OnboardingStatusResponse:
    """Get current onboarding status for the authenticated user"""
    try:
        status_response = await onboarding_service.get_onboarding_status(user_id)
        return status_response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get onboarding status: {str(e)}"
        )


@router.get("/avatars", response_model=list[Avatar])
async def get_avatars() -> list[Avatar]:
    """Get all available avatars (public endpoint)"""
    try:
        avatars = await onboarding_service.get_avatars()
        return avatars
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get avatars: {str(e)}"
        )


@router.get("/profile", response_model=ProfileResponse)
async def get_user_profile(
    request: Request,
    user_id: str = Depends(get_current_user_id)
) -> ProfileResponse:
    """Get user profile"""
    try:
        profile = await onboarding_service.get_user_profile(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        return profile
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profile: {str(e)}"
        )


@router.post("/profile", response_model=ProfileResponse)
async def create_or_update_profile(
    profile_data: CreateProfileRequest,
    request: Request,
    user_id: str = Depends(get_current_user_id)
) -> ProfileResponse:
    """Create or update user profile"""
    try:
        # Validate avatar exists
        avatars = await onboarding_service.get_avatars()
        avatar_ids = [avatar.id for avatar in avatars]
        if profile_data.selected_avatar_id not in avatar_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid avatar ID"
            )

        profile = await onboarding_service.create_or_update_profile(user_id, profile_data)
        return profile
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create/update profile: {str(e)}"
        )


@router.patch("/profile", response_model=ProfileResponse)
async def update_profile(
    update_data: UpdateProfileRequest,
    request: Request,
    user_id: str = Depends(get_current_user_id)
) -> ProfileResponse:
    """Update user profile"""
    try:
        # Validate avatar if provided
        if update_data.selected_avatar_id:
            avatars = await onboarding_service.get_avatars()
            avatar_ids = [avatar.id for avatar in avatars]
            if update_data.selected_avatar_id not in avatar_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid avatar ID"
                )

        profile = await onboarding_service.update_profile(user_id, update_data)
        return profile
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.get("/profile/analysis")
async def get_user_analysis(
    request: Request,
    user_id: str = Depends(get_current_user_id)
) -> UserProfileAnalysis:
    """Get user profile analysis result"""
    try:
        analysis = await onboarding_service.get_user_analysis(user_id)
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analysis: {str(e)}"
        )
