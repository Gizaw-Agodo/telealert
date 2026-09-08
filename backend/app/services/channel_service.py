import logging
from telethon.errors import ChannelPrivateError, FloodWaitError  # type: ignore
from telethon.tl.functions.channels import JoinChannelRequest # type: ignore
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.channel import Channel
from app.workers.telethon_collector import client as telethon_client

logger = logging.getLogger(__name__)


class ChannelService:

    @staticmethod
    async def get_or_join_channel(
        username: str, db: AsyncSession
    ) -> tuple[Channel | None, str | None]:
        """
        Retrieves channel from DB or uses Telethon to join it.
        Returns: (Channel instance or None, error_message or None)
        """
        clean_username = username.replace("@", "").strip().lower()

        # 1. Check local DB
        res = await db.execute(select(Channel).where(Channel.username == clean_username))
        channel = res.scalar_one_or_none()
        if channel:
            return channel, None

        # 2. Attempt joining via Telethon
        try:
            await telethon_client(JoinChannelRequest(clean_username)) # type: ignore
        except ChannelPrivateError:
            return None, "❌ Channel is private. Only public channels can be monitored."
        except ValueError:
            return None, "❌ Channel not found. Please check the username."
        except FloodWaitError as e:
            return None, f"⏳ Telegram rate limit active. Retry in {e.seconds}s."
        except Exception as e:
            logger.error(f"Failed to join @{clean_username}: {e}")
            return None, f"❌ Failed to join channel: {str(e)}"

        # 3. Persist to DB
        channel = Channel(username=clean_username, is_joined=True)
        db.add(channel)
        await db.commit()
        await db.refresh(channel)

        return channel, None