import httpx
from app.utils.config import settings

class SupabaseRESTClient:
    def __init__(self):
        self.url = f"{settings.SUPABASE_URL}/rest/v1"
        self.headers = {
            "apikey": settings.SUPABASE_KEY,
            "Authorization": f"Bearer {settings.SUPABASE_KEY}",
            "Content-Type": "application/json"
        }
        
    def get(self, table: str, params: dict = None):
        headers = self.headers.copy()
        headers["Prefer"] = "count=exact"
        with httpx.Client() as client:
            res = client.get(f"{self.url}/{table}", headers=headers, params=params)
            if res.status_code >= 400:
                raise Exception(f"Failed to fetch {table}: {res.text}")
            
            # Content-Range example: "0-14/156"
            content_range = res.headers.get("Content-Range")
            total = 0
            if content_range and "/" in content_range:
                try:
                    total = int(content_range.split("/")[-1])
                except (ValueError, IndexError):
                    total = 0
                    
            return {
                "data": res.json(),
                "total": total
            }
            
    def upsert(self, table: str, data: list):
        headers = self.headers.copy()
        headers["Prefer"] = "return=representation,resolution=merge-duplicates"
        with httpx.Client() as client:
            res = client.post(f"{self.url}/{table}", headers=headers, json=data)
            if res.status_code >= 400:
                raise Exception(f"Failed to upsert {table}: {res.text}")
            return res.json()

supabase = SupabaseRESTClient()
