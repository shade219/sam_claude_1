from datetime import datetime, timezone
from urllib.parse import urlparse
import config


def recency_score(published_at: str | None) -> float:
    if not published_at:
        return 0.1
    try:
        pub = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        age_hours = (datetime.now(timezone.utc) - pub).total_seconds() / 3600
    except Exception:
        return 0.1

    if age_hours <= 6:   return 1.0
    if age_hours <= 12:  return 0.8
    if age_hours <= 24:  return 0.6
    if age_hours <= 48:  return 0.4
    if age_hours <= 72:  return 0.2
    return 0.1


def trust_score(source: str | None) -> float:
    if not source:
        return 0.5
    domain = urlparse(f"https://{source}").netloc.removeprefix("www.") or source
    return config.TRUSTED_DOMAINS.get(domain, 0.5)


def popularity_score(raw: int) -> float:
    # Placeholder — will normalize against upvote signals once Reddit is wired up
    return 0.0


def compute_score(article: dict) -> dict:
    r = recency_score(article.get("published_at"))
    t = trust_score(article.get("source"))
    p = popularity_score(article.get("popularity_raw", 0))
    w = config.SCORE_WEIGHTS
    total = r * w["recency"] + t * w["trust"] + p * w["popularity"]
    return {
        **article,
        "recency_score": round(r, 4),
        "trust_score": round(t, 4),
        "popularity_score": round(p, 4),
        "score": round(total, 4),
    }
