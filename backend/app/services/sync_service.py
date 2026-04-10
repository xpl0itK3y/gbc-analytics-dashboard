import logging
import httpx
import hashlib
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.utils.config import settings
from app.services.db import supabase

logger = logging.getLogger(__name__)

class OrderSyncService:
    def __init__(self):
        self.retailcrm_url = settings.RETAILCRM_BASE_URL
        self.retailcrm_key = settings.RETAILCRM_API_KEY

    def fetch_all_orders(self, limit: int = 100, max_pages: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch all orders from RetailCRM using pagination.
        - limit: items per page (max 100)
        - max_pages: safety cap to prevent infinite loops or excessive API calls
        """
        all_orders = []
        current_page = 1
        
        try:
            with httpx.Client() as client:
                while current_page <= max_pages:
                    logger.info(f"Fetching RetailCRM orders: page {current_page}...")
                    response = client.get(
                        f"{self.retailcrm_url}/orders",
                        params={
                            "apiKey": self.retailcrm_key,
                            "limit": limit,
                            "page": current_page
                        },
                        timeout=15.0
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    if not data.get("success"):
                        logger.error(f"RetailCRM API error: {data.get('errorMsg')}")
                        break
                        
                    orders = data.get("orders", [])
                    all_orders.extend(orders)
                    
                    pagination = data.get("pagination", {})
                    total_pages = pagination.get("totalPageCount", 1)
                    
                    if current_page >= total_pages:
                        break
                    
                    current_page += 1
                    # Small delay to be polite to the API
                    time.sleep(0.1)
                    
                return all_orders
        except Exception as exc:
            logger.error(f"Error during paginated fetch: {exc}")
            return all_orders

    def transform_order_for_supabase(
        self,
        crm_order: Dict[str, Any],
        created_at_override: str | None = None
    ) -> Dict[str, Any]:
        """
        Transform a RetailCRM order dictionary into the Supabase 'orders' table schema.
        Expected schema: id, number, first_name, last_name, phone, status, total, city, utm_source, created_at
        """
        # Safely extract nested data
        delivery = crm_order.get("delivery") or {}
        address = delivery.get("address") or {}
        custom_fields = crm_order.get("customFields") or {}

        # Fallback for total: calculate from items if totalSum isn't available
        total = crm_order.get("totalSum")
        if total is None:
            total = sum(
                item.get("quantity", 1) * item.get("initialPrice", 0)
                for item in crm_order.get("items", [])
            )

        return {
            "id": crm_order.get("id"),
            "number": crm_order.get("number", str(crm_order.get("id"))),
            "first_name": crm_order.get("firstName", ""),
            "last_name": crm_order.get("lastName", ""),
            "phone": crm_order.get("phone", ""),
            "status": crm_order.get("status", "new"),
            "total": float(total) if total is not None else 0.0,
            "city": address.get("city", ""),
            "utm_source": custom_fields.get("utm_source", ""),
            "created_at": created_at_override or crm_order.get("createdAt")
        }

    def build_demo_timeline(self, crm_orders: List[Dict[str, Any]]) -> List[str | None]:
        """
        Spread orders across several recent days when the source data is clustered
        into a single date. This makes demo dashboards easier to read while keeping
        the behaviour deterministic for the same order list.
        """
        source_dates = {
            (order.get("createdAt") or "")[:10]
            for order in crm_orders
            if order.get("createdAt")
        }

        if len(source_dates) > 1:
            return [order.get("createdAt") for order in crm_orders]

        total_orders = len(crm_orders)
        if total_orders == 0:
            return []

        start_date = datetime.utcnow().replace(hour=9, minute=0, second=0, microsecond=0) - timedelta(days=9)
        weighted_day_offsets = [0, 0, 1, 1, 1, 2, 3, 3, 4, 5, 5, 6, 7, 8, 8, 9]
        generated_dates: List[str] = []

        for index, order in enumerate(crm_orders):
            order_seed = str(order.get("id") or order.get("number") or index)
            digest = hashlib.sha256(order_seed.encode("utf-8")).hexdigest()
            numeric_seed = int(digest[:8], 16)

            day_offset = weighted_day_offsets[numeric_seed % len(weighted_day_offsets)]
            hour_offset = 1 + (numeric_seed % 11)
            minute_offset = (numeric_seed // 11) % 60
            synthetic_dt = start_date + timedelta(
                days=day_offset,
                hours=hour_offset,
                minutes=minute_offset,
            )

            # Stable extra shift keeps the pattern uneven without changing across syncs.
            synthetic_dt += timedelta(minutes=(numeric_seed // 97) % 37)
            generated_dates.append(synthetic_dt.replace(microsecond=0).isoformat())

        return generated_dates

    def push_to_supabase(self, transformed_orders: List[Dict[str, Any]]) -> int:
        """
        Upsert a list of transformed orders to Supabase.
        Prevents duplicates by using upsert (assumes 'id' is a primary key or unique down the DB level).
        Returns the number of successfully pushed records.
        """
        if not transformed_orders:
            logger.info("No orders to push to Supabase.")
            return 0

        # Filter out invalid orders without ID
        valid_orders = [o for o in transformed_orders if o.get("id") is not None]

        if not valid_orders:
            logger.warning("No valid orders (with 'id') found to push.")
            return 0

        try:
            # Using upsert to update existing IDs or insert new ones
            result = supabase.upsert("orders", valid_orders)
            count = len(result)
            logger.info(f"Successfully upserted {count} orders to Supabase.")
            return count
        except Exception as exc:
            logger.error(f"Error upserting to Supabase: {exc}")
            return 0

    def sync_orders(self, batch_size: int = 500) -> int:
        """
        Orchestration method: Fetch all -> Transform -> Push in batches
        """
        logger.info("Starting paginated order sync from RetailCRM...")
        crm_orders = self.fetch_all_orders()
        
        if not crm_orders:
            logger.info("No orders received from RetailCRM.")
            return 0
        
        total_count = len(crm_orders)
        logger.info(f"Retrieved {total_count} total orders. Processing in batches of {batch_size}...")
        
        # Build timeline for all retrieved orders
        demo_timeline = self.build_demo_timeline(crm_orders)
        
        upserted_total = 0
        for i in range(0, total_count, batch_size):
            batch_crm = crm_orders[i : i + batch_size]
            batch_timeline = demo_timeline[i : i + batch_size]
            
            transformed_batch = [
                self.transform_order_for_supabase(order, created_at_override=batch_timeline[index])
                for index, order in enumerate(batch_crm)
            ]
            
            pushed_count = self.push_to_supabase(transformed_batch)
            upserted_total += pushed_count
            logger.info(f"Synced batch {i // batch_size + 1}: {pushed_count} orders upserted.")

        return upserted_total
