import logging
from datetime import datetime, timezone
import time
import sources.guardian as guardian
import sources.gnews as gnews
import scoring
import db
import config

log = logging.getLogger(__name__)

GNEWS_DELAY_SECONDS = 2


def fetch_all() -> int:
    log.info("Fetch started for topics: %s", config.TOPICS)
    now = datetime.now(timezone.utc).isoformat()
    total_stored = 0

    for i, topic in enumerate(config.TOPICS):
        raw = []

        try:
            fetched = guardian.fetch(topic)
            raw += fetched
            log.info("Guardian: %d articles fetched for '%s'", len(fetched), topic)
        except Exception as e:
            log.warning("Guardian failed for '%s': %s", topic, e)

        if i > 0:
            time.sleep(GNEWS_DELAY_SECONDS)

        try:
            fetched = gnews.fetch(topic)
            raw += fetched
            log.info("GNews: %d articles fetched for '%s'", len(fetched), topic)
        except Exception as e:
            log.warning("GNews failed for '%s': %s", topic, e)

        kept = dropped = 0
        for article in raw:
            if not scoring.is_relevant(article):
                dropped += 1
                continue
            try:
                scored = scoring.compute_score(article)
                scored["fetched_at"] = now
                db.upsert_article(scored)
                kept += 1
            except Exception as e:
                log.error("Failed to store article '%s': %s", article.get("url"), e)

        log.info("'%s': %d stored, %d dropped (off-topic)", topic, kept, dropped)
        total_stored += kept

    db.clear_old_articles(days=7)
    log.info("Fetch complete — %d articles stored across %d topics", total_stored, len(config.TOPICS))
    return total_stored
