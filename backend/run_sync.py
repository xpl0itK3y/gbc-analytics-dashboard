import logging
import sys

from app.services.sync_service import OrderSyncService


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def main() -> int:
    service = OrderSyncService()
    synced_count = service.sync_orders()

    if synced_count <= 0:
        logging.error("Sync finished without new or updated orders.")
        return 1

    logging.info("Sync completed successfully. Upserted %d orders.", synced_count)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
