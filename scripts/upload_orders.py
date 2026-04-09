"""
upload_orders.py
----------------
Reads mock_orders.json and uploads orders to RetailCRM and/or Supabase.
Usage:  python scripts/upload_orders.py
"""
import json
import os
from pathlib import Path


def load_mock_orders() -> list[dict]:
    """Load orders from the mock JSON file."""
    mock_path = Path(__file__).resolve().parent.parent / "mock_orders.json"
    with open(mock_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    orders = load_mock_orders()
    print(f"Loaded {len(orders)} orders from mock_orders.json")
    # TODO: implement upload logic in the next steps


if __name__ == "__main__":
    main()
