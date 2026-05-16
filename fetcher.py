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
    total_stored = 0

    for i, topic in enumerate(config.TOPICS):
        raw = []

        try:
            fetched = guardian.fetch(topic)
            raw += fetched
            print(f"  Guardian: {len(fetched)} fetched for '{topic}'")
        except Exception as e:
            print(f"  Guardian failed for '{topic}': {e}")

        if i > 0:
            time.sleep(GNEWS_DELAY_SECONDS)

        try:
            fetched = gnews.fetch(topic)
            raw += fetched
            print(f"  GNews:    {len(fetched)} fetched for '{topic}'")
        except Exception as e:
            print(f"  GNews failed for '{topic}': {e}")

        kept = 0
        dropped = 0
        for article in raw:
            if not scoring.is_relevant(article):
                dropped += 1
                continue
            scored = scoring.compute_score(article)
            scored["fetched_at"] = now
            db.upsert_article(scored)
            kept += 1

        print(f"  '{topic}': {kept} stored, {dropped} dropped (off-topic)")
        total_stored += kept

    db.clear_old_articles(days=7)
    print(f"Fetch complete — {total_stored} articles stored across {len(config.TOPICS)} topics")
    return total_stored
