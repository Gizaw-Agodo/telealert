import logging
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot import templates
from app.models.rule import AlertRule
from app.models.user import User
from app.services.bot_service import send_telegram_alert
from app.services.channel_service import ChannelService

logger = logging.getLogger(__name__)


async def handle_track_command(
    telegram_id: int, user: User, text: str, db: AsyncSession
) -> None:
    """Handles the /track command to add a new monitoring rule."""
    parts = text.split(maxsplit=2)
    if len(parts) < 3:
        await send_telegram_alert(telegram_id, templates.invalid_track_format())
        return

    raw_channel, keyword = parts[1], parts[2].strip()

    # 1. Quota Check
    count_res = await db.execute(
        select(func.count(AlertRule.id)).where(
            AlertRule.user_id == user.id, AlertRule.is_active == True
        )
    )
    active_count: int = count_res.scalar_one() or 0
    if active_count >= user.max_active_rules:
        await send_telegram_alert(
            telegram_id, templates.rule_limit_reached(user.max_active_rules)
        )
        return

    # 2. Channel Resolution (Check DB or Join via Telethon)
    await send_telegram_alert(telegram_id, f"⏳ Connecting to {raw_channel}...")
    
    channel, error = await ChannelService.get_or_join_channel(raw_channel, db)
    if error or not channel:
        await send_telegram_alert(telegram_id, error or "❌ Error resolving channel.")
        return

    # 3. Create Tracking Rule
    new_rule = AlertRule(
        user_id=user.id,
        channel_id=channel.id,
        keyword=keyword,
    )
    db.add(new_rule)
    await db.commit()

    logger.info(f"User {telegram_id} is now tracking {keyword} in {channel.username}")
    
    await send_telegram_alert(
        telegram_id, templates.rule_created_message(channel.username, keyword)
    )