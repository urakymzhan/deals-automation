# Deals Automation

Tracks home deals in Chicago suburbs

---

## Setup

### 1. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create `.env` file

Fill in `.env`:

---

## Running Locally

### Add home searches (run once)
```bash
venv/bin/python3 setup_searches.py
```

### Fetch listings & send emails
```bash
venv/bin/python3 home_tracker.py
```

### Start web dashboard
```bash
venv/bin/python3 app.py
```

### Add a new zip code to track
```bash
venv/bin/python3 add_home_search.py \
  --label "My Area" \
  --zip 60614 \
  --max-price 300000 \
  --min-beds 3
```

---

## Periodic Schedule
> **API limit**: This is due to API limit hence runs weekly. 100 requests/month free. 5 zip codes × weekly = ~20 req/month.

---

## Deployment

### Web dashboard
- Auto-deploys on every `git push`

### Tracker → GitHub Actions
- Runs every Monday at 8 AM UTC automatically
- Can also trigger manually: GitHub repo → **Actions** → **Weekly Deal Tracker** → **Run workflow**

### Database
- Free PostgreSQL
- dashboard: **console.neon.tech**

---

## Secrets & Environment Variables

Set .env secrets in both **GitHub Actions** (repo → Settings → Secrets) and **Render** (dashboard → Environment):

---

## Re-enabling eBay/Amazon Tracking

Uncomment in `scheduler.py`:
```python
check_all_items()
```

Then add items:
```bash
venv/bin/python3 add_item.py \
  --name "PS5" \
  --url "https://www.ebay.com/itm/..." \
  --source ebay \
  --target-price 400
```

---

## Stack

- **Python 3.14.3**
- **Flask** - web
- **SQLAlchemy** — ORM
- **PostgreSQL** (Neon) / SQLite for local dev
- **Gmail SMTP**
- **GitHub Actions**