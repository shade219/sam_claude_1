import httpx
import config

BASE_URL = "https://content.guardianapis.com/search"


def fetch(topic: str) -> list[dict]:
    params = {
        "q": topic,
        "api-key": config.GUARDIAN_API_KEY,
        "show-fields": "trailText",
        "order-by": "newest",
        "page-size": 20,
    }
    with httpx.Client(timeout=10) as client:
        resp = client.get(BASE_URL, params=params)
        resp.raise_for_status()

    results = resp.json().get("response", {}).get("results", [])
    return [
        {
            "title": r["webTitle"],
            "url": r["webUrl"],
            "source": "theguardian.com",
            "topic": topic,
            "published_at": r.get("webPublicationDate"),
            "popularity_raw": 0,
        }
        for r in results
    ]
