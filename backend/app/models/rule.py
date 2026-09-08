from datetime import datetime, timezone
from typing import TYPE_CHECKING,Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.channel import Channel
    from app.models.user import User


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id: Mapped[str] = mapped_column( String(36), primary_key=True, default=lambda: str(uuid4()))

    # Foreign Keys
    user_id: Mapped[str] = mapped_column(String(36),ForeignKey("users.id", ondelete="CASCADE"),nullable=False,index=True,)
    channel_id: Mapped[str] = mapped_column(String(36),ForeignKey("channels.id", ondelete="CASCADE"),nullable=False,index=True,)

    # Search criteria
    keyword: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    match_type: Mapped[str] = mapped_column(String(50), default="contains", nullable=False)  
    is_case_sensitive: Mapped[bool] = mapped_column( Boolean, default=False, nullable=False)

    # Status & Soft Delete
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, default=None)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc),nullable=False,)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc),onupdate=lambda: datetime.now(timezone.utc),nullable=False,)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="rules")
    channel: Mapped["Channel"] = relationship(back_populates="rules")
    