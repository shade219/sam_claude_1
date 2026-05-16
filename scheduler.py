from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import fetcher
import config

scheduler = AsyncIOScheduler(timezone="UTC")


def start():
    scheduler.add_job(
        fetcher.fetch_all,
        CronTrigger(hour=config.REFRESH_HOUR, minute=0, timezone="UTC"),
        id="daily_digest",
        replace_existing=True,
        misfire_grace_time=3600,  # run if missed by up to 1 hour (e.g. server restart)
    )
    scheduler.start()
    job = scheduler.get_job("daily_digest")
    next_run = job.next_run_time.strftime("%Y-%m-%d %H:%M UTC") if job else "unknown"
    print(f"Scheduler started — daily fetch at {config.REFRESH_HOUR:02d}:00 UTC | next run: {next_run}")


def stop():
    scheduler.shutdown(wait=False)


def next_run_iso() -> str | None:
    job = scheduler.get_job("daily_digest")
    return job.next_run_time.isoformat() if job and job.next_run_time else None
