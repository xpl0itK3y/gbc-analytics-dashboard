from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from app.services.db import supabase

router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("/")
def get_orders(limit: int = 100, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Returns a list of orders.
    Can filter by status.
    """
    try:
        params = {
            "select": "*",
            "order": "created_at.desc",
            "limit": limit
        }
        if status:
            params["status"] = f"eq.{status}"
            
        return supabase.get("orders", params=params)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")
