"""GET /metrics — Performance monitoring endpoint."""

from fastapi import APIRouter
from backend.services.metrics_service import get_metrics

router = APIRouter()


@router.get("/")
async def metrics():
    return get_metrics()
