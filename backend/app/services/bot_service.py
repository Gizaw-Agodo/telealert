import logging
import httpx
from app.core.config import settings
from typing import Any

logger = logging.getLogger(__name__)

async def send_telegram_alert(telegram_id: int, text: str) -> bool:
    """
    Sends a message to a user via the official Telegram Bot API.
    Returns True if successful, False otherwise.
    """
    
    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"

    payload: dict[str, Any] = {
        "chat_id": telegram_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload)
            response_data = response.json()
            
            if response.status_code == 200:
                return True
            
            # Handle specific Telegram errors
            error_msg = response_data.get("description", "Unknown error")
            if response.status_code == 403:
                logger.error(f"User {telegram_id} blocked the bot or hasn't started it.")
            else:
                logger.error(f"Telegram API Error: {error_msg}")
                
            return False
            
        except httpx.RequestError as exc:
            logger.error(f"HTTP Request failed while sending alert: {exc}")
            return False



async def setup_bot_commands() -> bool:
    """
    Registers the bot commands with Telegram. 
    This creates the auto-complete menu when users type '/'.
    """

    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/setMyCommands"
    
    # Define the commands and their short descriptions
    payload = {
        "commands": [
            {"command": "track", "description": "Monitor a channel for a keyword"},
            {"command": "rules", "description": "View your active tracking rules"},
            {"command": "delete", "description": "Remove an alert rule"},
            {"command": "help", "description": "Show usage instructions"}
        ]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                logger.info("✅ Bot commands registered successfully with Telegram.")
                return True
            
            logger.error(f"Failed to register bot commands: {response.text}")
            return False
            
        except httpx.RequestError as exc:
            logger.error(f"HTTP Request failed while setting commands: {exc}")
            return False