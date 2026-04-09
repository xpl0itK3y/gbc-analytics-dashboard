"""
upload_orders.py
================
Reads mock_orders.json and uploads each order to RetailCRM via API v5.

Endpoint : POST /api/v5/orders/create
Auth     : apiKey query-parameter
Payload  : application/x-www-form-urlencoded  (order = JSON string)

Features:
  - Automatic retries with exponential back-off (3 attempts)
  - Per-order error handling — one failure doesn't stop the batch
  - Structured logging with timestamps
  - Dry-run mode (--dry-run) to preview payloads without sending
  - Summary report at the end

Usage:
  python scripts/upload_orders.py              # upload all 50 orders
  python scripts/upload_orders.py --dry-run    # preview without sending
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Walk up to project root to locate .env (works from scripts/ or project root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATHS = [
    PROJECT_ROOT / ".env",
    PROJECT_ROOT / "backend" / ".env",
]

for env_path in ENV_PATHS:
    if env_path.exists():
        load_dotenv(env_path)
        break

RETAILCRM_SUBDOMAIN = os.getenv("RETAILCRM_SUBDOMAIN", "")
RETAILCRM_API_KEY = os.getenv("RETAILCRM_API_KEY", "")
RETAILCRM_BASE_URL = f"https://{RETAILCRM_SUBDOMAIN}.retailcrm.ru/api/v5"
MOCK_FILE = PROJECT_ROOT / "mock_orders.json"

# Retry settings
MAX_RETRIES = 3
BACKOFF_FACTOR = 1.5  # seconds: 1.5 → 2.25 → 3.375

# HTTP timeout (connect / read)
TIMEOUT = httpx.Timeout(10.0, read=30.0)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("upload_orders")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_mock_orders(path: Path = MOCK_FILE) -> list[dict[str, Any]]:
    """Load and return the list of orders from the mock JSON file."""
    logger.info("Loading orders from %s", path)
    with open(path, "r", encoding="utf-8") as f:
        orders = json.load(f)
    logger.info("Loaded %d orders", len(orders))
    return orders


def build_retailcrm_payload(order: dict[str, Any]) -> dict[str, Any]:
    """
    Transform a mock order dict into the RetailCRM-compatible order object.

    RetailCRM expects the `order` POST parameter to be a JSON *string*
    containing fields like firstName, lastName, phone, items, delivery, etc.
    """
    # Calculate total from line items:  quantity × initialPrice
    total = sum(
        item.get("quantity", 1) * item.get("initialPrice", 0)
        for item in order.get("items", [])
    )

    retailcrm_order: dict[str, Any] = {
        "firstName": order.get("firstName", ""),
        "lastName": order.get("lastName", ""),
        "phone": order.get("phone", ""),
        "email": order.get("email", ""),
        "orderType": order.get("orderType", "eshop-individual"),
        "orderMethod": order.get("orderMethod", "shopping-cart"),
        "status": order.get("status", "new"),
        "items": [
            {
                "productName": item["productName"],
                "quantity": item.get("quantity", 1),
                "initialPrice": item.get("initialPrice", 0),
            }
            for item in order.get("items", [])
        ],
        "delivery": order.get("delivery", {}),
        "customFields": order.get("customFields", {}),
    }

    return retailcrm_order


def send_order(
    client: httpx.Client,
    order_payload: dict[str, Any],
    index: int,
    dry_run: bool = False,
) -> bool:
    """
    POST a single order to RetailCRM with retries.

    Returns True on success, False on failure.
    """
    customer_name = (
        f"{order_payload.get('firstName', '')} {order_payload.get('lastName', '')}"
    ).strip()

    if dry_run:
        logger.info(
            "[DRY-RUN] Order #%d (%s) — payload preview:\n%s",
            index,
            customer_name,
            json.dumps(order_payload, ensure_ascii=False, indent=2),
        )
        return True

    # RetailCRM expects form-urlencoded: order=<json-string>
    form_data = {"order": json.dumps(order_payload, ensure_ascii=False)}

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.post(
                f"{RETAILCRM_BASE_URL}/orders/create",
                data=form_data,
                params={"apiKey": RETAILCRM_API_KEY},
                timeout=TIMEOUT,
            )

            # RetailCRM returns 2xx with {"success": true/false}
            body = response.json()

            if response.status_code == 201 or body.get("success"):
                order_id = body.get("id", "N/A")
                logger.info(
                    "✅  Order #%d (%s) → created (CRM id: %s)",
                    index,
                    customer_name,
                    order_id,
                )
                return True

            # API-level error (e.g. validation)
            errors = body.get("errors", body.get("errorMsg", "unknown"))
            logger.warning(
                "⚠️  Order #%d (%s) — API error (attempt %d/%d): %s",
                index,
                customer_name,
                attempt,
                MAX_RETRIES,
                errors,
            )

        except httpx.TimeoutException:
            logger.warning(
                "⏱  Order #%d (%s) — timeout (attempt %d/%d)",
                index,
                customer_name,
                attempt,
                MAX_RETRIES,
            )
        except httpx.HTTPError as exc:
            logger.warning(
                "🌐  Order #%d (%s) — HTTP error (attempt %d/%d): %s",
                index,
                customer_name,
                attempt,
                MAX_RETRIES,
                exc,
            )
        except Exception as exc:
            logger.error(
                "💥  Order #%d (%s) — unexpected error (attempt %d/%d): %s",
                index,
                customer_name,
                attempt,
                MAX_RETRIES,
                exc,
            )

        # Exponential back-off before next retry
        if attempt < MAX_RETRIES:
            wait = BACKOFF_FACTOR ** attempt
            logger.info("    ↳ retrying in %.1fs …", wait)
            time.sleep(wait)

    logger.error("❌  Order #%d (%s) — FAILED after %d attempts", index, customer_name, MAX_RETRIES)
    return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Upload mock orders to RetailCRM API v5",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview payloads without sending to RetailCRM",
    )
    args = parser.parse_args()

    # ── Validate configuration ────────────────────────────────────────────
    if not args.dry_run:
        if not RETAILCRM_SUBDOMAIN:
            logger.error("RETAILCRM_SUBDOMAIN is not set. Check your .env file.")
            sys.exit(1)
        if not RETAILCRM_API_KEY:
            logger.error("RETAILCRM_API_KEY is not set. Check your .env file.")
            sys.exit(1)
        logger.info("Target CRM: %s", RETAILCRM_BASE_URL)

    # ── Load orders ───────────────────────────────────────────────────────
    orders = load_mock_orders()

    if not orders:
        logger.warning("No orders found — nothing to do.")
        return

    # ── Upload loop ───────────────────────────────────────────────────────
    succeeded = 0
    failed = 0

    with httpx.Client() as client:
        for idx, raw_order in enumerate(orders, start=1):
            payload = build_retailcrm_payload(raw_order)
            ok = send_order(client, payload, idx, dry_run=args.dry_run)
            if ok:
                succeeded += 1
            else:
                failed += 1

            # Small delay between requests to respect rate limits
            if not args.dry_run and idx < len(orders):
                time.sleep(0.3)

    # ── Summary ───────────────────────────────────────────────────────────
    logger.info("─" * 50)
    logger.info(
        "Done.  Total: %d  |  ✅ Succeeded: %d  |  ❌ Failed: %d",
        len(orders),
        succeeded,
        failed,
    )
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
