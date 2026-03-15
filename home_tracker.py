from models import HomeSearch, PropertySnapshot, Session, init_db
from scrapers.redfin import search_properties, parse_property
from notifiers import notify


def check_all_home_searches():
    session = Session()
    searches = session.query(HomeSearch).filter_by(active=True).all()

    for search in searches:
        print(f"[HomeTracker] Checking '{search.label}' — zip {search.zip_code}")

        props = search_properties(
            zip_code=search.zip_code,
            max_price=search.max_price,
            min_beds=search.min_beds,
            min_baths=search.min_baths,
        )

        if not props:
            print(f"[HomeTracker] No results for {search.zip_code}")
            continue

        # Get zpids we've already seen for this search
        seen_zpids = {
            r.zpid for r in session.query(PropertySnapshot.zpid)
            .filter_by(search_id=search.id).all()
        }

        new_listings = []
        for prop in props:
            parsed = parse_property(prop, search.id)

            # Filter by max price
            if search.max_price and parsed["price"] and parsed["price"] > search.max_price:
                continue

            # Filter by min beds
            if search.min_beds and parsed["beds"] and parsed["beds"] < search.min_beds:
                continue

            # Filter by min baths
            if search.min_baths and parsed["baths"] and parsed["baths"] < search.min_baths:
                continue

            # Filter by max days on market
            if search.max_days_on_market and parsed["days_on_market"]:
                if parsed["days_on_market"] > search.max_days_on_market:
                    continue

            snapshot = PropertySnapshot(**parsed)
            session.add(snapshot)

            if parsed["zpid"] not in seen_zpids:
                new_listings.append(parsed)

        session.commit()

        # Send a single digest email for all new listings
        if new_listings:
            lines = []
            for p in new_listings:
                price_str = f"${p['price']:,.0f}" if p["price"] else "N/A"
                beds = p["beds"] or "?"
                baths = p["baths"] or "?"
                sqft = f"{p['sqft']:,.0f} sqft" if p["sqft"] else "N/A"
                dom = f"{p['days_on_market']} days on market" if p["days_on_market"] is not None else ""
                lines.append(
                    f"{p['address']}\n"
                    f"  Price: {price_str} | {beds}bd/{baths}ba | {sqft} {dom}\n"
                    f"  {p['url']}\n"
                )

            notify(
                subject=f"Deal Digest [{search.label}]: {len(new_listings)} new listings",
                body="\n".join(lines),
            )

        print(f"[HomeTracker] {len(props)} listings found, {len(new_listings)} new.")

    session.close()


if __name__ == "__main__":
    init_db()
    check_all_home_searches()
