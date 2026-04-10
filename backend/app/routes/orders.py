from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from app.services.db import supabase

router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("/")
def get_orders(limit: int = 15, offset: int = 0, status: Optional[str] = None) -> Dict[str, Any]:
    """
    Returns a list of orders.
    Can filter by status and supports pagination via limit/offset.
    """
    try:
        query_params = {
            "select": "*",
            "order": "created_at.desc",
            "limit": limit,
            "offset": offset
        }
        if status:
            query_params["status"] = f"eq.{status}"
            
        result = supabase.get("orders", params=query_params)
        return {
            "orders": result["data"],
            "total": result["total"]
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")
