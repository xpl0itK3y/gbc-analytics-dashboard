from collections import defaultdict
from typing import Dict, Any
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
        orders = supabase.get("orders", params={"select": "total,created_at"})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")

    total_orders = len(orders)
    total_revenue = sum(order.get("total", 0.0) for order in orders)
    
    orders_per_day: Dict[str, int] = defaultdict(int)
    revenue_per_day: Dict[str, float] = defaultdict(float)
    for order in orders:
        created_at = order.get("created_at")
        if created_at:
            # Simple slice if created_at is ISO8601 format: YYYY-MM-DD HH:MM:SS...
            day = created_at[:10]
            orders_per_day[day] += 1
            revenue_per_day[day] += float(order.get("total", 0.0) or 0.0)

    # Format orders_per_day mapping into sorted list of dicts for frontend charts
    chart_data = [
        {"date": date, "count": count}
        for date, count in sorted(orders_per_day.items())
    ]

    revenue_chart_data = [
        {"date": date, "revenue": revenue}
        for date, revenue in sorted(revenue_per_day.items())
    ]

    return {
        "summary": {
            "total_orders": total_orders,
            "total_revenue": total_revenue
        },
        "orders_per_day": chart_data,
        "revenue_per_day": revenue_chart_data,
    }
