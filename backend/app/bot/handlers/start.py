from app.bot import templates
from app.services.bot_service import send_telegram_alert


async def handle_start_command(telegram_id: int, first_name: str) -> None:
    """Handles the /start and /help commands."""
    await send_telegram_alert(
        telegram_id, templates.welcome_message(first_name)
    )