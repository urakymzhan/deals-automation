from flask import Flask, render_template, request
from models import HomeSearch, PropertySnapshot, Session, init_db

app = Flask(__name__)
init_db()


@app.route("/")
def index():
    session = Session()

    searches = session.query(HomeSearch).filter_by(active=True).order_by(HomeSearch.label).all()
    active_tab = request.args.get("tab", str(searches[0].id) if searches else "all")

    # Build listings query
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

    session.close()
    return render_template(
        "index.html",
        searches=searches,
        listings=listings,
        active_tab=active_tab,
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
