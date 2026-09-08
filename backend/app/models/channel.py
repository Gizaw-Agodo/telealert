from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from uuid import uuid4

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.rule import AlertRule


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    telegram_channel_id: Mapped[Optional[int]] = mapped_column(BigInteger, unique=True, index=True, nullable=True )
    username: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Worker tracking state
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_joined: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_message_id: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc),nullable=False,)
    updated_at: Mapped[datetime] = mapped_column( DateTime(timezone=True),default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc),nullable=False,)

    # Relationships
    rules: Mapped[List["AlertRule"]] = relationship(back_populates="channel", cascade="all, delete-orphan")