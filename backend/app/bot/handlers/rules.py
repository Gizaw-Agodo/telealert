from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.rule import AlertRule
from app.models.user import User
from app.services.bot_service import send_telegram_alert


async def handle_list_rules_command(
    telegram_id: int, user: User, db: AsyncSession
) -> None:
    """Handles the /rules command to list active alerts."""
    res = await db.execute(
        select(AlertRule)
        .options(selectinload(AlertRule.channel))
        .where(AlertRule.user_id == user.id, AlertRule.is_active == True)
    )
    rules = res.scalars().all()

    if not rules:
        await send_telegram_alert(
            telegram_id, 
            "ℹ️ You don't have any active tracking rules. Use /track to add one."
        )
        return

    lines = ["📋 <b>Your Active Rules:</b>\n"]
    for idx, rule in enumerate(rules, 1):
        lines.append(
            f"{idx}. <b>@{rule.channel.username}</b> → <code>{rule.keyword}</code> "
            f"(ID: <code>{rule.id}</code>)"
        )

    lines.append("\nTo remove a rule, send: <code>/delete &lt;rule_id&gt;</code>")
    
    await send_telegram_alert(telegram_id, "\n".join(lines))


async def handle_delete_command(
    telegram_id: int, user: User, text: str, db: AsyncSession
) -> None:
    """Handles the /delete command to remove an alert."""
    parts = text.split()
    if len(parts) < 2:
        await send_telegram_alert(
            telegram_id, 
            "⚠️ Usage: <code>/delete &lt;rule_id&gt;</code> (Find IDs via /rules)"
        )
        return

    rule_id = parts[1].strip()
    
    res = await db.execute(
        select(AlertRule).where(
            AlertRule.id == rule_id, 
            AlertRule.user_id == user.id
        )
    )
    rule: AlertRule | None = res.scalar_one_or_none()

    if not rule:
        await send_telegram_alert(telegram_id, "❌ Rule not found or it does not belong to you.")
        return

    await db.delete(rule)
    await db.commit()
    
    await send_telegram_alert(telegram_id, "🗑️ Rule successfully deleted.")