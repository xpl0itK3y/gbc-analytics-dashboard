from collections import defaultdict
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from app.services.db import supabase

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/")
def get_stats() -> Dict[str, Any]:
    """
    Returns aggregated statistics:
    - total_orders
    - total_revenue
    - orders_per_day
    """
    try:
        # Fetch all necessary fields to calculate stats
        # For larger datasets, this should ideally be done natively in SQL/Supabase aggregations.
        response = supabase.table("orders").select("total, created_at").execute()
        orders = response.data
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")

    total_orders = len(orders)
    total_revenue = sum(order.get("total", 0.0) for order in orders)
    
    orders_per_day: Dict[str, int] = defaultdict(int)
    for order in orders:
        created_at = order.get("created_at")
        if created_at:
            # Simple slice if created_at is ISO8601 format: YYYY-MM-DD HH:MM:SS...
            day = created_at[:10]
            orders_per_day[day] += 1

    # Format orders_per_day mapping into sorted list of dicts for frontend charts
    chart_data = [
        {"date": date, "count": count}
        for date, count in sorted(orders_per_day.items())
    ]

    return {
        "summary": {
            "total_orders": total_orders,
            "total_revenue": total_revenue
        },
        "orders_per_day": chart_data
    }
