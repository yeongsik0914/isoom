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
import os
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

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

# Mount Static and Frontend Directories
if os.path.exists("frontend"):
    app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")
    if os.path.exists("frontend/css"):
        app.mount("/css", StaticFiles(directory="frontend/css"), name="css")
    if os.path.exists("frontend/js"):
        app.mount("/js", StaticFiles(directory="frontend/js"), name="js")
    if os.path.exists("frontend/assets"):
        app.mount("/assets", StaticFiles(directory="frontend/assets"), name="assets")

if os.path.exists("frontend/templates"):
    app.mount("/templates", StaticFiles(directory="frontend/templates"), name="templates")

if os.path.exists("app/static"):
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

if os.path.exists("data"):
    app.mount("/data", StaticFiles(directory="data"), name="data")


@app.get("/", tags=["System"])
async def root(request: Request):
    """Root metadata and API service information, or mobile web app for browser clients."""
    accept = request.headers.get("accept", "")
    # Serve mobile web splash page as 1st priority for browser clients
    if "text/html" in accept and "application/json" not in accept:
        path = find_frontend_html("onboarding", "splash.html")
        if path and os.path.exists(path):
            return FileResponse(path, media_type="text/html")
        fallback = find_frontend_html("home", "index.html")
        if fallback and os.path.exists(fallback):
            return FileResponse(fallback, media_type="text/html")

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
            "aisum_splash": "/splash",
            "aisum_permission": "/permission",
            "aisum_home": "/home",
            "aisum_settings": "/settings",
            "aisum_terms": "/terms",
            "aisum_history": "/history",
            "aisum_qr": "/qr",
            "aisum_licenses": "/licenses",
            "aisum_guidebook": "/guidebook",
        },
    }


@app.get("/ktas", tags=["KTAS"], response_class=FileResponse)
async def get_ktas_viewer():
    """Serves the interactive KTAS 2021 guideline HTML viewer."""
    return FileResponse("ktas_viewer.html", media_type="text/html")


def find_frontend_html(category: str, filename: str) -> str | None:
    """Finds HTML file from unified templates directory with backward compatibility."""
    candidates = [
        f"frontend/templates/{filename}",
        f"frontend/templates/{category}/{filename}" if category else None,
        f"frontend/{category}/{filename}" if category else None,
        f"frontend/{filename}",
        f"app/templates/{filename}",
        f"app/static/{filename}",
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None



@app.get("/splash", tags=["Frontend"], response_class=FileResponse)
@app.get("/splash.html", tags=["Frontend"], response_class=FileResponse)
async def get_aisum_splash():
    """Serves the Aisum first loading splash screen."""
    path = find_frontend_html("onboarding", "splash.html")
    if path:
        return FileResponse(path, media_type="text/html")
    return JSONResponse(status_code=404, content={"detail": "Splash page not found"})


@app.get("/permission", tags=["Frontend"], response_class=FileResponse)
@app.get("/permission.html", tags=["Frontend"], response_class=FileResponse)
async def get_aisum_permission():
    """Serves the Aisum app permission specification page."""
    path = find_frontend_html("onboarding", "permission.html")
    if path:
        return FileResponse(path, media_type="text/html")
    return JSONResponse(status_code=404, content={"detail": "Permission page not found"})


@app.get("/home", tags=["Frontend"], response_class=FileResponse)
@app.get("/index.html", tags=["Frontend"], response_class=FileResponse)
async def get_aisum_home():
    """Serves the Aisum mobile web main page."""
    path = find_frontend_html("home", "index.html")
    if path:
        return FileResponse(path, media_type="text/html")
    return JSONResponse(status_code=404, content={"detail": "Home page not found"})


@app.get("/input", tags=["Frontend"], response_class=FileResponse)
@app.get("/input.html", tags=["Frontend"], response_class=FileResponse)
async def get_aisum_input():
    """Serves the Aisum symptom prompt input page."""
    path = find_frontend_html("triage", "input.html")
    if path:
        return FileResponse(path, media_type="text/html")
    return JSONResponse(status_code=404, content={"detail": "Input page not found"})


@app.get("/modal", tags=["Frontend"], response_class=FileResponse)
async def get_aisum_modal():
    """Serves the Aisum emergency guidance and consent modal preview page."""
    path = find_frontend_html("triage", "modal.html")
    if path:
        return FileResponse(path, media_type="text/html")
    return JSONResponse(status_code=404, content={"detail": "Modal page not found"})


@app.get("/result", tags=["Frontend"], response_class=FileResponse)
@app.get("/result.html", tags=["Frontend"], response_class=FileResponse)
async def get_aisum_result():
    """Serves the Aisum tailored medical recommendations result page."""
    path = find_frontend_html("result", "result.html")
    if path:
        return FileResponse(path, media_type="text/html")
    return JSONResponse(status_code=404, content={"detail": "Result page not found"})


@app.get("/loading", tags=["Frontend"], response_class=FileResponse)
async def get_aisum_loading():
    """Serves the Aisum AI analyzing loading animation page."""
    path = find_frontend_html("triage", "loading.html")
    if path:
        return FileResponse(path, media_type="text/html")
    return JSONResponse(status_code=404, content={"detail": "Loading page not found"})


@app.get("/hospital_detail", tags=["Frontend"], response_class=FileResponse)
@app.get("/hospital_detail.html", tags=["Frontend"], response_class=FileResponse)
async def get_aisum_hospital_detail():
    """Serves the Aisum Hospital Detail & Real-time queue ticketing page."""
    path = find_frontend_html("result", "hospital_detail.html")
    if path:
        return FileResponse(path, media_type="text/html")
    return JSONResponse(status_code=404, content={"detail": "Hospital detail page not found"})


@app.get("/pharmacy_detail", tags=["Frontend"], response_class=FileResponse)
@app.get("/pharmacy_detail.html", tags=["Frontend"], response_class=FileResponse)
async def get_aisum_pharmacy_detail():
    """Serves the Aisum Pharmacy Detail & Night Compounding Guidance page."""
    path = find_frontend_html("result", "pharmacy_detail.html")
    if path:
        return FileResponse(path, media_type="text/html")
    return JSONResponse(status_code=404, content={"detail": "Pharmacy detail page not found"})


@app.get("/emergency_alert", tags=["Frontend"], response_class=FileResponse)
@app.get("/emergency_alert.html", tags=["Frontend"], response_class=FileResponse)
async def get_aisum_emergency_alert():
    """Serves the Aisum 0ms Red Flag 119 emergency direct alert page."""
    path = find_frontend_html("emergency", "emergency_alert.html")
    if path:
        return FileResponse(path, media_type="text/html")
    return JSONResponse(status_code=404, content={"detail": "Emergency alert page not found"})


@app.get("/guide", tags=["Frontend"], response_class=FileResponse)
@app.get("/guide/emergency", tags=["Frontend"], response_class=FileResponse)
async def get_guide_unified():
    """Serves the unified Aisum Emergency Guide with horizontal swipe photo carousel."""
    path = find_frontend_html("emergency", "emergency_guide.html")
    if path:
        return FileResponse(path, media_type="text/html")
    return JSONResponse(status_code=404, content={"detail": "Emergency guide not found"})


@app.get("/guide/symptoms", tags=["Frontend"], response_class=FileResponse)
async def get_guide_symptoms():
    """Serves the Aisum Emergency Guide (Recommendation 1: Symptoms Photo Guide)."""
    path = find_frontend_html("emergency", "emergency_guide_symptoms.html")
    if path:
        return FileResponse(path, media_type="text/html")
    return JSONResponse(status_code=404, content={"detail": "Symptoms guide not found"})


@app.get("/guide/checklist", tags=["Frontend"], response_class=FileResponse)
async def get_guide_checklist():
    """Serves the Aisum Emergency Guide (Recommendation 2: ER Departure Checklist)."""
    path = find_frontend_html("emergency", "emergency_guide_checklist.html")
    if path:
        return FileResponse(path, media_type="text/html")
    return JSONResponse(status_code=404, content={"detail": "Checklist guide not found"})


@app.get("/settings", tags=["Frontend"], response_class=FileResponse)
@app.get("/settings.html", tags=["Frontend"], response_class=FileResponse)
async def get_aisum_settings():
    """Serves the Aisum Settings page."""
    path = find_frontend_html("settings", "settings.html")
    if path:
        return FileResponse(path, media_type="text/html")
    return JSONResponse(status_code=404, content={"detail": "Settings page not found"})


@app.get("/history", tags=["Frontend"], response_class=FileResponse)
@app.get("/history.html", tags=["Frontend"], response_class=FileResponse)
async def get_aisum_history():
    """Serves the Aisum Triage History page."""
    path = find_frontend_html("history", "history.html")
    if path:
        return FileResponse(path, media_type="text/html")
    return JSONResponse(status_code=404, content={"detail": "History page not found"})


@app.get("/terms", tags=["Frontend"], response_class=FileResponse)
@app.get("/terms.html", tags=["Frontend"], response_class=FileResponse)
async def get_aisum_terms():
    """Serves the Aisum Terms of Service page."""
    path = find_frontend_html("settings", "terms.html")
    if path:
        return FileResponse(path, media_type="text/html")
    return JSONResponse(status_code=404, content={"detail": "Terms page not found"})


@app.get("/qr", tags=["Frontend"], response_class=FileResponse)
@app.get("/qr.html", tags=["Frontend"], response_class=FileResponse)
async def get_aisum_qr():
    """Serves the Aisum Mobile Device QR Code & PWA onboarding page."""
    path = find_frontend_html("settings", "qr.html")
    if path:
        return FileResponse(path, media_type="text/html")
    return JSONResponse(status_code=404, content={"detail": "QR page not found"})


@app.get("/licenses", tags=["Frontend"], response_class=FileResponse)
@app.get("/licenses.html", tags=["Frontend"], response_class=FileResponse)
@app.get("/opensource", tags=["Frontend"], response_class=FileResponse)
@app.get("/opensource.html", tags=["Frontend"], response_class=FileResponse)
async def get_aisum_licenses():
    """Serves the Aisum Open Source Licenses and Attribution page."""
    path = find_frontend_html("settings", "licenses.html") or find_frontend_html("settings", "opensource.html")
    if path:
        return FileResponse(path, media_type="text/html")
    return JSONResponse(status_code=404, content={"detail": "Licenses page not found"})


@app.get("/guidebook", tags=["Frontend"], response_class=FileResponse)
@app.get("/guidebook.html", tags=["Frontend"], response_class=FileResponse)
async def get_aisum_guidebook():
    """Serves the comprehensive Aisum App Guidebook page."""
    path = find_frontend_html("guide", "guidebook.html")
    if path:
        return FileResponse(path, media_type="text/html")
    return JSONResponse(status_code=404, content={"detail": "Guidebook page not found"})


@app.get("/css/style.css", include_in_schema=False)
@app.get("/style.css", tags=["Frontend"], response_class=FileResponse)
async def get_aisum_style():
    """Serves the Aisum CSS stylesheet."""
    if os.path.exists("frontend/css/style.css"):
        return FileResponse("frontend/css/style.css", media_type="text/css")
    return FileResponse("app/static/css/style.css", media_type="text/css")



@app.get("/js/main.js", include_in_schema=False)
async def get_aisum_js():
    """Serves the Aisum JS module."""
    if os.path.exists("frontend/js/main.js"):
        return FileResponse("frontend/js/main.js", media_type="application/javascript")
    return JSONResponse(status_code=404, content={"detail": "JS not found"})


@app.get("/manifest.json", tags=["PWA"], response_class=FileResponse)
async def get_pwa_manifest():
    """Serves PWA Web App Manifest."""
    if os.path.exists("frontend/manifest.json"):
        return FileResponse("frontend/manifest.json", media_type="application/manifest+json")
    if os.path.exists("app/static/manifest.json"):
        return FileResponse("app/static/manifest.json", media_type="application/manifest+json")
    return JSONResponse(status_code=404, content={"detail": "Manifest not found"})


@app.get("/sw.js", tags=["PWA"], response_class=FileResponse)
async def get_pwa_service_worker():
    """Serves PWA Service Worker script with no-cache headers for instant updates."""
    target = "frontend/sw.js" if os.path.exists("frontend/sw.js") else "app/static/sw.js"
    if os.path.exists(target):
        return FileResponse(
            target,
            media_type="application/javascript",
            headers={"Service-Worker-Allowed": "/", "Cache-Control": "no-cache, no-store, must-revalidate"}
        )
    return JSONResponse(status_code=404, content={"detail": "Service worker not found"})


@app.get("/img/{filename}", tags=["PWA"], response_class=FileResponse)
async def get_pwa_image(filename: str):
    """Serves PWA icons and image assets."""
    for root in ["frontend/img", "app/static/img", "frontend/assets"]:
        p = os.path.join(root, filename)
        if os.path.exists(p):
            return FileResponse(p)
    return JSONResponse(status_code=404, content={"detail": f"Image {filename} not found"})


@app.get("/{subpath:path}/{filename}.html", include_in_schema=False)
async def fallback_subpath_html(subpath: str, filename: str):
    """Smart fallback router: intercepts requests like /home/input.html and serves from templates/."""
    target_filename = f"{filename}.html"
    path = find_frontend_html("", target_filename)
    if path and os.path.exists(path):
        return FileResponse(path, media_type="text/html")
    return JSONResponse(status_code=404, content={"detail": f"Page {target_filename} not found"})


@app.get("/{filename}.html", include_in_schema=False)
async def fallback_direct_html(filename: str):
    """Direct root HTML router: /index.html, /input.html, /result.html, etc."""
    target_filename = f"{filename}.html"
    path = find_frontend_html("", target_filename)
    if path and os.path.exists(path):
        return FileResponse(path, media_type="text/html")
    return JSONResponse(status_code=404, content={"detail": f"Page {target_filename} not found"})


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
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
    )
