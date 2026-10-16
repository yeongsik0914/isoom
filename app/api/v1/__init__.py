"""API v1 routers aggregator."""

from fastapi import APIRouter

from app.api.v1.chat import router as chat_router
from app.api.v1.emergency import router as emergency_router
from app.api.v1.location import router as location_router

api_v1_router = APIRouter()

api_v1_router.include_router(chat_router, prefix="/chat", tags=["Chat & Triage"])
api_v1_router.include_router(emergency_router, prefix="/emergency", tags=["Emergency & Spatial"])
api_v1_router.include_router(location_router, prefix="/location", tags=["Location & Geocoding"])

__all__ = ["api_v1_router", "chat_router", "emergency_router", "location_router"]
