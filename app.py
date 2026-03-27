import json
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from supabase import create_client
from models import HomeSearch, PropertySnapshot, Session, init_db
from config import SUPABASE_URL, SUPABASE_ANON_KEY, FLASK_SECRET_KEY

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY
app.jinja_env.filters["fromjson"] = json.loads
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
init_db()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("index"))
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        try:
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
            session["user"] = {"id": res.user.id, "email": res.user.email}
            return redirect(url_for("index"))
        except Exception as e:
            flash(str(e), "error")
    return render_template("login.html", mode="login")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if "user" in session:
        return redirect(url_for("index"))
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        try:
            res = supabase.auth.sign_up({"email": email, "password": password})
            if res.user:
                session["user"] = {"id": res.user.id, "email": res.user.email}
                return redirect(url_for("index"))
            flash("Check your email to confirm your account.", "info")
        except Exception as e:
            flash(str(e), "error")
    return render_template("login.html", mode="signup")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@login_required
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
    elif sort == "arv_desc":
        listings.sort(key=lambda x: x[0].estimated_profit or float("-inf"), reverse=True)
    elif sort == "score_desc":
        listings.sort(key=lambda x: x[0].motivation_score or 0, reverse=True)

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


@app.route("/listing/<zpid>")
@login_required
def listing(zpid):
    session = Session()
    snapshot = (
        session.query(PropertySnapshot)
        .filter_by(zpid=zpid)
        .order_by(PropertySnapshot.recorded_at.desc())
        .first()
    )
    if not snapshot:
        session.close()
        return "Listing not found", 404
    search = session.query(HomeSearch).filter_by(id=snapshot.search_id).first()
    session.close()
    return render_template("listing.html", snapshot=snapshot, search=search)


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=8080)
