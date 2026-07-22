"""Controller for model management request handling."""

from services.model_service import scan_model_directory, get_active_config


def list_available_models() -> dict:
    models = scan_model_directory()
    return {"models": models}


def get_active_model() -> dict:
    config = get_active_config()
    if config is None:
        return {"active_model": None}
    return config.to_dict()
