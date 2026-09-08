from pydantic import Field 
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv() 

class Settings(BaseSettings):
    
    # settings
    APP_NAME: str = "Tele Alert"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False)
    OPENAI_API_KEY:str = Field(default = "")
    OPENAI_MODEL_NAME: str = "gpt-3.5-turbo" 

    # --- Telegram Telethon & Bot Settings ---
    TELEGRAM_API_ID: int = Field(default=0, description="Telegram App API ID from my.telegram.org")
    TELEGRAM_API_HASH: str = Field(default="", description="Telegram App API Hash")
    BOT_TOKEN: str = Field(default="", description="Telegram Bot Token from BotFather for sending alerts")
    TELEGRAM_SESSION_NAME: str = Field(default="telealert_session", description="Name for the Telethon session file")
    TELEGRAM_SESSION_STRING: str = Field(default= "")

     # --- JWT Authentication Settings ---
    SECRET_KEY: str = Field(default = "",  description="Secret key for JWT token encoding/decoding.")
    ALGORITHM: str = "HS256" 
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 
    REFRESH_TOKEN_EXPIRE_DAYS: int = 15 


    # --- Database Settings ---
    DATABASE_URL: str = Field(default = "" , description="PostgreSQL database connection URL (e.g., postgresql+asyncpg://user:password@host:port/dbname)")

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

AVAILABLE_MATCH_TYPES: list[str] = [ "contains","exact","regex"]

settings = Settings()
