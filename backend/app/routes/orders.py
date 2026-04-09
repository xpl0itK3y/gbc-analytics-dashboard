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
        query = supabase.table("orders").select("*").order("created_at", desc=True).limit(limit)
        
        if status:
            query = query.eq("status", status)
            
        response = query.execute()
        return response.data
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")
