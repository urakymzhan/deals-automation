from flask import Flask, render_template, request
from models import HomeSearch, PropertySnapshot, Session, init_db

app = Flask(__name__)
init_db()


@app.route("/")
def index():
    session = Session()

    searches = session.query(HomeSearch).filter_by(active=True).order_by(HomeSearch.label).all()
    active_tab = request.args.get("tab", "all")
    sort = request.args.get("sort", "date")
    active_types = request.args.getlist("type")  # multi-value: ?type=Condo&type=Townhouse
    page = max(1, int(request.args.get("page", 1)))

    query = (
        session.query(PropertySnapshot, HomeSearch)
        .join(HomeSearch, PropertySnapshot.search_id == HomeSearch.id)
    )

    if active_tab != "all":
        query = query.filter(PropertySnapshot.search_id == int(active_tab))

    rows = query.order_by(PropertySnapshot.recorded_at.desc()).all()

    # Deduplicate by zpid — keep latest snapshot per property
    seen = set()
    listings = []
    for snapshot, search in rows:
        if snapshot.zpid not in seen:
            seen.add(snapshot.zpid)
            listings.append((snapshot, search))

    # Filter by property type (server-side, works across all pages)
    if active_types:
        listings = [(s, h) for s, h in listings if s.property_type in active_types]

    # Sort after deduplication
    if sort == "price_asc":
        listings.sort(key=lambda x: x[0].price or float("inf"))
    elif sort == "price_desc":
        listings.sort(key=lambda x: x[0].price or 0, reverse=True)
    elif sort == "dom_asc":
        listings.sort(key=lambda x: x[0].days_on_market if x[0].days_on_market is not None else float("inf"))
    elif sort == "dom_desc":
        listings.sort(key=lambda x: x[0].days_on_market if x[0].days_on_market is not None else -1, reverse=True)

    # Paginate
    per_page = 20
    total = len(listings)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = min(page, total_pages)
    listings = listings[(page - 1) * per_page: page * per_page]

    # Count unique listings per search (all listings, not filtered)
    all_rows = (
        session.query(PropertySnapshot, HomeSearch)
        .join(HomeSearch, PropertySnapshot.search_id == HomeSearch.id)
        .all()
    )
    seen_all = {}
    for snapshot, search in all_rows:
        if snapshot.zpid not in seen_all:
            seen_all[snapshot.zpid] = search.id
    counts = {}
    for zpid, sid in seen_all.items():
        counts[sid] = counts.get(sid, 0) + 1

    session.close()
    return render_template(
        "index.html",
        searches=searches,
        listings=listings,
        active_tab=active_tab,
        active_types=active_types,
        sort=sort,
        counts=counts,
        page=page,
        total_pages=total_pages,
        total=total,
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=8080)
