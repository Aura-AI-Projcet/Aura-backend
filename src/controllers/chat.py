"""
Chat Controller

Handles HTTP requests for chat functionality.
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, status

from ..middleware.auth import get_current_user_id
from ..services.chat import chat_service
from ..types.database import (
    ChatHistoryResponse,
    ChatInitiateRequest,
    ChatInitiateResponse,
    ChatMessageRequest,
    ChatMessageResponse,
    ChatSession,
)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/initiate", response_model=ChatInitiateResponse)
async def initiate_chat(
    request: ChatInitiateRequest, user_id: str = Depends(get_current_user_id)
) -> ChatInitiateResponse:
    """Initiate a new chat session"""
    try:
        response = await chat_service.initiate_chat(user_id, request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate chat: {str(e)}",
        )


@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
async def send_message(
    session_id: str,
    request: ChatMessageRequest,
    user_id: str = Depends(get_current_user_id),
) -> ChatMessageResponse:
    """Send a message in a chat session"""
    try:
        response = await chat_service.send_message(user_id, session_id, request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}",
        )


@router.get("/sessions/{session_id}/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    limit: int = 50,
    offset: int = 0,
    user_id: str = Depends(get_current_user_id),
) -> ChatHistoryResponse:
    """Get chat history for a session"""
    try:
        response = await chat_service.get_chat_history(
            user_id, session_id, limit, offset
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chat history: {str(e)}",
        )


@router.get("/sessions", response_model=list[ChatSession])
async def get_user_sessions(
    limit: int = 20, user_id: str = Depends(get_current_user_id)
) -> list[ChatSession]:
    """Get user's chat sessions"""
    try:
        sessions = await chat_service.get_user_sessions(user_id, limit)
        return sessions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sessions: {str(e)}",
        )


# WebSocket endpoint for real-time chat (optional - for future implementation)
@router.websocket("/sessions/{session_id}/ws")
async def websocket_endpoint(websocket: WebSocket, session_id: str) -> None:
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()

    try:
        while True:
            # Wait for message from client
            data = await websocket.receive_text()

            # Echo back for now (implement real chat logic later)
            await websocket.send_text(f"Echo: {data}")

    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()
