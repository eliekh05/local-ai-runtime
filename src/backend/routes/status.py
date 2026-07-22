"""GET /status — Health check and model state."""

from importlib.metadata import version as get_version
from fastapi import APIRouter
from backend.services.model_service import is_model_loaded, get_current_model_name

router = APIRouter()


@router.get("/")
async def get_status():
    return {
        "status": "ok",
        "model_loaded": is_model_loaded(),
        "current_model": get_current_model_name(),
        "version": get_version("local-ai-runtime"),
    }
