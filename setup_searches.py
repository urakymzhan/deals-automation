"""
Run this once to populate home searches in the database.
Usage: python setup_searches.py
"""
from models import HomeSearch, Session, init_db

SEARCHES = [
    {"label": "Cicero flips",   "zip_code": "60804", "max_price": 300000},
    {"label": "Berwyn flips",   "zip_code": "60402", "max_price": 300000},
    {"label": "Maywood flips",  "zip_code": "60153", "max_price": 300000},
    {"label": "Harvey flips",   "zip_code": "60426", "max_price": 300000},
    {"label": "Oak Park flips", "zip_code": "60302", "max_price": 300000},
]

def main():
    init_db()
    session = Session()

    existing = {s.zip_code for s in session.query(HomeSearch).all()}

    added = 0
    for s in SEARCHES:
        if s["zip_code"] not in existing:
            session.add(HomeSearch(**s))
            added += 1
            print(f"Added: {s['label']} ({s['zip_code']})")
        else:
            print(f"Skipped (already exists): {s['label']} ({s['zip_code']})")

    session.commit()
    session.close()
    print(f"\nDone. {added} searches added.")

if __name__ == "__main__":
    main()
