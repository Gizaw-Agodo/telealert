import os

from dotenv import load_dotenv
from telethon import TelegramClient, events

load_dotenv()

api_id = int(os.environ["TELEGRAM_API_ID"])
api_hash = os.environ["TELEGRAM_API_HASH"]

client = TelegramClient(
    "telealert_collector",
    api_id,
    api_hash,
)


@client.on(events.NewMessage)
async def handle_new_message(event):
    message = event.message

    print("=" * 60)
    print(f"Message ID: {message.id}")
    print(f"Chat ID: {event.chat_id}")
    print(f"Text: {message.text}")
    print("=" * 60)


async def main():
    print("Starting Telegram collector...")
    await client.start()
    print("Telegram collector connected.")
    await client.run_until_disconnected()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())