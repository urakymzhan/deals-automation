"""
CLI to add a tracked item to the database.

Usage:
    python add_item.py --name "PS5" --url "https://www.ebay.com/itm/..." --source ebay --target-price 400
"""
import argparse
from models import TrackedItem, Session, init_db


def main():
    parser = argparse.ArgumentParser(description="Add an item to track")
    parser.add_argument("--name", required=True, help="Friendly name for the item")
    parser.add_argument("--url", required=True, help="Product URL")
    parser.add_argument("--source", required=True, choices=["ebay", "amazon"], help="Site source")
    parser.add_argument("--target-price", type=float, default=None, help="Alert when price drops below this")
    args = parser.parse_args()

    init_db()
    session = Session()
    item = TrackedItem(
        name=args.name,
        url=args.url,
        source=args.source,
        target_price=args.target_price,
    )
    session.add(item)
    session.commit()
    print(f"Added: [{item.id}] {item.name} — target ${item.target_price}")
    session.close()


if __name__ == "__main__":
    main()
