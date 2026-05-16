import sqlite3
from datetime import datetime, timezone
from contextlib import contextmanager

DB_PATH = "digest.db"


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                title           TEXT NOT NULL,
                url             TEXT NOT NULL UNIQUE,
                source          TEXT,
                topic           TEXT,
                published_at    TEXT,
                recency_score   REAL DEFAULT 0,
                trust_score     REAL DEFAULT 0,
                popularity_score REAL DEFAULT 0,
                score           REAL DEFAULT 0,
                fetched_at      TEXT
            )
        """)


def upsert_article(article: dict):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO articles
                (title, url, source, topic, published_at,
                 recency_score, trust_score, popularity_score, score, fetched_at)
            VALUES
                (:title, :url, :source, :topic, :published_at,
                 :recency_score, :trust_score, :popularity_score, :score, :fetched_at)
            ON CONFLICT(url) DO UPDATE SET
                score            = excluded.score,
                recency_score    = excluded.recency_score,
                trust_score      = excluded.trust_score,
                popularity_score = excluded.popularity_score,
                fetched_at       = excluded.fetched_at
        """, article)


def get_articles(topic: str, limit: int = 10) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT * FROM articles
            WHERE topic = ?
            ORDER BY score DESC
            LIMIT ?
        """, (topic, limit)).fetchall()
    return [dict(r) for r in rows]


def get_all_topics_articles(topics: list[str], limit: int = 10) -> dict[str, list[dict]]:
    return {topic: get_articles(topic, limit) for topic in topics}


def clear_old_articles(days: int = 7):
    with get_conn() as conn:
        conn.execute("""
            DELETE FROM articles
            WHERE fetched_at < datetime('now', ? || ' days')
        """, (f"-{days}",))
