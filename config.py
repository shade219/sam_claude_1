import os
from dotenv import load_dotenv

load_dotenv()

GUARDIAN_API_KEY = os.getenv("GUARDIAN_API_KEY")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "daily-digest:v1.0")

TOPICS = ["AI", "climate", "space", "cybersecurity"]

TOP_N = 10

REFRESH_HOUR = 7

TRUSTED_DOMAINS = {
    "theguardian.com": 1.0,
    "arstechnica.com": 0.9,
    "reuters.com": 0.9,
    "bbc.com": 0.85,
    "apnews.com": 0.85,
    "wired.com": 0.8,
    "technologyreview.com": 0.8,
    "nature.com": 0.9,
    "scientificamerican.com": 0.85,
}

SCORE_WEIGHTS = {
    "recency": 0.4,
    "trust": 0.3,
    "popularity": 0.3,
}
