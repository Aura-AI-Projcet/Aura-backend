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
