from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.dispatcher import bot_dispatcher
from app.core.database import get_db_session

router = APIRouter(prefix="/webhook", tags=["Webhook"])


@router.post("/telegram", status_code=status.HTTP_200_OK)
async def telegram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    """Receives Telegram updates and processes them asynchronously."""
    try:
        update = await request.json()
    except Exception:
        return {"status": "ignored"}

    # Run command execution in the background so Telegram gets an instant 200 OK
    background_tasks.add_task(bot_dispatcher.dispatch, update, db)

    return {"status": "ok"}
