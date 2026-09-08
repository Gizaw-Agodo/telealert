def welcome_message(first_name: str) -> str:
    return (
        f"👋 Hello <b>{first_name}</b>!\n\n"
        "I monitor Telegram channels and alert you when specific keywords appear.\n\n"
        "Send <code>/help</code> to see what I can do."
    )


def help_message() -> str:
    return (
        "<b>Available Commands:</b>\n"
        "• <code>/track @channel keyword</code> — Monitor a channel for a keyword\n"
        "• <code>/rules</code> — View your active tracking rules\n"
        "• <code>/delete &lt;rule_id&gt;</code> — Remove an alert rule\n"
        "• <code>/help</code> — Show this guide\n\n"
        "<b>Example:</b>\n"
        "<code>/track @health_jobs midwifery</code>"
    )


def rule_created_message(channel: str, keyword: str) -> str:
    return f"✅ <b>Rule created!</b>\nWatching <b>@{channel}</b> for: <code>{keyword}</code>"


def rule_limit_reached(limit: int) -> str:
    return f"❌ Limit reached! You can track up to {limit} rules on the free plan."


def invalid_track_format() -> str:
    return (
        "⚠️ Invalid format.\n"
        "Usage: <code>/track @channel_username keyword</code>\n"
        "Example: <code>/track @health_jobs midwifery</code>"
    )