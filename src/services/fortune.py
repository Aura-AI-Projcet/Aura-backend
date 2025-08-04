"""
Fortune Service

Handles daily fortune, tarot, and divination features.
"""
from datetime import date, datetime
from typing import Any

import httpx

from ..config.env import settings
from ..config.supabase import admin_client, supabase_client
from ..types.database import (
    DailyFortune,
    DailyFortuneResponse,
    FortuneRequest,
    FortuneResponse,
    MessageType,
    SenderType,
)


class FortuneService:
    """Service for handling fortune and divination features"""

    def __init__(self) -> None:
        self.supabase = supabase_client
        self.admin_supabase = admin_client

    async def get_daily_fortune(
        self, user_id: str, target_date: str | None = None
    ) -> DailyFortuneResponse:
        """Get daily fortune for user"""

        if not target_date:
            target_date = date.today().isoformat()

        # Check if fortune already exists for this date
        existing_response = (
            self.supabase.table("daily_fortunes")
            .select("*")
            .eq("user_id", user_id)
            .eq("fortune_date", target_date)
            .execute()
        )

        if existing_response.data:
            fortune = DailyFortune(**existing_response.data[0])
            return DailyFortuneResponse(fortune=fortune, can_generate_new=False)

        # Generate new fortune if none exists
        fortune_data = await self._generate_daily_fortune(user_id, target_date)

        # Store the fortune
        fortune_record = {
            "user_id": user_id,
            "fortune_date": target_date,
            "fortune_data": fortune_data,
            "generated_at": datetime.utcnow().isoformat(),
            "is_pushed": False,
        }

        response = (
            self.supabase.table("daily_fortunes").insert(fortune_record).execute()
        )

        if not response.data:
            raise Exception("Failed to store daily fortune")

        fortune = DailyFortune(**response.data[0])
        return DailyFortuneResponse(fortune=fortune, can_generate_new=True)

    async def predict_fortune(
        self, user_id: str, request: FortuneRequest
    ) -> FortuneResponse:
        """Handle fortune prediction requests (tarot, divination, etc.)"""

        # Get user profile for context
        profile_response = (
            self.supabase.table("profiles").select("*").eq("id", user_id).execute()
        )
        user_profile = profile_response.data[0] if profile_response.data else {}

        # Call algorithm service
        fortune_result = await self._call_fortune_algorithm(
            user_id, request, user_profile
        )

        # Create related chat message if needed
        related_message = None
        if request.request_type in ["tarot", "divination"]:
            related_message = await self._create_fortune_message(
                user_id, fortune_result, request.request_type
            )

        return FortuneResponse(
            fortune_result=fortune_result,
            related_message=related_message,  # type: ignore # Will be implemented when ChatMessage integration is ready
        )

    async def get_fortune_history(
        self, user_id: str, limit: int = 30
    ) -> list[DailyFortune]:
        """Get user's fortune history"""

        response = (
            self.supabase.table("daily_fortunes")
            .select("*")
            .eq("user_id", user_id)
            .order("fortune_date", desc=True)
            .limit(limit)
            .execute()
        )

        return [DailyFortune(**fortune) for fortune in response.data]

    async def _generate_daily_fortune(
        self, user_id: str, fortune_date: str
    ) -> dict[str, Any]:
        """Generate daily fortune using algorithm service"""

        try:
            # Get user profile
            profile_response = (
                self.supabase.table("profiles").select("*").eq("id", user_id).execute()
            )
            user_profile = profile_response.data[0] if profile_response.data else {}

            async with httpx.AsyncClient() as client:
                payload = {
                    "user_id": user_id,
                    "date": fortune_date,
                    "user_profile": user_profile,
                }

                response = await client.post(
                    f"{settings.ALGORITHM_SERVICE_URL}/api/algorithm/daily-fortune/calculate",
                    json=payload,
                    timeout=30.0,
                )

                if response.status_code == 200:
                    result = response.json()
                    return dict(result.get("fortune_details", {}))
                else:
                    print(
                        f"Algorithm service error: {response.status_code} - {response.text}"
                    )

        except Exception as e:
            print(f"Error calling algorithm service: {str(e)}")

        # Fallback fortune data
        return {
            "luck_level": "平",
            "suitability": ["宜保持心情愉悦", "忌过度劳累"],
            "lucky_color": "蓝色",
            "lucky_number": 7,
            "general_summary": "今日运势平稳，适合静心思考，关注内心声音。",
        }

    async def _call_fortune_algorithm(
        self, user_id: str, request: FortuneRequest, user_profile: dict[str, Any]
    ) -> dict[str, Any]:
        """Call algorithm service for fortune prediction"""

        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "user_id": user_id,
                    "request_type": request.request_type,
                    "user_profile": user_profile,
                }

                # Add specific fields based on request type
                if request.date:
                    payload["date"] = request.date
                if request.question:
                    payload["tarot_question"] = request.question
                if request.divination_type:
                    payload["divination_type"] = request.divination_type

                response = await client.post(
                    f"{settings.ALGORITHM_SERVICE_URL}/api/algorithm/fortune/predict",
                    json=payload,
                    timeout=30.0,
                )

                if response.status_code == 200:
                    result = response.json()
                    return dict(result.get("fortune_result", {}))
                else:
                    print(
                        f"Algorithm service error: {response.status_code} - {response.text}"
                    )

        except Exception as e:
            print(f"Error calling algorithm service: {str(e)}")

        # Fallback result
        return {
            "type": request.request_type,
            "summary": "暂时无法获取结果，请稍后再试。",
            "details": {},
        }

    async def _create_fortune_message(
        self, user_id: str, fortune_result: dict[str, Any], fortune_type: str
    ) -> dict[str, Any] | None:
        """Create a chat message for fortune result"""

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

            # Determine message type
            message_type = (
                MessageType.TAROT_RESULT
                if fortune_type == "tarot"
                else MessageType.DIVINATION_RESULT
            )

            # Create message content
            content = fortune_result.get("summary", "你的运势结果已生成完毕。")

            # Store message
            message_data = {
                "session_id": session_id,
                "sender_type": SenderType.AI.value,
                "content": content,
                "timestamp": datetime.utcnow().isoformat(),
                "message_type": message_type.value,
                "related_data": fortune_result,
            }

            message_response = (
                self.supabase.table("chat_messages").insert(message_data).execute()
            )

            if message_response.data:
                return dict(message_response.data[0])

        except Exception as e:
            print(f"Error creating fortune message: {str(e)}")

        return None


# Global service instance
fortune_service = FortuneService()
