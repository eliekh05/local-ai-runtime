# huggingface/model_registry.py
#
# A local registry of known and downloaded models.
#
# STATUS: CONCEPT STUB — No registry operations are implemented.
#
# Purpose:
#   Track which models have been downloaded, where they live on disk,
#   what their metadata is, and which model profile config to use with them.
#
#   This is separate from scanning the models/ directory (which model_service does).
#   The registry stores richer metadata: HF repo origin, license, architecture
#   family, tested chat template, known context length, etc.
#
# Storage format (future):
#   A local JSON file at config/model_registry.json
#   Human-readable and editable by hand.
#
# TODO (Phase 4.6):
#   - Implement load_registry() / save_registry()
#   - Implement register_model() after successful download
#   - Implement lookup_model() by filename or repo_id
#   - Implement list_registered_models()
#   - Validate registry entries against actual files in models/

import json
from pathlib import Path
from datetime import datetime, timezone


REGISTRY_PATH = Path("config/model_registry.json")


class RegistryEntry:
    """
    A single entry in the model registry.

    Represents one GGUF file plus all known metadata about it.
    """

    def __init__(
        self,
        filename: str,
        repo_id: str | None = None,
        architecture: str | None = None,
        chat_template: str | None = None,
        context_length: int | None = None,
        quantization: str | None = None,
        parameter_count: str | None = None,
        license: str | None = None,
        notes: str = "",
        downloaded_at: str | None = None,
    ):
        self.filename = filename
        self.repo_id = repo_id
        self.architecture = architecture
        self.chat_template = chat_template
        self.context_length = context_length
        self.quantization = quantization
        self.parameter_count = parameter_count
        self.license = license
        self.notes = notes
        self.downloaded_at = downloaded_at or datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "filename": self.filename,
            "repo_id": self.repo_id,
            "architecture": self.architecture,
            "chat_template": self.chat_template,
            "context_length": self.context_length,
            "quantization": self.quantization,
            "parameter_count": self.parameter_count,
            "license": self.license,
            "notes": self.notes,
            "downloaded_at": self.downloaded_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RegistryEntry":
        return cls(**{k: data.get(k) for k in cls.__init__.__code__.co_varnames
                      if k != "self" and k in data})


class ModelRegistryError(Exception):
    """Raised when registry operations fail."""
    pass


def load_registry() -> list:
    """
    Load the local model registry from disk.

    Returns:
        list[RegistryEntry] — All registered models

    TODO (Phase 4.6):
        if not REGISTRY_PATH.exists():
            return []
        with open(REGISTRY_PATH) as f:
            data = json.load(f)
        return [RegistryEntry.from_dict(entry) for entry in data.get("models", [])]
    """
    # TODO: Implement
    return []


def save_registry(entries: list) -> None:
    """
    Save the model registry to disk.

    Arguments:
        entries (list[RegistryEntry]) — Full registry to write

    TODO (Phase 4.6):
        REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        data = {"models": [e.to_dict() for e in entries]}
        with open(REGISTRY_PATH, "w") as f:
            json.dump(data, f, indent=2)
    """
    raise NotImplementedError("save_registry() not yet implemented. See TODO.md Phase 4.6.")


def register_model(entry: RegistryEntry) -> None:
    """
    Add a new model to the registry (or update if filename already exists).

    Arguments:
        entry (RegistryEntry) — The model entry to register

    TODO (Phase 4.6):
        existing = load_registry()
        # Replace if already present
        updated = [e for e in existing if e.filename != entry.filename]
        updated.append(entry)
        save_registry(updated)
    """
    raise NotImplementedError("register_model() not yet implemented. See TODO.md Phase 4.6.")


def lookup_model(filename: str) -> "RegistryEntry | None":
    """
    Look up a model in the registry by filename.

    Arguments:
        filename (str) — The .gguf filename to look up

    Returns:
        RegistryEntry if found, None otherwise

    TODO (Phase 4.6):
        registry = load_registry()
        for entry in registry:
            if entry.filename == filename:
                return entry
        return None
    """
    # TODO: Implement
    return None


def list_registered_models() -> list:
    """
    Return all models currently in the registry.

    Returns:
        list[dict] — Registry entries as dicts (for API serialization)

    TODO (Phase 4.6):
        return [e.to_dict() for e in load_registry()]
    """
    return []
