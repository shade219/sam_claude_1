# Daily Digest

A self-hosted web app that curates a ranked daily reading list from across the internet for topics you care about. Articles are fetched from The Guardian and GNews, scored by recency, source trust, and popularity, then presented in a clean browser UI that refreshes automatically every day.

---

## Features

- **Multi-source fetching** — The Guardian API and GNews API (Reddit support planned)
- **Relevance filtering** — Off-topic articles are dropped before storage using per-topic keyword gates
- **Scored ranking** — Articles ranked by recency (40%), source trust (30%), and popularity (30%)
- **Daily auto-refresh** — APScheduler triggers a fetch at a configurable UTC hour
- **Clean web UI** — Topic tabs, score bars, trust indicators, and relative timestamps
- **Zero infrastructure** — SQLite database, no external services required

---

## Quick Start

### 1. Clone and set up the environment

```bash
git clone git@github.com:shade219/sam_claude_1.git
cd sam_claude_1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API keys

Copy the example env file and fill in your keys:

```bash
cp .env.example .env   # then edit .env
```

| Key | Where to get it |
|---|---|
| `GUARDIAN_API_KEY` | [open.platform.theguardian.com](https://open.platform.theguardian.com/access/support/applications) — free, instant |
| `GNEWS_API_KEY` | [gnews.io/register](https://gnews.io/register) — free tier, 100 req/day |

### 3. Run

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open `http://localhost:8000` in your browser. Click **Refresh** to fetch your first batch of articles.

---

## Configuration

All settings live in `config.py`:

```python
# Topics to track
TOPICS = ["AI", "climate", "space", "cybersecurity"]

# Number of articles shown per topic
TOP_N = 10

# UTC hour for the daily automatic refresh (24h clock)
REFRESH_HOUR = 7

# Source trust scores — domains not listed default to 0.5
TRUSTED_DOMAINS = {
    "theguardian.com": 1.0,
    "reuters.com": 0.9,
    ...
}
```

To add a new topic, add it to `TOPICS` and extend `TOPIC_KEYWORDS`, `TOPIC_GUARDIAN_SECTIONS`, and `TOPIC_GUARDIAN_QUERIES` with appropriate values.

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Serves the digest UI |
| `GET` | `/api/topics` | List of configured topics |
| `GET` | `/api/articles?topic=AI&n=10` | Top-N articles for a topic |
| `GET` | `/api/digest` | All topics in one response |
| `GET` | `/api/status` | Article counts, last fetch time, next scheduled run |
| `POST` | `/api/refresh` | Manually trigger a fetch |

---

## Project Structure

```
├── main.py               # FastAPI app — routes and lifespan
├── scheduler.py          # APScheduler daily job
├── fetcher.py            # Orchestrates sources → scoring → DB
├── scoring.py            # Recency, trust, popularity, and relevance scoring
├── db.py                 # SQLite schema and queries
├── config.py             # Topics, weights, trusted domains, API keys
├── sources/
│   ├── guardian.py       # The Guardian API client
│   └── gnews.py          # GNews API client
├── static/
│   └── index.html        # Frontend digest UI
├── requirements.txt
├── .env                  # API keys (not committed)
└── APP_PLAN.md           # Original design document
```

---

## Scoring

Articles are scored on a 0–1 scale using three signals:

| Signal | Weight | Source |
|---|---|---|
| Recency | 40% | Age of article (decays from 1.0 at <6h to 0.1 at >72h) |
| Trust | 30% | Source domain matched against `TRUSTED_DOMAINS` |
| Popularity | 30% | Upvote/engagement signals (Reddit — planned) |

While Reddit is not connected, the popularity weight is redistributed proportionally between recency and trust.

Articles with no matching topic keywords in their title are discarded before scoring.

---

## Planned

- Reddit API integration for popularity signals
- Email digest delivery
- Topic management via UI
- AI-powered relevance scoring (Claude API)
