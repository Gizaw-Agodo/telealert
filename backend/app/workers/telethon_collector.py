import logging
from telethon import TelegramClient, events # type: ignore  
from telethon.sessions import StringSession # type: ignore  

from app.core.config import settings
from app.core.shared_queue import QueueMessagePayload, message_queue

logger = logging.getLogger(__name__)

client = TelegramClient(
    StringSession(settings.TELEGRAM_SESSION_STRING),
    settings.TELEGRAM_API_ID,
    settings.TELEGRAM_API_HASH,
)

async def start_telethon_client() -> None:
    """Starts the Telethon client and registers the event listener."""
    logger.info("Starting Telethon collector...")
    await client.start() # type: ignore  
    logger.info("✅ Telethon client connected and listening.")

@client.on(events.NewMessage())
async def handle_new_message(event: events.NewMessage.Event) -> None:
    if not event.is_channel:
        return

    chat = await event.get_chat()  # type: ignore  
    
    # Safely extract username (Telethon entities dynamically assign this)
    raw_username = getattr(chat, "username", None) # type: ignore  
    channel_username: str = str(raw_username) if raw_username else str(getattr(chat, "id", "")) # type: ignore  
    
    text: str = getattr(event.message, "message", "") # type: ignore  

    if not text:
        return

    payload: QueueMessagePayload = {
        "channel_username": channel_username.lower(),
        "channel_id": getattr(chat, "id", 0), # type: ignore  
        "message_id": getattr(event.message, "id", 0), # type: ignore  
        "text": text,
    }

    await message_queue.put(payload)