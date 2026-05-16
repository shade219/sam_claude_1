import json
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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                name             TEXT PRIMARY KEY,
                keywords         TEXT NOT NULL,
                guardian_section TEXT,
                guardian_query   TEXT NOT NULL,
                is_builtin       INTEGER DEFAULT 0,
                created_at       TEXT NOT NULL
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


def get_topic_stats() -> dict[str, dict]:
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT topic, COUNT(*) as count, MAX(fetched_at) as last_fetched
            FROM articles
            GROUP BY topic
        """).fetchall()
    return {r["topic"]: {"count": r["count"], "last_fetched": r["last_fetched"]} for r in rows}


def clear_old_articles(days: int = 7):
    with get_conn() as conn:
        conn.execute("""
            DELETE FROM articles
            WHERE fetched_at < datetime('now', ? || ' days')
        """, (f"-{days}",))


# ── Topic config persistence ──────────────────────────────────────────────────

def seed_builtin_topics(topics_data: dict):
    """Insert built-in topics on first run; skips existing rows."""
    now = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        for name, cfg in topics_data.items():
            conn.execute("""
                INSERT OR IGNORE INTO topics
                    (name, keywords, guardian_section, guardian_query, is_builtin, created_at)
                VALUES (?, ?, ?, ?, 1, ?)
            """, (
                name,
                json.dumps(cfg["keywords"]),
                cfg.get("guardian_section") or None,
                cfg["guardian_query"],
                now,
            ))


def get_all_topic_configs() -> dict[str, dict]:
    """Return all topics ordered: built-ins first, then user-added by creation time."""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT name, keywords, guardian_section, guardian_query, is_builtin
            FROM topics
            ORDER BY is_builtin DESC, created_at
        """).fetchall()
    return {
        r["name"]: {
            "keywords": json.loads(r["keywords"]),
            "guardian_section": r["guardian_section"],
            "guardian_query": r["guardian_query"],
            "is_builtin": bool(r["is_builtin"]),
        }
        for r in rows
    }


def add_topic(name: str, keywords: list, guardian_section: str | None, guardian_query: str):
    now = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO topics (name, keywords, guardian_section, guardian_query, is_builtin, created_at)
            VALUES (?, ?, ?, ?, 0, ?)
        """, (name, json.dumps(keywords), guardian_section or None, guardian_query, now))


def delete_topic(name: str) -> bool:
    """Delete a user-added topic and its articles. Returns False for built-ins."""
    with get_conn() as conn:
        row = conn.execute("SELECT is_builtin FROM topics WHERE name = ?", (name,)).fetchone()
        if not row or row["is_builtin"]:
            return False
        conn.execute("DELETE FROM topics WHERE name = ?", (name,))
        conn.execute("DELETE FROM articles WHERE topic = ?", (name,))
    return True
