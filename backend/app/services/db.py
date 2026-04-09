from supabase import create_client, Client
from app.utils.config import settings

def get_supabase_client() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# Singleton initialized client for general use in routes
supabase: Client = get_supabase_client()
