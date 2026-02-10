from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent

class Settings(BaseSettings):
    BOT_TOKEN: str
    GEMINI_API_KEY: str
    ENVIRONMENT: str = "development"
    DB_NAME: str = "bot.db"
    
    class Config:
        env_file = BASE_DIR / ".env.local" if (BASE_DIR / ".env.local").exists() else BASE_DIR / ".env"

# ایجاد instance
settings = Settings()