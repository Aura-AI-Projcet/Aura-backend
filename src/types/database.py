"""
Database Models and Types
"""
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class GenderEnum(str, Enum):
    """Gender enumeration"""

    MALE = "male"
    FEMALE = "female"
    SECRET = "secret"
    LGBTQ_PLUS = "lgbtq+"


class Avatar(BaseModel):
    """Avatar model"""

    id: UUID
    name: str
    description: str | None = None
    image_url: str | None = None
    abilities: list[str] | None = None
    initial_dialogue_prompt: str | None = None
    created_at: datetime
    updated_at: datetime


class Profile(BaseModel):
    """User profile model"""

    id: UUID
    nickname: str | None = None
    gender: GenderEnum | None = None
    birth_year: int | None = None
    birth_month: int | None = None
    birth_day: int | None = None
    birth_hour: int | None = None
    birth_minute: int | None = None
    birth_second: int | None = None
    birth_location: str | None = None
    birth_longitude: float | None = None
    birth_latitude: float | None = None
    selected_avatar_id: UUID | None = None
    created_at: datetime
    updated_at: datetime


class UserProfileAnalysis(BaseModel):
    """User profile analysis result model"""

    id: UUID
    user_id: UUID
    analysis_data: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class OtherProfile(BaseModel):
    """Other person profile model for compatibility analysis"""

    id: UUID
    user_id: UUID
    name: str
    gender: GenderEnum | None = None
    birth_year: int
    birth_month: int
    birth_day: int
    birth_hour: int | None = None
    birth_minute: int | None = None
    birth_second: int | None = None
    birth_location: str | None = None
    birth_longitude: float | None = None
    birth_latitude: float | None = None
    relation_type: str | None = None
    created_at: datetime
    updated_at: datetime


# Request/Response Models for API


class BirthInfo(BaseModel):
    """Birth information model"""

    year: int = Field(..., ge=1900, le=2030)
    month: int = Field(..., ge=1, le=12)
    day: int = Field(..., ge=1, le=31)
    hour: int | None = Field(None, ge=0, le=23)
    minute: int | None = Field(None, ge=0, le=59)
    second: int | None = Field(None, ge=0, le=59)
    location: str = Field(..., min_length=1)
    longitude: float | None = Field(None, ge=-180, le=180)
    latitude: float | None = Field(None, ge=-90, le=90)


class CreateProfileRequest(BaseModel):
    """Request model for creating user profile"""

    nickname: str = Field(..., min_length=1, max_length=50)
    gender: GenderEnum
    birth_info: BirthInfo
    selected_avatar_id: UUID


class UpdateProfileRequest(BaseModel):
    """Request model for updating user profile"""

    nickname: str | None = Field(None, min_length=1, max_length=50)
    gender: GenderEnum | None = None
    birth_info: BirthInfo | None = None
    selected_avatar_id: UUID | None = None


class ProfileResponse(BaseModel):
    """Response model for user profile"""

    id: UUID
    nickname: str | None
    gender: GenderEnum | None
    birth_year: int | None
    birth_month: int | None
    birth_day: int | None
    birth_hour: int | None
    birth_minute: int | None
    birth_second: int | None
    birth_location: str | None
    birth_longitude: float | None
    birth_latitude: float | None
    selected_avatar: Avatar | None = None
    analysis_completed: bool = False
    created_at: datetime
    updated_at: datetime


class OnboardingStep(str, Enum):
    """Onboarding step enumeration"""

    BASIC_INFO = "basic_info"
    BIRTH_INFO = "birth_info"
    AVATAR_SELECTION = "avatar_selection"
    ANALYSIS_PROCESSING = "analysis_processing"
    FIRST_CHAT = "first_chat"
    COMPLETED = "completed"


class OnboardingStatusResponse(BaseModel):
    """Response model for onboarding status"""

    current_step: OnboardingStep
    completed_steps: list[OnboardingStep]
    profile: ProfileResponse | None = None
    available_avatars: list[Avatar]


# Chat and Messaging Models


class ChatSession(BaseModel):
    """Chat session model"""

    id: UUID
    user_id: UUID
    avatar_id: UUID
    session_start_time: datetime
    session_end_time: datetime | None = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class MessageType(str, Enum):
    """Message type enumeration"""

    TEXT = "text"
    FORTUNE_CARD = "fortune_card"
    COMPATIBILITY_CARD = "compatibility_card"
    TAROT_RESULT = "tarot_result"
    DIVINATION_RESULT = "divination_result"


class SenderType(str, Enum):
    """Message sender type enumeration"""

    USER = "user"
    AI = "ai"


class ChatMessage(BaseModel):
    """Chat message model"""

    id: UUID
    session_id: UUID
    sender_type: SenderType
    content: str
    timestamp: datetime
    message_type: MessageType = MessageType.TEXT
    related_data: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


# Fortune and Divination Models


class DailyFortune(BaseModel):
    """Daily fortune model"""

    id: UUID
    user_id: UUID
    fortune_date: datetime
    fortune_data: dict[str, Any]
    generated_at: datetime
    is_pushed: bool = False
    created_at: datetime
    updated_at: datetime


# Compatibility Analysis Models


class CompatibilityAnalysisResult(BaseModel):
    """Compatibility analysis result model"""

    id: UUID
    user_id_main: UUID
    other_profile_id: UUID
    analysis_data: dict[str, Any]
    analysis_date: datetime
    created_at: datetime
    updated_at: datetime


# Payment and Subscription Models


class TransactionType(str, Enum):
    """Transaction type enumeration"""

    PURCHASE = "purchase"
    REFUND = "refund"
    RECHARGE = "recharge"


class TransactionStatus(str, Enum):
    """Transaction status enumeration"""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PricingPlan(BaseModel):
    """Pricing plan model"""

    id: UUID
    name: str
    description: str
    price: float
    currency: str = "USD"
    duration_days: int | None = None
    features: dict[str, Any]
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class Transaction(BaseModel):
    """Transaction model"""

    id: UUID
    user_id: UUID
    plan_id: UUID | None = None
    amount: float
    currency: str
    transaction_type: TransactionType
    status: TransactionStatus
    payment_gateway_id: str | None = None
    payment_method: str | None = None
    transaction_time: datetime
    created_at: datetime
    updated_at: datetime


class SubscriptionStatus(str, Enum):
    """Subscription status enumeration"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELLED = "cancelled"


class UserSubscription(BaseModel):
    """User subscription model"""

    id: UUID
    user_id: UUID
    plan_id: UUID
    start_date: datetime
    end_date: datetime
    status: SubscriptionStatus
    auto_renew: bool = False
    created_at: datetime
    updated_at: datetime


# API Request/Response Models


# Chat API Models
class ChatInitiateRequest(BaseModel):
    """Request model for initiating chat"""

    avatar_id: UUID


class ChatInitiateResponse(BaseModel):
    """Response model for chat initiation"""

    session_id: UUID
    initial_message: ChatMessage
    user_profile: ProfileResponse  # Add user_profile
    avatar: Avatar  # Add avatar


class ChatMessageRequest(BaseModel):
    """Request model for sending chat message"""

    content: str = Field(..., min_length=1, max_length=2000)


class ChatMessageResponse(BaseModel):
    """Response model for chat message"""

    message: ChatMessage
    ai_response: ChatMessage | None = None
    suggested_actions: list[dict[str, Any]] | None = None


class ChatHistoryResponse(BaseModel):
    """Response model for chat history"""

    session: ChatSession
    messages: list[ChatMessage]
    has_more: bool = False


class ChatSessionsResponse(BaseModel):
    """Response model for user chat sessions"""

    sessions: list[ChatSession]


# Fortune API Models
class FortuneRequest(BaseModel):
    """Request model for fortune prediction"""

    request_type: str = Field(..., description="daily_fortune, tarot, divination")
    date: str | None = Field(None, description="YYYY-MM-DD for daily fortune")
    question: str | None = Field(None, min_length=1, max_length=500)
    divination_type: str | None = Field(None, description="求签, 摇卦, 金钱卦")


class FortuneResponse(BaseModel):
    """Response model for fortune prediction"""

    fortune_result: dict[str, Any]
    related_message: ChatMessage | None = None


# Compatibility API Models
class CreateOtherProfileRequest(BaseModel):
    """Request model for creating other person profile"""

    name: str = Field(..., min_length=1, max_length=50)
    gender: GenderEnum | None = None
    birth_info: BirthInfo
    relation_type: str | None = Field(None, max_length=50)


class OtherProfileResponse(BaseModel):
    """Response model for other person profile"""

    id: UUID
    name: str
    gender: GenderEnum | None
    birth_year: int
    birth_month: int
    birth_day: int
    birth_hour: int | None
    birth_minute: int | None
    birth_second: int | None
    birth_location: str | None
    relation_type: str | None
    created_at: datetime


class CompatibilityRequest(BaseModel):
    """Request model for compatibility analysis"""

    other_profile_id: UUID
    analysis_depth: str = Field(
        default="all", description="short_term, medium_term, long_term, all"
    )


class CompatibilityResponse(BaseModel):
    """Response model for compatibility analysis"""

    compatibility_result: dict[str, Any]
    other_profile: OtherProfileResponse
    related_message: ChatMessage | None = None


# Payment API Models
class CreateTransactionRequest(BaseModel):
    """Request model for creating transaction"""

    plan_id: UUID
    payment_method: str = Field(..., description="stripe, alipay")


class TransactionResponse(BaseModel):
    """Response model for transaction"""

    transaction: Transaction
    payment_url: str | None = None
    client_secret: str | None = None


class WebhookEventRequest(BaseModel):
    """Request model for payment webhook"""

    event_type: str
    event_data: dict[str, Any]


# Daily Fortune Models
class DailyFortuneResponse(BaseModel):
    """Response model for daily fortune"""

    fortune: DailyFortune
    can_generate_new: bool = False
