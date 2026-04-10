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
        result = supabase.get("orders", params={"select": "total,created_at,status,city,utm_source"})
        orders = result["data"]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")

    total_orders = len(orders)
    total_revenue = sum(order.get("total", 0.0) or 0.0 for order in orders)
    
    orders_per_day = defaultdict(int)
    revenue_per_day = defaultdict(float)
    status_counts = defaultdict(int)
    city_counts = defaultdict(int)
    source_counts = defaultdict(int)

    for order in orders:
        # Timeline stats
        created_at = order.get("created_at")
        if created_at:
            day = created_at[:10]
            orders_per_day[day] += 1
            revenue_per_day[day] += float(order.get("total", 0.0) or 0.0)
        
        # Insights stats
        st = order.get("status") or "new"
        status_counts[st] += 1
        
        ct = order.get("city") or "Не указан"
        city_counts[ct] += 1
        
        src = order.get("utm_source") or "Без метки"
        source_counts[src] += 1

    # Format timeline data
    chart_data = [{"date": d, "count": c} for d, c in sorted(orders_per_day.items())]
    revenue_chart_data = [{"date": d, "revenue": r} for d, r in sorted(revenue_per_day.items())]

    # Format insights data (Top 5 for efficiency)
    top_statuses = [{"name": k, "count": v} for k, v in sorted(status_counts.items(), key=lambda x: x[1], reverse=True)]
    top_cities = [{"name": k, "count": v} for k, v in sorted(city_counts.items(), key=lambda x: x[1], reverse=True)]
    top_sources = [{"name": k, "count": v} for k, v in sorted(source_counts.items(), key=lambda x: x[1], reverse=True)]

    return {
        "summary": {
            "total_orders": total_orders,
            "total_revenue": total_revenue
        },
        "orders_per_day": chart_data,
        "revenue_per_day": revenue_chart_data,
        "insights": {
            "statuses": top_statuses,
            "cities": top_cities,
            "sources": top_sources
        }
    }
