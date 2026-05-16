import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import fetcher
import config

log = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone="UTC")


def start():
    scheduler.add_job(
        fetcher.fetch_all,
        CronTrigger(hour=config.REFRESH_HOUR, minute=0, timezone="UTC"),
        id="daily_digest",
        replace_existing=True,
        misfire_grace_time=3600,  # still run if server was down at fire time and recovers within 1h
    )
    scheduler.start()
    job = scheduler.get_job("daily_digest")
    next_run = job.next_run_time.strftime("%Y-%m-%d %H:%M UTC") if job else "unknown"
    log.info("Scheduler started — daily fetch at %02d:00 UTC | next run: %s", config.REFRESH_HOUR, next_run)


def stop():
    scheduler.shutdown(wait=False)
    log.info("Scheduler stopped")


def next_run_iso() -> str | None:
    job = scheduler.get_job("daily_digest")
    return job.next_run_time.isoformat() if job and job.next_run_time else None
