import asyncio
from typing import TypedDict

class QueueMessagePayload(TypedDict):
    channel_username: str
    channel_id: int
    message_id: int
    text: str

message_queue: asyncio.Queue[QueueMessagePayload] = asyncio.Queue()