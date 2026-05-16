from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

import config
import db
import fetcher
import scheduler as sched


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    sched.start()
    yield
    sched.stop()


app = FastAPI(title="Daily Digest", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def index():
    return FileResponse("static/index.html")


@app.get("/api/topics")
def get_topics():
    return {"topics": config.TOPICS}


@app.get("/api/articles")
def get_articles(topic: str, n: int = config.TOP_N):
    if topic not in config.TOPICS:
        raise HTTPException(status_code=404, detail=f"Topic '{topic}' not configured")
    articles = db.get_articles(topic, limit=n)
    return {"topic": topic, "articles": articles}


@app.get("/api/digest")
def get_digest():
    return db.get_all_topics_articles(config.TOPICS, limit=config.TOP_N)


@app.get("/api/status")
def status():
    return {
        "topics": db.get_topic_stats(),
        "configured": config.TOPICS,
        "next_scheduled_run": sched.next_run_iso(),
    }


@app.post("/api/refresh")
def refresh():
    count = fetcher.fetch_all()
    return {"status": "ok", "articles_fetched": count}
