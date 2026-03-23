"""
Run this once to populate home searches in the database.
Usage: python setup_searches.py

Active flag controls which searches run in the tracker.
Set active=False to register a zip without running it yet (saves API quota).
Upgrade RapidAPI plan before activating all zips.

API budget reminder:
  Free tier  = 100 req/month → ~25 active zips at weekly runs
  Basic tier = 500 req/month → ~125 active zips at weekly runs
"""
from models import HomeSearch, Session, init_db

SEARCHES = [

    # ── Chicago West Suburbs (HIGH ROI — active by default) ──────────────
    {"label": "Cicero",         "zip_code": "60804", "max_price": 300000, "active": True},
    {"label": "Berwyn",         "zip_code": "60402", "max_price": 300000, "active": True},
    {"label": "Maywood",        "zip_code": "60153", "max_price": 300000, "active": True},
    {"label": "Bellwood",       "zip_code": "60104", "max_price": 300000, "active": True},
    {"label": "Melrose Park",   "zip_code": "60160", "max_price": 300000, "active": True},
    {"label": "Stone Park",     "zip_code": "60165", "max_price": 300000, "active": True},
    {"label": "Broadview",      "zip_code": "60155", "max_price": 300000, "active": True},

    # ── Chicago South Suburbs (HIGH ROI — active by default) ─────────────
    {"label": "Harvey",         "zip_code": "60426", "max_price": 300000, "active": True},
    {"label": "Dolton",         "zip_code": "60419", "max_price": 300000, "active": True},
    {"label": "Calumet City",   "zip_code": "60409", "max_price": 300000, "active": True},
    {"label": "Lansing",        "zip_code": "60438", "max_price": 300000, "active": True},
    {"label": "Riverdale",      "zip_code": "60827", "max_price": 300000, "active": True},
    {"label": "Chicago Heights","zip_code": "60411", "max_price": 300000, "active": True},
    {"label": "Markham",        "zip_code": "60428", "max_price": 300000, "active": True},

    # ── Chicago Northwest Suburbs ─────────────────────────────────────────
    {"label": "Waukegan",       "zip_code": "60085", "max_price": 300000, "active": True},
    {"label": "North Chicago",  "zip_code": "60064", "max_price": 300000, "active": True},
    {"label": "Zion",           "zip_code": "60099", "max_price": 300000, "active": True},
    {"label": "Elgin",          "zip_code": "60120", "max_price": 300000, "active": True},
    {"label": "Aurora",         "zip_code": "60505", "max_price": 300000, "active": True},
    {"label": "Joliet",         "zip_code": "60432", "max_price": 300000, "active": True},

    # ── Oak Park / River Forest ───────────────────────────────────────────
    {"label": "Oak Park",       "zip_code": "60302", "max_price": 300000, "active": True},
    {"label": "Forest Park",    "zip_code": "60130", "max_price": 300000, "active": True},

    # ── Rockford Area ─────────────────────────────────────────────────────
    {"label": "Rockford",       "zip_code": "61101", "max_price": 300000, "active": False},
    {"label": "Rockford South", "zip_code": "61102", "max_price": 300000, "active": False},
    {"label": "Rockford East",  "zip_code": "61108", "max_price": 300000, "active": False},
    {"label": "Loves Park",     "zip_code": "61111", "max_price": 300000, "active": False},

    # ── Peoria Area ───────────────────────────────────────────────────────
    {"label": "Peoria",         "zip_code": "61603", "max_price": 300000, "active": False},
    {"label": "Peoria West",    "zip_code": "61604", "max_price": 300000, "active": False},
    {"label": "East Peoria",    "zip_code": "61611", "max_price": 300000, "active": False},

    # ── Springfield Area ──────────────────────────────────────────────────
    {"label": "Springfield",    "zip_code": "62702", "max_price": 300000, "active": False},
    {"label": "Springfield N",  "zip_code": "62702", "max_price": 300000, "active": False},

    # ── Champaign-Urbana ──────────────────────────────────────────────────
    {"label": "Champaign",      "zip_code": "61820", "max_price": 300000, "active": False},
    {"label": "Urbana",         "zip_code": "61801", "max_price": 300000, "active": False},

    # ── Quad Cities (IL side) ─────────────────────────────────────────────
    {"label": "Rock Island",    "zip_code": "61201", "max_price": 300000, "active": False},
    {"label": "Moline",         "zip_code": "61265", "max_price": 300000, "active": False},

    # ── Southern Illinois ─────────────────────────────────────────────────
    {"label": "East St. Louis", "zip_code": "62201", "max_price": 300000, "active": False},
    {"label": "Belleville",     "zip_code": "62220", "max_price": 300000, "active": False},
    {"label": "Decatur",        "zip_code": "62521", "max_price": 300000, "active": False},

]


def main():
    init_db()
    session = Session()

    existing = {s.zip_code for s in session.query(HomeSearch).all()}

    added = 0
    for s in SEARCHES:
        if s["zip_code"] not in existing:
            search = HomeSearch(
                label=s["label"],
                zip_code=s["zip_code"],
                max_price=s.get("max_price"),
                active=s.get("active", True),
            )
            session.add(search)
            added += 1
            status = "ACTIVE" if s.get("active", True) else "inactive"
            print(f"[{status}] Added: {s['label']} ({s['zip_code']})")
        else:
            print(f"Skipped (already exists): {s['label']} ({s['zip_code']})")

    session.commit()
    session.close()

    active = sum(1 for s in SEARCHES if s.get("active", True))
    print(f"\nDone. {added} searches added ({active} active, {len(SEARCHES)-active} inactive).")
    print(f"Estimated API usage: {active} req/run × 4 runs/month = {active*4} req/month")


if __name__ == "__main__":
    main()
