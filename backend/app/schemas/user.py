from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    telegram_id: int = Field(..., description="The user's Telegram ID")
    telegram_username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    """Payload for creating a new user (e.g., when they first start the bot)."""
    pass


class UserUpdate(BaseModel):
    """Payload for updating a user's details."""
    telegram_username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Data returned to the client."""
    id: str
    max_active_rules: int
    daily_alerts_sent_count: int
    max_daily_alerts: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)