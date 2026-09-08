from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ChannelBase(BaseModel):
    username: str = Field(..., description="The channel username without the '@'")
    title: Optional[str] = None


class ChannelCreate(ChannelBase):
    telegram_channel_id: Optional[int] = None


class ChannelUpdate(BaseModel):
    title: Optional[str] = None
    is_active: Optional[bool] = None
    is_joined: Optional[bool] = None


class ChannelResponse(ChannelBase):
    id: str
    telegram_channel_id: Optional[int]
    is_active: bool
    is_joined: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)