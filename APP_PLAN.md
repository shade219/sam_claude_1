# Daily Digest App — Plan

## Overview

A personal web app that curates a daily short-list of interesting articles, posts, and blog entries from across the internet for user-defined topics. Each day it fetches fresh content, scores it, and presents a clean digest ranked by quality and relevance.

---

## Goals

- Aggregate articles from multiple sources for chosen topics
- Score and rank articles by recency, source trust, and popularity
- Present a daily top-N digest via a local web app
- Keep infrastructure simple and free to run

---

## Data Sources

| Source | API / Library | Cost | Notes |
|---|---|---|---|
| The Guardian | REST API + API key | Free (5,000 req/day) | High quality, broad topic coverage |
| GNews | REST API + API key | Free (100 req/day) | Good for broad keyword search |
| Reddit | PRAW (OAuth) | Free (personal use) | Community-voted signals, tech/news subreddits |

**Not used (yet):** NewsAPI.org — free tier restricts recent articles in production.

---

## Ranking Logic (v1)

Articles are scored on three signals, then combined into a single score:

1. **Recency** — articles published within the last 24 hours score highest; score decays with age
2. **Source trust score** — manually maintained list of trusted domains with a weight multiplier (e.g. theguardian.com = 1.0, unknown blog = 0.5)
3. **Popularity signals** — Reddit upvote count and comment count for posts; shares/engagement where available from APIs

Combined score formula (initial, subject to tuning):

```
score = (recency_score * 0.4) + (trust_score * 0.3) + (popularity_score * 0.3)
```

Top-N articles per topic are surfaced in the digest (N is configurable, default = 10).

---

## Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| Backend | Python + FastAPI | Lightweight, async-friendly, easy to extend |
| Frontend | HTML + vanilla JS | No build step, simple to iterate on |
| Storage | SQLite | Zero-config, sufficient for personal use |
| Scheduling | APScheduler | In-process daily refresh, no external cron needed |
| Reddit client | PRAW | Official Python wrapper for Reddit API |

---

## App Structure (planned)

```
daily-digest/
├── main.py               # FastAPI app entry point
├── scheduler.py          # Daily fetch + score job
├── sources/
│   ├── guardian.py       # Guardian API client
│   ├── gnews.py          # GNews API client
│   └── reddit.py         # Reddit (PRAW) client
├── scoring.py            # Ranking and scoring logic
├── db.py                 # SQLite models and queries
├── static/
│   └── index.html        # Frontend digest view
├── config.py             # Topics, top-N, trust scores, API keys
├── requirements.txt
└── APP_PLAN.md           # This file
```

---

## Configuration

Users define topics and preferences in `config.py`:

```python
TOPICS = ["AI", "climate", "space", "cybersecurity"]
TOP_N = 10
REFRESH_HOUR = 7          # Fetch new articles at 7am daily
TRUSTED_DOMAINS = {
    "theguardian.com": 1.0,
    "arstechnica.com": 0.9,
    "reuters.com": 0.9,
    "bbc.com": 0.85,
}
```

---

## Digest UI (web app)

- Single-page layout served by FastAPI at `localhost:8000`
- Topic tabs or sections across the top
- Each article card shows: title, source, published time, score, and a link
- "Refresh" button to manually trigger a fetch
- Minimal styling — readable, no frameworks needed

---

## Development Phases

| Phase | Scope |
|---|---|
| **1 — Scaffold** | Repo setup, FastAPI skeleton, SQLite schema, config |
| **2 — Sources** | Guardian + GNews + Reddit clients, raw article storage |
| **3 — Scoring** | Implement recency + trust + popularity scoring pipeline |
| **4 — UI** | Build digest frontend, topic tabs, article cards |
| **5 — Scheduler** | Wire up APScheduler for daily refresh |
| **6 — Polish** | Error handling, logging, README, GitHub push |

---

## Future Ideas (out of scope for v1)

- AI relevance scoring via Claude API
- Email digest delivery
- User-configurable topics via UI (not just config.py)
- More sources: HackerNews API, NY Times API, The Atlantic RSS
- Deduplication across sources
