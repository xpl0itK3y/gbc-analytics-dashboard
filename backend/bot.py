import asyncio
import logging
import json
from pathlib import Path
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import httpx

from app.utils.config import settings

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("retailcrm_bot")

STATE_FILE = Path(__file__).resolve().parent / "data" / "bot_state.json"
POLL_INTERVAL = 60  # seconds between RetailCRM checks
THRESHOLD_TOTAL = 50000

def get_last_processed_id() -> int:
    """Read the last processed order ID from the state file."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r") as f:
                data = json.load(f)
                return data.get("last_order_id", 0)
        except Exception as e:
            logger.error(f"Failed to read state file: {e}")
    return 0

def save_last_processed_id(order_id: int):
    """Save the last processed order ID to the state file."""
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, "w") as f:
            json.dump({"last_order_id": order_id}, f)
    except Exception as e:
        logger.error(f"Failed to save state file: {e}")

async def fetch_high_value_orders(last_id: int):
    """
    Fetch ascending orders from RetailCRM that are > last_id.
    Filter for ones where the total sum > THRESHOLD_TOTAL.
    """
    new_high_value = []
    max_id_seen = last_id

    try:
        # We query RetailCRM for recent orders
        # Sorting by id ascending so we process oldest-first among the new ones
        url = f"{settings.RETAILCRM_BASE_URL}/orders"
        
        # httpx async client for async execution
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params={
                    "apiKey": settings.RETAILCRM_API_KEY,
                    "limit": 50,
                    # Optional: "filter[minId]": last_id  --> RetailCRM V5 doesn't natively support filter[minId] directly in all setups
                    # So we fetch the latest block and filter manually in python.
                },
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            if not data.get("success"):
                logger.error(f"RetailCRM API Error: {data.get('errorMsg')}")
                return [], max_id_seen
            
            orders = data.get("orders", [])
            
            # Sort orders by ID ascending to process chronologically
            orders_sorted = sorted(orders, key=lambda x: x.get("id", 0))

            for order in orders_sorted:
                order_id = order.get("id", 0)
                
                # Update high-water mark
                if order_id > max_id_seen:
                    max_id_seen = order_id
                
                # Check if it's genuinely new
                if order_id <= last_id:
                    continue
                
                # Compute total robustly
                total = order.get("totalSum")
                if total is None:
                    total = sum(
                        item.get("quantity", 1) * item.get("initialPrice", 0)
                        for item in order.get("items", [])
                    )

                if total > THRESHOLD_TOTAL:
                    new_high_value.append({
                        "id": order_id,
                        "number": order.get("number", str(order_id)),
                        "total": total
                    })
                    
    except Exception as e:
        logger.error(f"Error fetching orders from RetailCRM: {e}")

    return new_high_value, max_id_seen

async def ping_bot_task():
    """Main background loop polling the API."""
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        logger.error("Telegram token or Chat ID is missing! Exiting...")
        return

    logger.info("Starting up Telegram RetailCRM Notifier Bot...")
    
    # Initialize Aiogram Bot
    bot = Bot(
        token=settings.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    last_processed_id = get_last_processed_id()
    
    # NEW: If starting for the first time, fetch current max ID to avoid historical spam
    if last_processed_id == 0:
        logger.info("First run detected. Initializing state with current latest order to skip history...")
        _, current_max = await fetch_high_value_orders(0)
        last_processed_id = current_max
        save_last_processed_id(last_processed_id)

    logger.info(f"Resuming from last_order_id: {last_processed_id}")

    try:
        while True:
            logger.debug("Checking for new orders...")
            orders, new_max_id = await fetch_high_value_orders(last_processed_id)
            
            for o in orders:
                number = o["number"]
                total = "{:,.0f}".format(o["total"])
                
                text = f"New high-value order: {number} — {total} ₸"
                
                try:
                    await bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=text)
                    logger.info(f"Notification sent for order {number} ({total} ₸)")
                except Exception as e:
                    logger.error(f"Failed to send Telegram message for order {number}: {e}")
            
            # Update state if new orders have appeared
            if new_max_id > last_processed_id:
                last_processed_id = new_max_id
                save_last_processed_id(last_processed_id)
            
            await asyncio.sleep(POLL_INTERVAL)
            
    except asyncio.CancelledError:
        logger.info("Polling task cancelled. Shutting down gracefully...")
    finally:
        # Proper session closure required by aiogram v3
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(ping_bot_task())
    except KeyboardInterrupt:
        logger.info("Bot manually stopped.")
