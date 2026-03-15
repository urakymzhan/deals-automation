# Deals Automation

A deal tracking tool with two modes:
1. **Home deals** (active) — monitors Redfin listings by zip code and sends a daily digest email for new properties
2. **Product deals** (paused) — tracks eBay/Amazon prices and alerts when they drop below a target price

## Project Structure

```
deals-automation/
├── venv/                       # Python virtual environment (Python 3.14.3)
├── scrapers/
│   ├── __init__.py             # get_scraper() factory for product scrapers
│   ├── base.py                 # BaseScraper + ScrapeResult dataclass
│   ├── ebay.py                 # eBay scraper (Playwright)
│   ├── amazon.py               # Amazon scraper (requests + BeautifulSoup)
│   └── redfin.py               # Redfin property search via RapidAPI
├── models/
│   ├── __init__.py
│   └── database.py             # SQLAlchemy models: TrackedItem, PriceHistory, HomeSearch, PropertySnapshot
├── notifiers/
│   ├── __init__.py             # notify() — routes to email or SMS
│   ├── email_notifier.py       # Gmail SMTP via App Password
│   └── sms_notifier.py         # Twilio SMS
├── tracker.py                  # Product tracker (eBay/Amazon) — currently paused
├── home_tracker.py             # Home deals tracker — sends digest email for new listings
├── scheduler.py                # Runs home_tracker daily at 8:00 AM
├── add_item.py                 # CLI to add a product to track
├── add_home_search.py          # CLI to add a zip code home search
├── config.py                   # All settings loaded from .env
├── .env                        # Credentials (never commit)
├── .env.example                # Credentials template
└── requirements.txt
```

## Key Concepts

- **HomeSearch**: a zip code + criteria (max price, min beds/baths) to monitor on Redfin
- **PropertySnapshot**: every property seen per check — used to detect new listings
- **Home tracker**: on each run, fetches listings, compares to seen properties, sends one digest email for new ones
- **TrackedItem**: a product URL + target price (eBay/Amazon) — paused for now
- **Notifier**: `notify(subject, body)` routes to Gmail SMTP (email) or Twilio (SMS) based on `NOTIFICATION_METHOD`

## Running

```bash
# Add a home search
venv/bin/python3 add_home_search.py --label "Chicago flips" --zip 60614 --max-price 300000 --min-beds 3

# One-time home check
venv/bin/python3 home_tracker.py

# Start scheduler (runs immediately + daily at 8 AM)
venv/bin/python3 scheduler.py

# Add a product to track (when re-enabled)
venv/bin/python3 add_item.py --name "PS5" --url "https://www.ebay.com/itm/..." --source ebay --target-price 400
```

## Enabling/Disabling Product Tracking

In `scheduler.py`, uncomment this line to re-enable eBay/Amazon tracking:
```python
# check_all_items()  # uncomment to enable eBay/Amazon tracking
```

## Adding a New Home Search Area

```bash
venv/bin/python3 add_home_search.py \
  --label "Lincoln Park" \
  --zip 60614 \
  --max-price 400000 \
  --min-beds 3 \
  --min-baths 2 \
  --max-dom 60
```

## Stack

- Python 3.14.3 (via pyenv)
- SQLite + SQLAlchemy
- Playwright (eBay scraping)
- requests + BeautifulSoup4 (Amazon scraping)
- RapidAPI — Redfin (`redfin-com-data.p.rapidapi.com`) — 100 requests/month free tier
- APScheduler (daily cron at 8 AM)
- Gmail SMTP with App Password (email notifications)
- Twilio (SMS — available but not active)

## API Limits

- **RapidAPI Redfin**: 100 requests/month — scheduler runs once daily (~30 requests/month)
