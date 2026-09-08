import asyncio
import logging
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import AsyncSessionLocal
from app.core.shared_queue import QueueMessagePayload, message_queue
from app.models.channel import Channel
from app.models.rule import AlertRule
from app.services.bot_service import send_telegram_alert

logger = logging.getLogger(__name__)



async def process_queue() -> None:
    """Infinite loop that pulls messages and matches them against the DB."""
    logger.info("✅ Matcher worker started.")

    while True:
        try:
            msg_data: QueueMessagePayload = await message_queue.get()
            text_lower: str = msg_data["text"].lower()
            channel_username: str = msg_data["channel_username"]

            async with AsyncSessionLocal() as db:
                # Find the channel
                result = await db.execute(select(Channel).where(Channel.username == channel_username) )
                channel: Channel | None = result.scalar_one_or_none()

                if not channel:
                    message_queue.task_done()
                    continue

                # Find active rules for this channel, including user details
                rules_result = await db.execute(
                    select(AlertRule)
                    .options(selectinload(AlertRule.user))
                    .where(
                        AlertRule.channel_id == str(channel.id),
                        AlertRule.is_active == True,
                    )
                )
                rules: Sequence[AlertRule] = rules_result.scalars().all()

                # Match keywords and trigger alerts
                for rule in rules:
                    if rule.keyword.lower() in text_lower:
                        logger.info(f"🔔 Match found for user {rule.user.telegram_id}")

                        alert_text: str = (
                            f"🚨 <b>Keyword Match:</b> {rule.keyword}\n"
                            f"📢 <b>Channel:</b> @{channel.username}\n\n"
                            f"{msg_data['text'][:300]}...\n\n"
                            f'<a href="https://t.me/{channel.username}/{msg_data["message_id"]}">🔗 Go to message</a>'
                        )

                        await send_telegram_alert(rule.user.telegram_id, alert_text)

            message_queue.task_done()

        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error processing message: {e}")