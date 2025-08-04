"""
Chat Service

Handles chat sessions, messaging, and integration with AI service.
"""
from datetime import datetime

import httpx
from gotrue import SyncGoTrueClient  # type: ignore

from src.config.env import settings
from src.config.supabase import admin_client, supabase_client
from src.types.database import (
    Avatar,
    ChatHistoryResponse,
    ChatInitiateRequest,
    ChatInitiateResponse,
    ChatMessage,
    ChatMessageRequest,  # Ensure ChatMessageRequest is explicitly imported and visible
    ChatMessageResponse,
    ChatSession,
    ChatSessionsResponse,
    MessageType,
    ProfileResponse,
    SenderType,
)
from supabase.client import Client, SyncPostgrestClient


class ChatService:
    """Service for handling chat-related operations."""

    def __init__(
        self,
        db_client: Client = supabase_client,
        auth_client: SyncGoTrueClient = admin_client.auth,
        http_client: httpx.AsyncClient = httpx.AsyncClient(),
    ) -> None:
        self.db_client: SyncPostgrestClient = db_client
        self.auth_client: SyncGoTrueClient = auth_client
        self.http_client = http_client

    async def initiate_chat(
        self, user_id: str, request: ChatInitiateRequest
    ) -> ChatInitiateResponse:
        """Initiates a new chat session for a user with a selected AI avatar.

        Args:
            user_id (str): The ID of the user initiating the chat.
            request (ChatInitiateRequest): The request body containing the avatar ID.

        Returns:
            ChatInitiateResponse: The response containing the new session ID, initial AI message,
                                    user profile, and avatar details.

        Raises:
            ValueError: If the avatar is not found, session creation fails, or initial AI message storage fails.
            RuntimeError: If there is an error communicating with the algorithm service.
        """
        # Check if the avatar exists
        avatar_response = (
            self.db_client.table("avatars")
            .select("*", count="exact")
            .eq("id", str(request.avatar_id))
            .single()
            .execute()
        )

        if not avatar_response.data:
            raise ValueError(f"Avatar with ID {request.avatar_id} not found.")

        avatar = Avatar(**avatar_response.data)

        # Create a new chat session
        session_data = {
            "user_id": user_id,
            "avatar_id": str(request.avatar_id),
            "session_start_time": datetime.now().isoformat(),
            "is_active": True,
        }
        session_response = (
            self.db_client.table("chat_sessions").insert(session_data).execute()
        )

        if not session_response.data or session_response.count == 0:
            raise ValueError("Failed to create chat session.")

        new_session = ChatSession(**session_response.data[0])

        # Get initial AI message and user profile from algorithm service
        initial_message_content = (
            f"Hello! I am {avatar.name}. How can I assist you today?"
        )
        initial_message_obj, user_profile_obj = await self._get_initial_message(
            user_id=user_id, initial_message_content=initial_message_content
        )

        # Store the initial AI message
        ai_message_data = {
            "session_id": str(new_session.id),
            "sender_type": SenderType.AI.value,
            "message_type": MessageType.TEXT.value,
            "content": initial_message_obj.content,
            "timestamp": datetime.now().isoformat(),
        }
        ai_message_response = (
            self.db_client.table("chat_messages").insert(ai_message_data).execute()
        )

        if not ai_message_response.data or ai_message_response.count == 0:
            raise ValueError("Failed to store initial AI message.")

        # Create ChatMessage object from the stored data to ensure consistency
        stored_initial_message = ChatMessage(**ai_message_response.data[0])

        return ChatInitiateResponse(
            session_id=new_session.id,
            initial_message=stored_initial_message,
            user_profile=user_profile_obj,
            avatar=avatar,
        )

    async def send_message(
        self, session_id: str, user_id: str, request: ChatMessageRequest
    ) -> ChatMessageResponse:
        """Sends a new message to an existing chat session and gets AI response.

        Args:
            session_id (str): The ID of the chat session.
            user_id (str): The ID of the user sending the message.
            request (ChatMessageRequest): The request body containing the message content.

        Returns:
            ChatMessageResponse: The response containing the sent message and AI's response.

        Raises:
            ValueError: If the chat session is not found or message storage fails.
            RuntimeError: If there is an error communicating with the algorithm service.
        """
        # Verify chat session exists
        session_response = (
            self.db_client.table("chat_sessions")
            .select("*", count="exact")
            .eq("id", session_id)
            .single()
            .execute()
        )

        if not session_response.data:
            raise ValueError("Chat session not found.")

        # Store user message
        user_message_data = {
            "session_id": session_id,
            "sender_type": SenderType.USER.value,
            "message_type": MessageType.TEXT.value,
            "content": request.content,
            "timestamp": datetime.now().isoformat(),
        }
        user_message_response = (
            self.db_client.table("chat_messages").insert(user_message_data).execute()
        )

        if not user_message_response.data or user_message_response.count == 0:
            raise ValueError("Failed to store user message.")

        user_message = ChatMessage(**user_message_response.data[0])

        # Get AI response from algorithm service
        ai_response_obj = await self._get_ai_response(
            session_id=session_id,
            user_id=user_id,
            message_content=request.content,
        )

        # Store AI response
        ai_response_data = {
            "session_id": session_id,
            "sender_type": SenderType.AI.value,
            "message_type": MessageType.TEXT.value,
            "content": ai_response_obj.content,
            "timestamp": datetime.now().isoformat(),
        }
        stored_ai_message_response = (
            self.db_client.table("chat_messages").insert(ai_response_data).execute()
        )

        if not stored_ai_message_response.data or stored_ai_message_response.count == 0:
            # This is a critical failure, consider more robust error handling/rollback
            print("Warning: Failed to store AI response message.")
            stored_ai_message = None  # type: ignore[assignment]
        else:
            stored_ai_message = ChatMessage(**stored_ai_message_response.data[0])

        return ChatMessageResponse(message=user_message, ai_response=stored_ai_message)

    async def get_chat_history(
        self, session_id: str, user_id: str
    ) -> ChatHistoryResponse:
        """Retrieves the chat history for a given session.

        Args:
            session_id (str): The ID of the chat session.
            user_id (str): The ID of the user requesting the history.

        Returns:
            ChatHistoryResponse: The chat session details and a list of messages.

        Raises:
            ValueError: If the chat session is not found.
        """
        session_response = (
            self.db_client.table("chat_sessions")
            .select("*", count="exact")
            .eq("id", session_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )

        if not session_response.data:
            raise ValueError("Chat session not found.")

        session = ChatSession(**session_response.data)

        messages_response = (
            self.db_client.table("chat_messages")
            .select("*", count="exact")
            .eq("session_id", session_id)
            .order("timestamp", desc=False)
            .execute()
        )

        messages = [
            ChatMessage(**msg)
            for msg in messages_response.data
            if messages_response.data
        ]

        return ChatHistoryResponse(session=session, messages=messages)

    async def get_user_sessions(self, user_id: str) -> ChatSessionsResponse:
        """Retrieves all chat sessions for a given user, including related avatar and profile info.

        Args:
            user_id (str): The ID of the user.

        Returns:
            ChatSessionsResponse: A list of chat sessions with associated avatar and user profile.
        """
        sessions_response = (
            self.db_client.table("chat_sessions")
            .select(
                "*,"
                "avatars(id, name, image_url),"
                "profiles(id, nickname, gender, birth_year, birth_month, birth_day, birth_location, analysis_completed)"
            )
            .eq("user_id", user_id)
            .order("session_start_time", desc=True)
            .execute()
        )

        sessions = []
        for session_data in sessions_response.data:
            avatar_data = session_data.pop("avatars")  # Extract avatar data
            profile_data = session_data.pop("profiles")  # Extract profile data

            # Create Avatar and Profile objects
            avatar_obj = Avatar(**avatar_data) if avatar_data else None

            # Manually instantiate ProfileResponse, handling potential None values
            # profile_obj is not directly used for ChatSession appending, it's for type consistency of data from DB
            # profile_obj = None
            # Removed profile_obj instantiation as it was unused and caused linting errors
            # if profile_data:
            #     profile_obj = ProfileResponse(
            #         id=UUID(profile_data['id']),
            #         nickname=profile_data.get('nickname'),
            #         gender=GenderEnum(profile_data['gender']) if profile_data.get('gender') else None,
            #         birth_year=profile_data.get('birth_year'),
            #         birth_month=profile_data.get('birth_month'),
            #         birth_day=profile_data.get('birth_day'),
            #         birth_hour=None, # Assuming these are not returned by this specific select
            #         birth_minute=None,
            #         birth_second=None,
            #         birth_location=profile_data.get('birth_location'),
            #         birth_longitude=None, # Assuming these are not returned by this specific select
            #         birth_latitude=None,
            #         selected_avatar=avatar_obj, # Link the avatar object
            #         analysis_completed=profile_data.get('analysis_completed', False),
            #         created_at=datetime.fromisoformat(profile_data['created_at']),
            #         updated_at=datetime.fromisoformat(profile_data['updated_at'])
            #     )

            # Reconstruct session data with correct avatar and profile objects
            session_obj = ChatSession(**session_data)
            # NOTE: ChatSession does not directly contain profile or full avatar objects,
            # these are part of the outer response structure or retrieved separately.
            # For now, we will return the basic ChatSession objects.
            sessions.append(session_obj)

        return ChatSessionsResponse(sessions=sessions)

    async def _get_initial_message(
        self, user_id: str, initial_message_content: str
    ) -> tuple[ChatMessage, ProfileResponse]:
        """Calls the algorithm service to get the initial AI message and user profile.

        Args:
            user_id (str): The ID of the user.
            initial_message_content (str): The initial message content to send to the AI.

        Returns:
            Tuple[ChatMessage, ProfileResponse]: The initial AI message and the updated user profile.

        Raises:
            ValueError: If the algorithm service returns an error or invalid data.
            RuntimeError: If there is a network or unexpected error during communication.
        """
        try:
            response = await self.http_client.post(
                f"{settings.ALGORITHM_SERVICE_URL}/chat/initiate",
                json={
                    "user_id": user_id,
                    "initial_message": initial_message_content,
                },
                timeout=settings.ALGORITHM_SERVICE_TIMEOUT,
            )
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
            response_data = response.json()

            if (
                "initial_message" not in response_data
                or "user_profile" not in response_data
            ):
                raise ValueError("Algorithm service returned incomplete data.")

            initial_message = ChatMessage(**response_data["initial_message"])
            user_profile = ProfileResponse(**response_data["user_profile"])

            return initial_message, user_profile
        except httpx.HTTPStatusError as e:
            print(f"HTTP error during initial message retrieval: {e}")
            raise ValueError(
                "Algorithm service error during initial message retrieval"
            ) from e
        except httpx.RequestError as e:
            print(f"Network error during initial message retrieval: {e}")
            raise RuntimeError(
                "Failed to get initial message from algorithm service"
            ) from e
        except Exception as e:
            print(f"Unexpected error during initial message retrieval: {e}")
            raise RuntimeError(
                "Failed to get initial message from algorithm service"
            ) from e

    async def _get_ai_response(
        self, session_id: str, user_id: str, message_content: str
    ) -> ChatMessage:
        """Calls the algorithm service to get AI's response to a message.

        Args:
            session_id (str): The ID of the chat session.
            user_id (str): The ID of the user.
            message_content (str): The content of the user's message.

        Returns:
            ChatMessage: The AI's response message.

        Raises:
            ValueError: If the algorithm service returns an error or invalid data.
            RuntimeError: If there is a network or unexpected error during communication.
        """
        try:
            response = await self.http_client.post(
                f"{settings.ALGORITHM_SERVICE_URL}/chat/send_message",
                json={
                    "session_id": session_id,
                    "user_id": user_id,
                    "message": message_content,
                },
                timeout=settings.ALGORITHM_SERVICE_TIMEOUT,
            )
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
            response_data = response.json()

            if "ai_response" not in response_data:
                raise ValueError("Algorithm service returned incomplete data.")

            ai_response = ChatMessage(**response_data["ai_response"])

            return ai_response
        except httpx.HTTPStatusError as e:
            print(f"HTTP error during AI response retrieval: {e}")
            raise ValueError(
                "Algorithm service error during AI response retrieval"
            ) from e
        except httpx.RequestError as e:
            print(f"Network error during AI response retrieval: {e}")
            raise RuntimeError(
                "Failed to get AI response from algorithm service"
            ) from e
        except Exception as e:
            print(f"Unexpected error during AI response retrieval: {e}")
            raise RuntimeError(
                "Failed to get AI response from algorithm service"
            ) from e


chat_service = ChatService()
