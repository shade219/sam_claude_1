import logging
import httpx
from urllib.parse import urlparse
import config

log = logging.getLogger(__name__)

BASE_URL = "https://gnews.io/api/v4/search"


def fetch(topic: str) -> list[dict]:
    if not config.GNEWS_API_KEY:
        raise ValueError("GNEWS_API_KEY is not set")

    params = {
        "q":     topic,
        "token": config.GNEWS_API_KEY,
        "lang":  "en",
        "max":   10,
    }

    with httpx.Client(timeout=10) as client:
        resp = client.get(BASE_URL, params=params)
        resp.raise_for_status()

    articles_raw = resp.json().get("articles", [])
    if not articles_raw:
        log.debug("GNews returned 0 articles for topic '%s'", topic)

    results = []
    for a in articles_raw:
        source_url = a.get("source", {}).get("url", "")
        domain     = urlparse(source_url).netloc.removeprefix("www.") or source_url
        results.append({
            "title":          a["title"],
            "url":            a["url"],
            "source":         domain,
            "topic":          topic,
            "published_at":   a.get("publishedAt"),
            "popularity_raw": 0,
        })
    return results
