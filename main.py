import logging
import logging.config
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pydantic import BaseModel

import config
import db
import fetcher
import scheduler as sched

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)-8s %(name)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        }
    },
    "root": {"level": "INFO", "handlers": ["console"]},
    # Quiet noisy third-party loggers
    "loggers": {
        "apscheduler":  {"level": "WARNING"},
        "httpx":        {"level": "WARNING"},
        "uvicorn":      {"level": "INFO"},
    },
}

log = logging.getLogger(__name__)


def _check_config():
    missing = []
    if not config.GUARDIAN_API_KEY:
        missing.append("GUARDIAN_API_KEY")
    if not config.GNEWS_API_KEY:
        missing.append("GNEWS_API_KEY")
    if missing:
        log.warning("Missing API keys (sources will be skipped): %s", ", ".join(missing))


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.config.dictConfig(LOGGING_CONFIG)
    _check_config()
    db.init_db()
    db.seed_builtin_topics({
        name: {
            "keywords": config.TOPIC_KEYWORDS[name],
            "guardian_section": config.TOPIC_GUARDIAN_SECTIONS.get(name),
            "guardian_query": config.TOPIC_GUARDIAN_QUERIES[name],
        }
        for name in config.TOPICS
    })
    sched.start()
    yield
    sched.stop()


app = FastAPI(title="Daily Digest", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def index():
    return FileResponse("static/index.html")


class AddTopicRequest(BaseModel):
    topic: str


@app.get("/api/topics")
def get_topics():
    configs = db.get_all_topic_configs()
    return {
        "topics": list(configs.keys()),
        "builtin": [name for name, cfg in configs.items() if cfg["is_builtin"]],
    }


@app.post("/api/topics")
def add_topic(req: AddTopicRequest):
    topic = req.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Topic name cannot be empty")
    existing = db.get_all_topic_configs()
    if topic in existing:
        raise HTTPException(status_code=409, detail=f"Topic '{topic}' already exists")
    try:
        from claude_topics import generate_topic_config
        cfg = generate_topic_config(topic)
        db.add_topic(topic, cfg.keywords, cfg.guardian_section or None, cfg.guardian_query)
        return {"topic": topic, "keywords": cfg.keywords, "guardian_query": cfg.guardian_query}
    except Exception as e:
        log.error("Failed to generate config for topic '%s': %s", topic, e)
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/topics/{name}")
def remove_topic(name: str):
    if not db.delete_topic(name):
        raise HTTPException(status_code=400, detail=f"'{name}' is a built-in topic or does not exist")
    return {"status": "ok"}


@app.get("/api/articles")
def get_articles(topic: str, n: int = config.TOP_N):
    configs = db.get_all_topic_configs()
    if topic not in configs:
        raise HTTPException(status_code=404, detail=f"Topic '{topic}' not configured")
    articles = db.get_articles(topic, limit=n)
    return {"topic": topic, "articles": articles}


@app.get("/api/digest")
def get_digest():
    topics = list(db.get_all_topic_configs().keys())
    return db.get_all_topics_articles(topics, limit=config.TOP_N)


@app.get("/api/status")
def status():
    configs = db.get_all_topic_configs()
    return {
        "topics": db.get_topic_stats(),
        "configured": list(configs.keys()),
        "next_scheduled_run": sched.next_run_iso(),
    }


@app.post("/api/refresh")
def refresh():
    count = fetcher.fetch_all()
    return {"status": "ok", "articles_fetched": count}
