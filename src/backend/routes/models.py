"""GET /models — List available GGUF model files with auto-detected metadata."""

from fastapi import APIRouter
from backend.services.model_service import scan_model_directory

router = APIRouter()


@router.get("/")
async def list_models():
    models = scan_model_directory()
    return {"models": models}


@router.get("/detect")
async def detect_models():
    """Auto-detect metadata for all GGUF files in models/ directory."""
    from model_runtime.detector import detect_models_in_directory
    from backend.services.model_service import _get_models_dir
    models_dir = _get_models_dir()
    results = detect_models_in_directory(models_dir)
    return {"models": results}
