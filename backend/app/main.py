from contextlib import asynccontextmanager
from typing import AsyncGenerator
import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
import logging

from app.core.config import settings
from app.core.database import engine,create_db_and_tables
from app.api.routes import users, rules, webhook

from app.workers.telethon_collector import start_telethon_client, client as telethon_client
from app.workers.matcher import process_queue
from app.workers.telethon_collector import start_telethon_client
from app.services.bot_service import setup_bot_commands

logging.basicConfig(level=logging.INFO,format="%(levelname)s - %(message)s",)

# 2. Silence the HTTP libraries to prevent token leaks
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    
    # ---------------- STARTUP ----------------
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}...")

    # 1. Verify Database Connection
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        print("✅ Database connection established successfully.")
    except Exception as exc:
        print(f"❌ Failed to connect to the database: {exc}")
        raise exc

    # 2. Optional: Create tables automatically for local development
    if settings.DEBUG:
        await create_db_and_tables()
        print("🛠️  Development mode: Database tables verified/created.")

    # 2. CONFIGURE TELEGRAM BOT UI
    await setup_bot_commands()

    await start_telethon_client()
    
    # Start the infinite matcher loop as an asyncio background task
    matcher_task = asyncio.create_task(process_queue())
    print("✅ Matcher background task running.")

    yield

    # 3. GRACEFUL SHUTDOWN
    print("🛑 Shutting down application...")
    
    # Cancel the infinite matcher loop
    matcher_task.cancel()
    
    # Disconnect the Telethon client
    if telethon_client.is_connected():
        await telethon_client.disconnect()  # type: ignore
        print("🔌 Telethon client disconnected.")
        
    # Close database connections
    await engine.dispose()
    print("🔌 Database engine closed.")

    # ---------------- SHUTDOWN ----------------
    print("🛑 Shutting down application...")
    await engine.dispose()
    print("🔌 Database engine connections closed.")


# Initialize FastAPI instance
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api/v1")
app.include_router(rules.router, prefix="/api/v1")
app.include_router(webhook.router, prefix="/api/v1")


# Root Healthcheck Route
@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
