"""GET /status — Health check and model state."""

import sys
from pathlib import Path

# Ensure project root on sys.path
_project_root = str(Path(__file__).resolve().parent.parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from fastapi import APIRouter
from services.model_service import is_model_loaded, get_current_model_name

router = APIRouter()


@router.get("/")
async def get_status():
    return {
        "status": "ok",
        "model_loaded": is_model_loaded(),
        "current_model": get_current_model_name(),
        "version": "0.1.0",
    }
