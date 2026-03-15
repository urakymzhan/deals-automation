"""
CLI to add a home search to the database.

Usage:
    python add_home_search.py --label "Chicago flips" --zip 60614 --max-price 300000 --min-beds 3
"""
import argparse
from models import HomeSearch, Session, init_db


def main():
    parser = argparse.ArgumentParser(description="Add a home search to track")
    parser.add_argument("--label", required=True, help="Friendly name, e.g. 'Chicago flips'")
    parser.add_argument("--zip", required=True, help="Zip code to search")
    parser.add_argument("--max-price", type=float, default=None, help="Max listing price")
    parser.add_argument("--min-beds", type=int, default=None, help="Minimum bedrooms")
    parser.add_argument("--min-baths", type=float, default=None, help="Minimum bathrooms")
    parser.add_argument("--max-dom", type=int, default=None, help="Max days on market (skip stale listings)")
    args = parser.parse_args()

    init_db()
    session = Session()
    search = HomeSearch(
        label=args.label,
        zip_code=args.zip,
        max_price=args.max_price,
        min_beds=args.min_beds,
        min_baths=args.min_baths,
        max_days_on_market=args.max_dom,
    )
    session.add(search)
    session.commit()
    print(f"Added home search [{search.id}]: {search.label} | zip {search.zip_code} | max ${search.max_price}")
    session.close()


if __name__ == "__main__":
    main()
