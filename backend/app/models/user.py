from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from uuid import uuid4
from datetime import date

from sqlalchemy import BigInteger, DateTime,  String, Date, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base


if TYPE_CHECKING:
    from app.models.rule import AlertRule


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column( String(36), primary_key=True, default=lambda: str(uuid4()))
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    telegram_username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Quotas & Limits (Adapted for Alert Monitoring)
    daily_limit_resets_at: Mapped[date] = mapped_column( Date, default=date.today, nullable=False)
    daily_alerts_sent_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_daily_alerts: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    max_active_rules: Mapped[int] = mapped_column(Integer, default=3, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column( DateTime(timezone=True),default=lambda: datetime.now(timezone.utc),nullable=False,)
    updated_at: Mapped[datetime] = mapped_column( DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),onupdate=lambda: datetime.now(timezone.utc),nullable=False,)

    # Relationships
    rules: Mapped[List["AlertRule"]] = relationship(back_populates="user", cascade="all, delete-orphan")
