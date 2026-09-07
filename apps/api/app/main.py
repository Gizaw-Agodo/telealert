from fastapi import FastAPI

app = FastAPI(
    title="TeleAlert API",
    description="Telegram monitoring and alerting platform",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}