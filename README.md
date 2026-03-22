# Deals Automation

Tracks home deals in Chicago suburbs and sends weekly email digests for new listings under $300K. Built for house flipping research.

---

## Stack

- **Python 3.14.3** (via pyenv)
- **Flask** — web dashboard
- **SQLAlchemy** — ORM
- **PostgreSQL** (Neon.tech — free forever) / SQLite for local dev
- **Redfin via RapidAPI** — property listings (100 req/month free)
- **Gmail SMTP** — email notifications via App Password
- **GitHub Actions** — runs tracker every Monday at 8 AM UTC
- **Render.com** — hosts the web dashboard (free tier)

---

## Local Setup

### 1. Clone the repo
```bash
git clone https://github.com/urakymzhan/deals-automation.git
cd deals-automation
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create `.env` file
```bash
cp .env.example .env
```

Fill in `.env`:
```
DATABASE_URL=sqlite:///deals.db        # or your Neon PostgreSQL URL
NOTIFICATION_METHOD=email

EMAIL_FROM=ulanr92@gmail.com
EMAIL_TO=your@email.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx

RAPIDAPI_KEY=your_rapidapi_key
RAPIDAPI_HOST=redfin-com-data.p.rapidapi.com
```

> **Gmail App Password**: myaccount.google.com/apppasswords → Create → copy 16-char password

> **RapidAPI key**: rapidapi.com → subscribe to "Redfin Com Data" → copy key

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
# Open http://127.0.0.1:5000
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

| What | How often | Where |
|------|-----------|-------|
| Fetch new listings + email digest | Every Monday 8 AM UTC | GitHub Actions |
| Web dashboard | Always on | Render.com |

> **RapidAPI limit**: 100 requests/month free. 5 zip codes × weekly = ~20 req/month. Safe.

---

## Deployment

### Web dashboard → Render.com
- URL: **https://deals-web.onrender.com**
- Auto-deploys on every `git push`
- Spins down after 15 min inactivity (first load takes ~30s)

### Tracker → GitHub Actions
- Runs every Monday at 8 AM UTC automatically
- Can also trigger manually: GitHub repo → **Actions** → **Weekly Deal Tracker** → **Run workflow**

### Database → Neon.tech
- Free PostgreSQL, never expires
- dashboard: **console.neon.tech**

---

## Secrets & Environment Variables

Set these in both **GitHub Actions** (repo → Settings → Secrets) and **Render** (dashboard → Environment):

| Key | Description |
|-----|-------------|
| `DATABASE_URL` | Neon PostgreSQL connection string |
| `EMAIL_FROM` | Gmail address used to send |
| `EMAIL_TO` | Email to receive alerts |
| `GMAIL_APP_PASSWORD` | Gmail App Password (not your real password) |
| `RAPIDAPI_KEY` | RapidAPI key |
| `RAPIDAPI_HOST` | `redfin-com-data.p.rapidapi.com` |

---

## Tracked Areas

| Area | Zip | Max Price |
|------|-----|-----------|
| Cicero, IL | 60804 | $300,000 |
| Berwyn, IL | 60402 | $300,000 |
| Maywood, IL | 60153 | $300,000 |
| Harvey, IL | 60426 | $300,000 |
| Oak Park, IL | 60302 | $300,000 |

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
