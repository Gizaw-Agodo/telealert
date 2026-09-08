from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.handlers.rules import handle_delete_command, handle_list_rules_command
from app.bot.handlers.start import handle_start_command
from app.bot.handlers.track import handle_track_command
from app.bot.handlers.help import handle_help_command

from app.models.user import User
from app.services.bot_service import send_telegram_alert



class BotDispatcher:
    async def dispatch(self, update: dict[str, Any], db: AsyncSession) -> None:
        if "message" not in update or "text" not in update["message"]:
            return

        msg = update["message"]
        text: str = msg.get("text", "").strip()
        telegram_id: int = msg["from"]["id"]
        first_name: str = msg["from"].get("first_name", "User")
        username: str = msg["from"].get("username", "")

        # Get or create user
        res = await db.execute(select(User).where(User.telegram_id == telegram_id))
        user = res.scalar_one_or_none()
        if not user:
            user = User(
                telegram_id=telegram_id,
                first_name=first_name,
                telegram_username=username,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

        # Route by command prefix
        command = text.split()[0].lower() if text else ""

        if command == "/start":
            await handle_start_command(telegram_id, first_name)
        elif command == "/help":
            await handle_help_command(telegram_id)
        elif command == "/track":
            await handle_track_command(telegram_id, user, text, db)
        elif command == "/rules":
            await handle_list_rules_command(telegram_id, user, db)
        elif command == "/delete":
            await handle_delete_command(telegram_id, user, text, db)
        else:
            await send_telegram_alert(telegram_id,"❓ Unrecognized command. Send /help to see what I can do.",)


bot_dispatcher = BotDispatcher()