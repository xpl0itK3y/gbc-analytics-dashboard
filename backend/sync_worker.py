import time
import logging
import sys
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("sync_worker")

# Add the app directory to the path so we can import app.services
sys.path.append(os.getcwd())

from app.services.sync_service import OrderSyncService

POLL_INTERVAL = 10  # seconds (speeded up for real-time demo)

def run_sync_worker():
    """
    Main loop that triggers order synchronization every POLL_INTERVAL seconds.
    """
    logger.info(f"Starting background synchronization worker (Interval: {POLL_INTERVAL}s)...")
    service = OrderSyncService()
    
    while True:
        try:
            logger.info("Triggering periodic order sync...")
            count = service.sync_orders()
            logger.info(f"Sync cycle complete. {count} orders processed.")
        except Exception as e:
            logger.error(f"Error during synchronization cycle: {e}")
        
        logger.debug(f"Sleeping for {POLL_INTERVAL} seconds...")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    try:
        run_sync_worker()
    except KeyboardInterrupt:
        logger.info("Sync worker stopped manually.")
    except Exception as e:
        logger.critical(f"Sync worker crashed: {e}")
        sys.exit(1)
