from datetime import datetime, timezone
import time
import sources.guardian as guardian
import sources.gnews as gnews
import scoring
import db
import config

GNEWS_DELAY_SECONDS = 2


def fetch_all() -> int:
    now = datetime.now(timezone.utc).isoformat()
    total = 0

    for i, topic in enumerate(config.TOPICS):
        raw = []

        try:
            raw += guardian.fetch(topic)
            print(f"  Guardian: {len(raw)} articles for '{topic}'")
        except Exception as e:
            print(f"  Guardian failed for '{topic}': {e}")

        if i > 0:
            time.sleep(GNEWS_DELAY_SECONDS)

        before = len(raw)
        try:
            raw += gnews.fetch(topic)
            print(f"  GNews: {len(raw) - before} articles for '{topic}'")
        except Exception as e:
            print(f"  GNews failed for '{topic}': {e}")

        for article in raw:
            scored = scoring.compute_score(article)
            scored["fetched_at"] = now
            db.upsert_article(scored)

        total += len(raw)

    db.clear_old_articles(days=7)
    print(f"Fetch complete — {total} articles across {len(config.TOPICS)} topics")
    return total
