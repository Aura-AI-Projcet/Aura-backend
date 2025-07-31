"""
Onboarding Service

Handles user onboarding flow including profile creation, avatar selection,
and integration with algorithm service for user profile analysis.
"""
import asyncio
from typing import Any

import httpx

from ..config.env import settings
from ..config.supabase import admin_client, supabase_client
from ..types.database import (
    Avatar,
    BirthInfo,
    CreateProfileRequest,
    OnboardingStatusResponse,
    OnboardingStep,
    ProfileResponse,
    UpdateProfileRequest,
    UserProfileAnalysis,
)


class OnboardingService:
    """Service for handling user onboarding"""

    def __init__(self) -> None:
        self.supabase = supabase_client
        self.admin_supabase = admin_client

    async def get_onboarding_status(self, user_id: str) -> OnboardingStatusResponse:
        """Get current onboarding status for user"""

        # Get user profile
        profile = await self.get_user_profile(user_id)

        # Get available avatars
        avatars = await self.get_avatars()

        # Determine current step and completed steps
        completed_steps = []
        current_step = OnboardingStep.BASIC_INFO

        if profile:
            if profile.nickname and profile.gender:
                completed_steps.append(OnboardingStep.BASIC_INFO)
                current_step = OnboardingStep.BIRTH_INFO

            if profile.birth_year and profile.birth_month and profile.birth_day:
                completed_steps.append(OnboardingStep.BIRTH_INFO)
                current_step = OnboardingStep.AVATAR_SELECTION

            if profile.selected_avatar:
                completed_steps.append(OnboardingStep.AVATAR_SELECTION)
                current_step = OnboardingStep.ANALYSIS_PROCESSING

                # Check if analysis is completed
                analysis = await self.get_user_analysis(user_id)
                if analysis:
                    completed_steps.append(OnboardingStep.ANALYSIS_PROCESSING)
                    current_step = OnboardingStep.FIRST_CHAT

                    # For now, assume first chat is always the final step
                    completed_steps.append(OnboardingStep.FIRST_CHAT)
                    current_step = OnboardingStep.COMPLETED

        return OnboardingStatusResponse(
            current_step=current_step,
            completed_steps=completed_steps,
            profile=profile,
            available_avatars=avatars
        )

    async def get_avatars(self) -> list[Avatar]:
        """Get all available avatars"""
        response = self.supabase.table('avatars').select('*').execute()

        avatars = []
        for avatar_data in response.data:
            # Parse abilities JSON
            abilities = avatar_data.get('abilities', [])
            if isinstance(abilities, str):
                import json
                abilities = json.loads(abilities)

            avatar = Avatar(
                id=avatar_data['id'],
                name=avatar_data['name'],
                description=avatar_data.get('description'),
                image_url=avatar_data.get('image_url'),
                abilities=abilities,
                initial_dialogue_prompt=avatar_data.get('initial_dialogue_prompt'),
                created_at=avatar_data['created_at'],
                updated_at=avatar_data['updated_at']
            )
            avatars.append(avatar)

        return avatars

    async def get_user_profile(self, user_id: str) -> ProfileResponse | None:
        """Get user profile with avatar information"""
        response = self.supabase.table('profiles').select(
            '*, selected_avatar:avatars(*)'
        ).eq('id', user_id).execute()

        if not response.data:
            return None

        profile_data = response.data[0]

        # Parse selected avatar
        selected_avatar = None
        if profile_data.get('selected_avatar'):
            avatar_data = profile_data['selected_avatar']
            abilities = avatar_data.get('abilities', [])
            if isinstance(abilities, str):
                import json
                abilities = json.loads(abilities)

            selected_avatar = Avatar(
                id=avatar_data['id'],
                name=avatar_data['name'],
                description=avatar_data.get('description'),
                image_url=avatar_data.get('image_url'),
                abilities=abilities,
                initial_dialogue_prompt=avatar_data.get('initial_dialogue_prompt'),
                created_at=avatar_data['created_at'],
                updated_at=avatar_data['updated_at']
            )

        # Check if analysis is completed
        analysis = await self.get_user_analysis(user_id)
        analysis_completed = analysis is not None

        return ProfileResponse(
            id=profile_data['id'],
            nickname=profile_data.get('nickname'),
            gender=profile_data.get('gender'),
            birth_year=profile_data.get('birth_year'),
            birth_month=profile_data.get('birth_month'),
            birth_day=profile_data.get('birth_day'),
            birth_hour=profile_data.get('birth_hour'),
            birth_minute=profile_data.get('birth_minute'),
            birth_second=profile_data.get('birth_second'),
            birth_location=profile_data.get('birth_location'),
            birth_longitude=profile_data.get('birth_longitude'),
            birth_latitude=profile_data.get('birth_latitude'),
            selected_avatar=selected_avatar,
            analysis_completed=analysis_completed,
            created_at=profile_data['created_at'],
            updated_at=profile_data['updated_at']
        )

    async def create_or_update_profile(
        self,
        user_id: str,
        profile_data: CreateProfileRequest
    ) -> ProfileResponse:
        """Create or update user profile"""

        # Prepare profile data
        profile_dict = {
            'id': user_id,
            'nickname': profile_data.nickname,
            'gender': profile_data.gender.value,
            'birth_year': profile_data.birth_info.year,
            'birth_month': profile_data.birth_info.month,
            'birth_day': profile_data.birth_info.day,
            'birth_hour': profile_data.birth_info.hour,
            'birth_minute': profile_data.birth_info.minute,
            'birth_second': profile_data.birth_info.second,
            'birth_location': profile_data.birth_info.location,
            'birth_longitude': profile_data.birth_info.longitude,
            'birth_latitude': profile_data.birth_info.latitude,
            'selected_avatar_id': str(profile_data.selected_avatar_id)
        }

        # Use upsert to create or update
        response = self.supabase.table('profiles').upsert(profile_dict).execute()

        if not response.data:
            raise Exception("Failed to create/update profile")

        # Trigger user profile analysis
        asyncio.create_task(self._trigger_profile_analysis(user_id, profile_data.birth_info))

        # Return updated profile
        profile = await self.get_user_profile(user_id)
        if profile is None:
            raise Exception("Failed to retrieve created profile")
        return profile

    async def update_profile(
        self,
        user_id: str,
        update_data: UpdateProfileRequest
    ) -> ProfileResponse:
        """Update existing user profile"""

        # Prepare update data
        update_dict: dict[str, Any] = {}

        if update_data.nickname is not None:
            update_dict['nickname'] = update_data.nickname

        if update_data.gender is not None:
            update_dict['gender'] = update_data.gender.value

        if update_data.birth_info is not None:
            update_dict.update({
                'birth_year': update_data.birth_info.year,
                'birth_month': update_data.birth_info.month,
                'birth_day': update_data.birth_info.day,
                'birth_hour': update_data.birth_info.hour,
                'birth_minute': update_data.birth_info.minute,
                'birth_second': update_data.birth_info.second,
                'birth_location': update_data.birth_info.location,
                'birth_longitude': update_data.birth_info.longitude,
                'birth_latitude': update_data.birth_info.latitude,
            })

            # Trigger re-analysis if birth info changed
            asyncio.create_task(self._trigger_profile_analysis(user_id, update_data.birth_info))

        if update_data.selected_avatar_id is not None:
            update_dict['selected_avatar_id'] = str(update_data.selected_avatar_id)

        # Update profile
        response = self.supabase.table('profiles').update(update_dict).eq('id', user_id).execute()

        if not response.data:
            raise Exception("Failed to update profile")

        # Return updated profile
        profile = await self.get_user_profile(user_id)
        if profile is None:
            raise Exception("Failed to retrieve updated profile")
        return profile

    async def get_user_analysis(self, user_id: str) -> UserProfileAnalysis | None:
        """Get user profile analysis result"""
        response = self.supabase.table('user_profiles_analysis').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(1).execute()

        if not response.data:
            return None

        analysis_data = response.data[0]
        return UserProfileAnalysis(
            id=analysis_data['id'],
            user_id=analysis_data['user_id'],
            analysis_data=analysis_data['analysis_data'],
            created_at=analysis_data['created_at'],
            updated_at=analysis_data['updated_at']
        )

    async def _trigger_profile_analysis(self, user_id: str, birth_info: BirthInfo) -> None:
        """Trigger user profile analysis with algorithm service"""
        try:
            # Prepare request data for algorithm service
            birth_info_dict: dict[str, Any] = {
                "year": birth_info.year,
                "month": birth_info.month,
                "day": birth_info.day,
                "location": birth_info.location,
            }

            # Add optional fields only if they're not None
            if birth_info.hour is not None:
                birth_info_dict["hour"] = birth_info.hour
            if birth_info.minute is not None:
                birth_info_dict["minute"] = birth_info.minute
            if birth_info.second is not None:
                birth_info_dict["second"] = birth_info.second
            if birth_info.longitude is not None:
                birth_info_dict["longitude"] = birth_info.longitude
            if birth_info.latitude is not None:
                birth_info_dict["latitude"] = birth_info.latitude

            algorithm_request = {
                "user_id": user_id,
                "birth_info": birth_info_dict
            }

            # Call algorithm service
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.ALGORITHM_SERVICE_URL}/api/algorithm/user-profile-analysis",
                    json=algorithm_request,
                    timeout=60.0
                )

                if response.status_code == 200:
                    analysis_result = response.json()

                    # Store analysis result in database
                    await self._store_analysis_result(user_id, analysis_result.get('analysis_results', {}))

                else:
                    print(f"Algorithm service error: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"Error calling algorithm service: {str(e)}")
            # Don't raise exception as this should not block user onboarding

    async def _store_analysis_result(self, user_id: str, analysis_data: dict[str, Any]) -> None:
        """Store user profile analysis result"""
        analysis_record = {
            'user_id': user_id,
            'analysis_data': analysis_data
        }

        response = self.supabase.table('user_profiles_analysis').insert(analysis_record).execute()

        if not response.data:
            raise Exception("Failed to store analysis result")


# Global service instance
onboarding_service = OnboardingService()
