from app.bot import templates
from app.services.bot_service import send_telegram_alert


async def handle_help_command(telegram_id: int) -> None:
    """Handles the /help command to show usage instructions."""
    await send_telegram_alert(
        telegram_id, 
        templates.help_message()
    )