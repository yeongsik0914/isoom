"""Background Daemon & APScheduler Service for MoonlightCare.

Orchestrates 2-track background tasks:
1. Real-time Emergency Bed Poller (every 5 minutes):
   - Polls NMC E-Gen real-time pediatric beds and unstructured notices.
   - Applies In-Memory Hash Diffing (MD5) to eliminate redundant writes.
   - Batch writes modified documents to Cloud Firestore 'emergency_beds'.
2. Static Dataset Sync Worker (daily at 04:00 AM KST):
   - Updates emergency hospital GPS coordinates cache.
   - Refreshes nationwide Moonlight Children's Hospital - 30-min Pharmacy pairing master.
"""

from __future__ import annotations

import datetime
import logging
from typing import Any, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings
from app.schemas.emergency import HolidayInfo
from app.services.emergency_sync_service import (
    default_hash_cache,
    fetch_emergency_beds,
    fetch_hospital_coordinates,
    sync_to_firestore,
)
from app.services.holiday_service import HolidayService
from app.services.pairing_service import load_nationwide_pairings

logger = logging.getLogger(__name__)
KST = datetime.timezone(datetime.timedelta(hours=9))


class BackgroundDaemon:
    """Manages APScheduler lifecycle and metric counters for MoonlightCare."""

    def __init__(self) -> None:
        self.scheduler: Optional[AsyncIOScheduler] = None
        self.holiday_service = HolidayService()
        self.last_bed_poll_time: Optional[str] = None
        self.last_bed_poll_stats: Optional[dict[str, Any]] = None
        self.last_static_sync_time: Optional[str] = None
        self.last_eviction_time: Optional[str] = None
        self.poll_count: int = 0
        self.static_sync_count: int = 0
        self.eviction_count: int = 0
        self._is_running: bool = False

    def is_running(self) -> bool:
        """Returns True if scheduler is active and running."""
        return bool(self.scheduler and self.scheduler.running)

    async def evict_expired_sessions(self, max_idle_seconds: int = 1800) -> dict[str, Any]:
        """Purges inactive patient consultation sessions from memory (30-min TTL)."""
        now_str = datetime.datetime.now(KST).isoformat()
        self.eviction_count += 1
        self.last_eviction_time = now_str
        try:
            from app.api.v1.chat import get_supervisor

            supervisor = get_supervisor()
            evicted = await supervisor.session_manager.evict_expired_sessions(
                max_idle_seconds=max_idle_seconds
            )
            active = supervisor.session_manager.count()
            logger.info(
                f"[Scheduler] Session eviction #{self.eviction_count} complete: "
                f"evicted={evicted}, active_remaining={active}"
            )
            return {
                "evicted_count": evicted,
                "active_remaining": active,
                "timestamp": now_str,
                "status": "SUCCESS",
            }
        except Exception as e:
            logger.error(f"[Scheduler] Error during session eviction: {e}", exc_info=True)
            return {"error": str(e), "timestamp": now_str, "status": "FAILED"}

    async def poll_realtime_beds(self) -> dict[str, Any]:
        """Polls real-time emergency beds and updates Firestore via Hash Diffing."""
        now_str = datetime.datetime.now(KST).isoformat()
        self.poll_count += 1
        self.last_bed_poll_time = now_str

        try:
            date_str = datetime.datetime.now(KST).strftime("%Y%m%d")
            holiday_info = self.holiday_service.get_holiday_info(date_str)

            # 1. Collect real-time beds with NLP filtering (force_refresh=True to refresh TTL cache)
            beds = fetch_emergency_beds(stage1="서울특별시", force_refresh=True)

            stats: dict[str, Any]
            # 2. Synchronize to Firestore if credentials exist
            if settings.has_firebase_key():
                try:
                    stats = sync_to_firestore(
                        hospitals=beds,
                        holiday_meta=holiday_info,
                        use_diffing=True,
                        hash_cache=default_hash_cache,
                    )
                except Exception as fe:
                    logger.warning(f"[Scheduler] Firestore write fallback: {fe}")
                    # Diff in memory even when Firestore write fails
                    changed, skipped = default_hash_cache.diff_and_filter(beds)
                    stats = {
                        "total_count": len(beds),
                        "synced_count": len(changed),
                        "skipped_count": skipped,
                        "acceptable_count": sum(1 for b in beds if b.pediatric_acceptable),
                        "surge_risk_level": holiday_info.surge_risk_level,
                        "saving_rate_percent": round((skipped / len(beds)) * 100, 1) if beds else 0.0,
                        "note": "Local diffing executed (Firestore write skipped)",
                    }
            else:
                # In-memory diffing for local testing / offline dev
                changed, skipped = default_hash_cache.diff_and_filter(beds)
                stats = {
                    "total_count": len(beds),
                    "synced_count": len(changed),
                    "skipped_count": skipped,
                    "acceptable_count": sum(1 for b in beds if b.pediatric_acceptable),
                    "surge_risk_level": holiday_info.surge_risk_level,
                    "saving_rate_percent": round((skipped / len(beds)) * 100, 1) if beds else 0.0,
                    "note": "Local mock/in-memory diffing executed",
                }

            self.last_bed_poll_stats = stats
            logger.info(
                f"[Scheduler] Bed poll #{self.poll_count} complete: "
                f"total={stats['total_count']}, synced={stats['synced_count']}, "
                f"skipped={stats['skipped_count']} ({stats['saving_rate_percent']}%)"
            )
            return stats
        except Exception as e:
            logger.error(f"[Scheduler] Error during real-time bed polling: {e}", exc_info=True)
            err_stats = {"error": str(e), "timestamp": now_str}
            self.last_bed_poll_stats = err_stats
            return err_stats

    async def sync_static_datasets(self) -> dict[str, Any]:
        """Refreshes hospital coordinates and pairing datasets (24-hour cycle)."""
        now_str = datetime.datetime.now(KST).isoformat()
        self.static_sync_count += 1
        self.last_static_sync_time = now_str

        try:
            coords = fetch_hospital_coordinates(stage1="서울특별시")
            pairings = load_nationwide_pairings()

            stats = {
                "hospital_coords_count": len(coords),
                "pairings_count": len(pairings),
                "synced_at": now_str,
                "status": "SUCCESS",
            }
            logger.info(
                f"[Scheduler] Static datasets sync complete: coords={len(coords)}, pairings={len(pairings)}"
            )
            return stats
        except Exception as e:
            logger.error(f"[Scheduler] Error during static datasets sync: {e}", exc_info=True)
            return {"error": str(e), "synced_at": now_str, "status": "FAILED"}

    def start(
        self,
        bed_interval_minutes: int = 5,
        static_cron_hour: int = 4,
        static_cron_minute: int = 0,
        session_eviction_interval_minutes: int = 15,
    ) -> None:
        """Initializes and starts the APScheduler if not already active."""
        if self.scheduler and self.scheduler.running:
            return

        self.scheduler = AsyncIOScheduler(timezone="Asia/Seoul")

        # Job 1: 5-minute Real-time Bed Poller
        self.scheduler.add_job(
            self.poll_realtime_beds,
            trigger=IntervalTrigger(minutes=bed_interval_minutes),
            id="job_realtime_bed_poller",
            name="5-Minute Real-time Emergency Bed Poller",
            replace_existing=True,
            coalesce=True,
        )

        # Job 2: 24-hour Static Dataset Sync (04:00 AM KST)
        self.scheduler.add_job(
            self.sync_static_datasets,
            trigger=CronTrigger(hour=static_cron_hour, minute=static_cron_minute, timezone="Asia/Seoul"),
            id="job_static_dataset_sync",
            name="Daily 04:00 AM Static Data & Pairing Sync",
            replace_existing=True,
            coalesce=True,
        )

        # Job 3: Periodic Session Inactivity Eviction (every 15 minutes)
        self.scheduler.add_job(
            self.evict_expired_sessions,
            trigger=IntervalTrigger(minutes=session_eviction_interval_minutes),
            id="job_session_eviction",
            name="15-Minute Session Inactivity Eviction Worker",
            replace_existing=True,
            coalesce=True,
        )

        self.scheduler.start()
        self._is_running = True
        logger.info("[Scheduler] Background daemon started with 3-track jobs (Beds, Static, Sessions).")

    def shutdown(self, wait: bool = False) -> None:
        """Stops the scheduler cleanly."""
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown(wait=wait)
            self._is_running = False
            logger.info("[Scheduler] Background daemon cleanly shut down.")

    def get_status(self) -> dict[str, Any]:
        """Returns the current operational status of the background daemon."""
        jobs_info: list[dict[str, Any]] = []
        if self.scheduler:
            for job in self.scheduler.get_jobs():
                next_run = job.next_run_time.isoformat() if job.next_run_time else None
                jobs_info.append(
                    {
                        "id": job.id,
                        "name": job.name,
                        "next_run_time": next_run,
                    }
                )

        return {
            "running": self.is_running(),
            "jobs": jobs_info,
            "last_bed_poll_time": self.last_bed_poll_time,
            "last_bed_poll_stats": self.last_bed_poll_stats,
            "last_static_sync_time": self.last_static_sync_time,
            "last_eviction_time": self.last_eviction_time,
            "poll_count": self.poll_count,
            "static_sync_count": self.static_sync_count,
            "eviction_count": self.eviction_count,
        }


# Global singleton daemon instance
background_daemon = BackgroundDaemon()
