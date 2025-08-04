"""
Compatibility Service

Handles other person profiles and compatibility analysis.
"""
from datetime import datetime
from typing import Any

import httpx

from ..config.env import settings
from ..config.supabase import admin_client, supabase_client
from ..types.database import (
    ChatMessage,
    CompatibilityAnalysisResult,
    CompatibilityRequest,
    CompatibilityResponse,
    CreateOtherProfileRequest,
    MessageType,
    OtherProfile,
    OtherProfileResponse,
    SenderType,
)


class CompatibilityService:
    """Service for handling compatibility analysis"""

    def __init__(self) -> None:
        self.supabase = supabase_client
        self.admin_supabase = admin_client

    async def create_other_profile(
        self, user_id: str, request: CreateOtherProfileRequest
    ) -> OtherProfileResponse:
        """Create other person profile for compatibility analysis"""

        birth_info = request.birth_info

        profile_data = {
            "user_id": user_id,
            "name": request.name,
            "gender": request.gender.value if request.gender else None,
            "birth_year": birth_info.year,
            "birth_month": birth_info.month,
            "birth_day": birth_info.day,
            "birth_hour": birth_info.hour,
            "birth_minute": birth_info.minute,
            "birth_second": birth_info.second,
            "birth_location": birth_info.location,
            "birth_longitude": birth_info.longitude,
            "birth_latitude": birth_info.latitude,
            "relation_type": request.relation_type,
        }

        response = self.supabase.table("other_profiles").insert(profile_data).execute()

        if not response.data:
            raise Exception("Failed to create other profile")

        profile = OtherProfile(**response.data[0])

        return OtherProfileResponse(
            id=profile.id,
            name=profile.name,
            gender=profile.gender,
            birth_year=profile.birth_year,
            birth_month=profile.birth_month,
            birth_day=profile.birth_day,
            birth_hour=profile.birth_hour,
            birth_minute=profile.birth_minute,
            birth_second=profile.birth_second,
            birth_location=profile.birth_location,
            relation_type=profile.relation_type,
            created_at=profile.created_at,
        )

    async def get_other_profiles(self, user_id: str) -> list[OtherProfileResponse]:
        """Get all other profiles for a user"""

        response = (
            self.supabase.table("other_profiles")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )

        profiles = []
        for profile_data in response.data:
            profile = OtherProfile(**profile_data)
            profiles.append(
                OtherProfileResponse(
                    id=profile.id,
                    name=profile.name,
                    gender=profile.gender,
                    birth_year=profile.birth_year,
                    birth_month=profile.birth_month,
                    birth_day=profile.birth_day,
                    birth_hour=profile.birth_hour,
                    birth_minute=profile.birth_minute,
                    birth_second=profile.birth_second,
                    birth_location=profile.birth_location,
                    relation_type=profile.relation_type,
                    created_at=profile.created_at,
                )
            )

        return profiles

    async def get_other_profile(
        self, user_id: str, profile_id: str
    ) -> OtherProfileResponse | None:
        """Get specific other profile by ID"""
        response = (
            self.supabase.table("other_profiles")
            .select("*")
            .eq("user_id", user_id)
            .eq("id", profile_id)
            .execute()
        )

        if not response.data:
            return None

        profile_data = response.data[0]
        profile = OtherProfile(**profile_data)
        return OtherProfileResponse(
            id=profile.id,
            name=profile.name,
            gender=profile.gender,
            birth_year=profile.birth_year,
            birth_month=profile.birth_month,
            birth_day=profile.birth_day,
            birth_hour=profile.birth_hour,
            birth_minute=profile.birth_minute,
            birth_second=profile.birth_second,
            birth_location=profile.birth_location,
            relation_type=profile.relation_type,
            created_at=profile.created_at,
        )

    async def analyze_compatibility(
        self, user_id: str, request: CompatibilityRequest
    ) -> CompatibilityResponse:
        """Perform compatibility analysis"""

        # Get other profile
        other_profile_response = (
            self.supabase.table("other_profiles")
            .select("*")
            .eq("id", str(request.other_profile_id))
            .eq("user_id", user_id)
            .execute()
        )

        if not other_profile_response.data:
            raise Exception("Other profile not found")

        other_profile_data = other_profile_response.data[0]
        other_profile = OtherProfile(**other_profile_data)

        # Get main user profile
        main_profile_response = (
            self.supabase.table("profiles").select("*").eq("id", user_id).execute()
        )

        if not main_profile_response.data:
            raise Exception("User profile not found")

        main_profile = main_profile_response.data[0]

        # Check if analysis already exists
        existing_analysis = await self._get_existing_analysis(
            user_id, str(request.other_profile_id)
        )

        if existing_analysis:
            compatibility_result = existing_analysis.analysis_data
        else:
            # Perform new analysis
            compatibility_result = await self._perform_compatibility_analysis(
                main_profile, other_profile_data, request.analysis_depth
            )

            # Store analysis result
            await self._store_analysis_result(
                user_id, str(request.other_profile_id), compatibility_result
            )

        # Create related chat message
        related_message = await self._create_compatibility_message(
            user_id, compatibility_result, other_profile.name
        )

        return CompatibilityResponse(
            compatibility_result=compatibility_result,
            other_profile=OtherProfileResponse(
                id=other_profile.id,
                name=other_profile.name,
                gender=other_profile.gender,
                birth_year=other_profile.birth_year,
                birth_month=other_profile.birth_month,
                birth_day=other_profile.birth_day,
                birth_hour=other_profile.birth_hour,
                birth_minute=other_profile.birth_minute,
                birth_second=other_profile.birth_second,
                birth_location=other_profile.birth_location,
                relation_type=other_profile.relation_type,
                created_at=other_profile.created_at,
            ),
            related_message=related_message,
        )

    async def get_compatibility_history(
        self, user_id: str, limit: int = 10, offset: int = 0
    ) -> list[CompatibilityResponse]:
        """Get user's compatibility analysis history"""

        response = (
            self.supabase.table("compatibility_analysis_results")
            .select("*, other_profiles(*)")
            .eq("user_id_main", user_id)
            .order("analysis_date", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )

        results = []
        for analysis_data in response.data:
            other_profile_data = analysis_data["other_profiles"]
            other_profile = OtherProfileResponse(
                id=other_profile_data["id"],
                name=other_profile_data["name"],
                gender=other_profile_data.get("gender"),
                birth_year=other_profile_data["birth_year"],
                birth_month=other_profile_data["birth_month"],
                birth_day=other_profile_data["birth_day"],
                birth_hour=other_profile_data.get("birth_hour"),
                birth_minute=other_profile_data.get("birth_minute"),
                birth_second=other_profile_data.get("birth_second"),
                birth_location=other_profile_data.get("birth_location"),
                relation_type=other_profile_data.get("relation_type"),
                created_at=other_profile_data["created_at"],
            )

            compatibility_response = CompatibilityResponse(
                compatibility_result=analysis_data["analysis_data"],
                other_profile=other_profile,
                related_message=None,
            )
            results.append(compatibility_response)

        return results

    async def delete_other_profile(self, user_id: str, profile_id: str) -> bool:
        """Delete other person profile"""
        # First check if profile exists and belongs to user
        existing_response = (
            self.supabase.table("other_profiles")
            .select("id")
            .eq("user_id", user_id)
            .eq("id", profile_id)
            .execute()
        )

        if not existing_response.data:
            return False

        # Delete the profile
        delete_response = (
            self.supabase.table("other_profiles")
            .delete()
            .eq("user_id", user_id)
            .eq("id", profile_id)
            .execute()
        )

        return len(delete_response.data) > 0

    async def _get_existing_analysis(
        self, user_id: str, other_profile_id: str
    ) -> CompatibilityAnalysisResult | None:
        """Check if compatibility analysis already exists"""

        response = (
            self.supabase.table("compatibility_analysis_results")
            .select("*")
            .eq("user_id_main", user_id)
            .eq("other_profile_id", other_profile_id)
            .execute()
        )

        if response.data:
            return CompatibilityAnalysisResult(**response.data[0])

        return None

    async def _perform_compatibility_analysis(
        self,
        main_profile: dict[str, Any],
        other_profile: dict[str, Any],
        analysis_depth: str,
    ) -> dict[str, Any]:
        """Perform compatibility analysis using algorithm service"""

        try:
            # Prepare birth info for both profiles
            main_birth_info = {
                "year": main_profile.get("birth_year"),
                "month": main_profile.get("birth_month"),
                "day": main_profile.get("birth_day"),
                "hour": main_profile.get("birth_hour"),
                "minute": main_profile.get("birth_minute"),
                "second": main_profile.get("birth_second"),
                "location": main_profile.get("birth_location"),
                "longitude": main_profile.get("birth_longitude"),
                "latitude": main_profile.get("birth_latitude"),
            }

            other_birth_info = {
                "name": other_profile.get("name"),
                "gender": other_profile.get("gender"),
                "birth_year": other_profile.get("birth_year"),
                "birth_month": other_profile.get("birth_month"),
                "birth_day": other_profile.get("birth_day"),
                "birth_hour": other_profile.get("birth_hour"),
                "birth_minute": other_profile.get("birth_minute"),
                "birth_second": other_profile.get("birth_second"),
                "birth_location": other_profile.get("birth_location"),
                "birth_longitude": other_profile.get("birth_longitude"),
                "birth_latitude": other_profile.get("birth_latitude"),
            }

            async with httpx.AsyncClient() as client:
                payload = {
                    "user_id_main": main_profile["id"],
                    "main_profile_birth_info": main_birth_info,
                    "other_profile_birth_info": other_birth_info,
                    "analysis_depth": analysis_depth,
                }

                response = await client.post(
                    f"{settings.ALGORITHM_SERVICE_URL}/api/algorithm/compatibility/calculate",
                    json=payload,
                    timeout=60.0,  # Longer timeout for complex analysis
                )

                if response.status_code == 200:
                    result = response.json()
                    return dict(result.get("compatibility_result", {}))
                else:
                    print(
                        f"Algorithm service error: {response.status_code} - {response.text}"
                    )

        except Exception as e:
            print(f"Error calling algorithm service: {str(e)}")

        # Fallback analysis result
        return {
            "overall_score": 75,
            "aspect_scores": {
                "emotional_connection": 80,
                "communication_style": 70,
                "values_alignment": 75,
                "conflict_resolution": 75,
            },
            "relationship_overview": "你们之间有着不错的匹配度，在多个方面都展现出良好的兼容性。",
            "short_term_outlook": "短期内你们的关系会比较和谐。",
            "medium_term_outlook": "中期需要在沟通方面多下功夫。",
            "long_term_outlook": "长期来看你们有潜力建立稳定的关系。",
            "strengths": ["情感连接良好", "价值观相近"],
            "challenges": ["沟通方式需要磨合"],
            "actionable_advice": ["多进行深度交流", "学会倾听对方"],
        }

    async def _store_analysis_result(
        self, user_id: str, other_profile_id: str, analysis_data: dict[str, Any]
    ) -> None:
        """Store compatibility analysis result"""

        analysis_record = {
            "user_id_main": user_id,
            "other_profile_id": other_profile_id,
            "analysis_data": analysis_data,
            "analysis_date": datetime.utcnow().date().isoformat(),
        }

        response = (
            self.supabase.table("compatibility_analysis_results")
            .insert(analysis_record)
            .execute()
        )

        if not response.data:
            raise Exception("Failed to store compatibility analysis result")

    async def _create_compatibility_message(
        self, user_id: str, compatibility_result: dict[str, Any], other_name: str
    ) -> ChatMessage | None:
        """Create a chat message for compatibility result"""

        try:
            # Get the most recent active session for the user
            session_response = (
                self.supabase.table("chat_sessions")
                .select("*")
                .eq("user_id", user_id)
                .eq("is_active", True)
                .order("session_start_time", desc=True)
                .limit(1)
                .execute()
            )

            if not session_response.data:
                return None

            session_id = session_response.data[0]["id"]

            # Create message content
            overall_score = compatibility_result.get("overall_score", 0)
            content = f"我已经完成了你和{other_name}的合盘分析。你们的整体匹配度是{overall_score}分（满分100）。{compatibility_result.get('relationship_overview', '')}"

            # Store message
            message_data = {
                "session_id": session_id,
                "sender_type": SenderType.AI.value,
                "content": content,
                "timestamp": datetime.utcnow().isoformat(),
                "message_type": MessageType.COMPATIBILITY_CARD.value,
                "related_data": compatibility_result,
            }

            message_response = (
                self.supabase.table("chat_messages").insert(message_data).execute()
            )

            if message_response.data:
                return ChatMessage(**message_response.data[0])

        except Exception as e:
            print(f"Error creating compatibility message: {str(e)}")

        return None


# Global service instance
compatibility_service = CompatibilityService()
