import os
from pathlib import Path
from dotenv import load_dotenv

# Try to load from project root first, then backend
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
ENV_PATHS = [
    PROJECT_ROOT / ".env",
    PROJECT_ROOT / "backend" / ".env",
]

for env_path in ENV_PATHS:
    if env_path.exists():
        load_dotenv(env_path)
        break

class Settings:
    RETAILCRM_SUBDOMAIN = os.getenv("RETAILCRM_SUBDOMAIN", "")
    RETAILCRM_API_KEY = os.getenv("RETAILCRM_API_KEY", "")
    RETAILCRM_BASE_URL = f"https://{RETAILCRM_SUBDOMAIN}.retailcrm.ru/api/v5"

    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

settings = Settings()
