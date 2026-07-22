# huggingface/cache_manager.py
#
# Manages the local model cache — tracking what's been downloaded,
# where it lives, and cleaning up stale or unwanted files.
#
# STATUS: CONCEPT STUB — No cache operations implemented.
#
# Design notes:
#   The Hugging Face Hub client library (huggingface_hub) maintains its own
#   cache at ~/.cache/huggingface/ by default. This module intentionally
#   redirects all storage INTO the project's models/ directory instead,
#   to satisfy the requirement that everything lives inside the repo.
#
#   This means we bypass huggingface_hub's default caching and take
#   direct control of where files land.
#
# Cache location: ./models/  (relative to project root)
# Metadata file:  ./config/cache_manifest.json
#
# TODO (Phase 4.6):
#   - Implement get_cached_models()
#   - Implement is_cached()
#   - Implement cache_size_bytes()
#   - Implement evict_model() (delete a model file + registry entry)
#   - Implement validate_cache() (check files match manifest checksums)

import os
from pathlib import Path


MODELS_DIR = Path("models")
CACHE_MANIFEST_PATH = Path("config/cache_manifest.json")


def get_cached_models() -> list:
    """
    Return a list of all .gguf files currently in the models/ directory.

    Returns:
        list[dict] — Each item: { filename, size_bytes, path }

    NOTE: This scans the filesystem directly and does NOT require the
    registry or manifest. It is the ground truth of what's on disk.

    TODO (Phase 4.6): This is straightforward stdlib — safe to implement early.

        if not MODELS_DIR.exists():
            return []
        return [
            {
                "filename": f.name,
                "size_bytes": f.stat().st_size,
                "path": str(f.resolve()),
            }
            for f in MODELS_DIR.glob("*.gguf")
        ]
    """
    # TODO: Implement
    return []


def is_cached(filename: str) -> bool:
    """
    Check whether a model file exists in the local cache.

    Arguments:
        filename (str) — The .gguf filename to check

    Returns:
        bool — True if the file exists in models/

    TODO (Phase 4.6):
        return (MODELS_DIR / filename).exists()
    """
    # TODO: Implement
    return False


def cache_size_bytes() -> int:
    """
    Return the total disk space used by all cached model files.

    Returns:
        int — Total bytes used by .gguf files in models/

    TODO (Phase 4.6):
        total = 0
        for f in MODELS_DIR.glob("*.gguf"):
            total += f.stat().st_size
        return total
    """
    # TODO: Implement
    return 0


def cache_size_human() -> str:
    """
    Return total cache size as a human-readable string (e.g. "8.3 GB").

    TODO (Phase 4.6):
        Implement after cache_size_bytes() is working.
    """
    # TODO: Implement
    return "[unknown]"


def evict_model(filename: str, confirm: bool = False) -> bool:
    """
    Delete a model file from the local cache.

    Arguments:
        filename (str)  — The .gguf filename to remove
        confirm  (bool) — Safety flag: must be True to actually delete

    Returns:
        bool — True if file was deleted, False if not found

    WARNING: This permanently deletes the model file. Re-downloading
    large files takes time and bandwidth.

    TODO (Phase 4.6):
        if not confirm:
            raise ValueError("Set confirm=True to actually delete a model file.")
        path = MODELS_DIR / filename
        if not path.exists():
            return False
        path.unlink()
        # Also remove from registry
        # model_registry.deregister_model(filename)
        return True
    """
    raise NotImplementedError(
        "evict_model() not yet implemented. "
        "Deliberately requires confirm=True as a safety measure."
    )


def validate_cache() -> dict:
    """
    Check that all files in models/ match their expected checksums
    in the cache manifest.

    Returns:
        dict — { "valid": list[str], "missing": list[str], "corrupt": list[str] }

    TODO (Phase 4.6):
        Read config/cache_manifest.json, verify each entry against disk.
        This is important for detecting partial downloads.
    """
    raise NotImplementedError("validate_cache() not yet implemented. See TODO.md Phase 4.6.")
