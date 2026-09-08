from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.channel import ChannelResponse


class AlertRuleBase(BaseModel):
    keyword: str = Field(..., min_length=2, max_length=100)
    match_type: str = Field(default="contains", description="'contains', 'exact', or 'regex'")
    is_case_sensitive: bool = Field(default=False)


class AlertRuleCreate(AlertRuleBase):
    """
    To create a rule, the user just provides the channel username and keyword.
    The backend will handle finding/creating the Channel ID under the hood.
    """
    channel_username: str = Field(..., description="Target channel username")
    user_id: str = Field(..., description="The UUID of the user making the request")


class AlertRuleUpdate(BaseModel):
    keyword: Optional[str] = Field(None, min_length=2, max_length=100)
    match_type: Optional[str] = None
    is_case_sensitive: Optional[bool] = None
    is_active: Optional[bool] = None


class AlertRuleResponse(AlertRuleBase):
    id: str
    user_id: str
    channel_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # Include the channel data in the response so the frontend can display it
    channel: Optional[ChannelResponse] = None

    model_config = ConfigDict(from_attributes=True)