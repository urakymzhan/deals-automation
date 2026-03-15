from models import TrackedItem, PriceHistory, Session, init_db
from scrapers import get_scraper
from notifiers import notify


def check_all_items():
    session = Session()
    items = session.query(TrackedItem).filter_by(active=True).all()

    for item in items:
        scraper = get_scraper(item.source)
        if not scraper:
            print(f"[Tracker] No scraper for source: {item.source}")
            continue

        result = scraper.scrape(item.url)
        if not result or result.price is None:
            print(f"[Tracker] Could not get price for: {item.name}")
            continue

        print(f"[Tracker] {item.name} — ${result.price:.2f}")

        # Save price snapshot
        snapshot = PriceHistory(item_id=item.id, price=result.price, title=result.title)
        session.add(snapshot)
        session.commit()

        # Check if price dropped below target
        if item.target_price and result.price <= item.target_price:
            notify(
                subject=f"Deal Alert: {item.name}",
                body=(
                    f"{result.title}\n"
                    f"Current price: ${result.price:.2f}\n"
                    f"Your target:   ${item.target_price:.2f}\n"
                    f"Link: {item.url}"
                ),
            )

    session.close()


if __name__ == "__main__":
    init_db()
    check_all_items()
