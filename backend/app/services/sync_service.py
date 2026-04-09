import logging
import httpx
from typing import List, Dict, Any
from supabase import create_client, Client
from app.utils.config import settings

logger = logging.getLogger(__name__)

class OrderSyncService:
    def __init__(self):
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        self.retailcrm_url = settings.RETAILCRM_BASE_URL
        self.retailcrm_key = settings.RETAILCRM_API_KEY

    def fetch_recent_orders(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch recent orders from RetailCRM API v5.
        """
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.retailcrm_url}/orders",
                    params={
                        "apiKey": self.retailcrm_key,
                        "limit": limit
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                if not data.get("success"):
                    logger.error(f"RetailCRM API error: {data.get('errorMsg')}")
                    return []
                return data.get("orders", [])
        except httpx.HTTPError as exc:
            logger.error(f"HTTP error occurred while fetching from RetailCRM: {exc}")
            return []
        except Exception as exc:
            logger.error(f"Unexpected error while fetching from RetailCRM: {exc}")
            return []

    def transform_order_for_supabase(self, crm_order: Dict[str, Any]) -> Dict[str, Any]:
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
            "created_at": crm_order.get("createdAt")
        }

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
            result = self.supabase.table("orders").upsert(valid_orders).execute()
            count = len(result.data)
            logger.info(f"Successfully upserted {count} orders to Supabase.")
            return count
        except Exception as exc:
            logger.error(f"Error upserting to Supabase: {exc}")
            return 0

    def sync_orders(self) -> int:
        """
        Orchestration method: Fetch -> Transform -> Push
        """
        logger.info("Starting order sync from RetailCRM to Supabase...")
        crm_orders = self.fetch_recent_orders()
        if not crm_orders:
            logger.info("No orders received from RetailCRM during sync.")
            return 0
        
        transformed = [self.transform_order_for_supabase(order) for order in crm_orders]
        upserted_count = self.push_to_supabase(transformed)
        return upserted_count
