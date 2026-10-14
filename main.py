"""MoonlightCare FastAPI Application Entrypoint.

Main server application connecting:
1. 0ms Red Flag Guardrail & Supervisor FSM Orchestrator (POST /api/v1/chat).
2. 5ms Spatial Emergency Department & Pairing Search (GET /api/v1/emergency/*).
3. APScheduler 2-Track Background Daemon:
   - 5-minute Real-time Bed Poller (Hash Diffing Firestore batch upsert).
   - 24-hour Static Dataset Sync Worker (04:00 AM KST).
"""

from __future__ import annotations

import contextlib
import datetime
import logging
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from app.api import api_v1_router
from app.api.v1.chat import get_supervisor
from app.config import settings
from app.services.emergency_sync_service import fetch_hospital_coordinates
from app.services.pairing_service import load_nationwide_pairings
from app.services.scheduler import background_daemon

# Configure standard logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("moonlightcare")

KST = datetime.timezone(datetime.timedelta(hours=9))


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifecycle context manager: handles startup and graceful shutdown."""
    logger.info("🚀 Starting MoonlightCare API Server...")

    # 1. Warm up disk caches
    try:
        coords = fetch_hospital_coordinates(stage1="서울특별시")
        pairings = load_nationwide_pairings()
        logger.info(
            f"✅ Cache pre-warmed: {len(coords)} hospital coords, {len(pairings)} pairings."
        )
    except Exception as e:
        logger.warning(f"⚠️ Cache pre-warming warning: {e}")

    # 2. Start APScheduler background daemon (3-Track)
    try:
        background_daemon.start(
            bed_interval_minutes=5,
            static_cron_hour=4,
            static_cron_minute=0,
            session_eviction_interval_minutes=15,
        )
        logger.info("✅ APScheduler 3-Track background worker (Beds, Static, Sessions) started.")
    except Exception as e:
        logger.warning(f"⚠️ Background scheduler startup warning: {e}")

    yield

    # Graceful shutdown
    logger.info("🛑 Shutting down MoonlightCare API Server...")
    try:
        background_daemon.shutdown(wait=False)
        logger.info("✅ Background scheduler stopped cleanly.")
    except Exception as e:
        logger.error(f"Error during scheduler shutdown: {e}")


app = FastAPI(
    title="MoonlightCare API",
    description=(
        "야간 소아 응급실 뺑뺑이를 막는 0ms 세이프티 가드레일 & "
        "데이터 기반 2-트랙 지능형 라우터 REST API 서비스"
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware for Web & Mobile Clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/", tags=["System"])
async def root():
    """Root metadata and API service information."""
    return {
        "service": "MoonlightCare API",
        "version": "1.0.0",
        "description": "야간 소아 응급실 & 달빛어린이병원 2-트랙 실시간 매칭 시스템",
        "docs_url": "/docs",
        "health_url": "/health",
        "endpoints": {
            "chat": "/api/v1/chat",
            "chat_stream": "/api/v1/chat/stream",
            "emergency_nearby": "/api/v1/emergency/nearby",
            "emergency_pairings": "/api/v1/emergency/pairings",
            "emergency_sync": "/api/v1/emergency/sync",
            "scheduler_status": "/api/v1/emergency/status",
        },
    }


@app.get("/ktas", tags=["KTAS"], response_class=FileResponse)
async def get_ktas_viewer():
    """Serves the interactive KTAS 2021 guideline HTML viewer."""
    return FileResponse("ktas_viewer.html", media_type="text/html")


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint providing runtime operational status."""
    supervisor = get_supervisor()
    now_kst = datetime.datetime.now(KST).isoformat()

    return {
        "status": "healthy",
        "timestamp": now_kst,
        "scheduler": {
            "running": background_daemon.is_running(),
            "poll_count": background_daemon.poll_count,
            "last_poll_time": background_daemon.last_bed_poll_time,
        },
        "sessions": {
            "active_count": supervisor.session_manager.count(),
        },
        "integrations": {
            "public_data_api_configured": settings.has_public_api_key(),
            "gemini_api_configured": bool(settings.gemini_api_key),
            "firebase_configured": settings.has_firebase_key(),
        },
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )
