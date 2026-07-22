# huggingface/downloader.py
#
# Conceptual module for downloading model files from the Hugging Face Hub.
#
# STATUS: CONCEPT STUB — Nothing here downloads anything.
# No network calls are made. No authentication is required.
# No Hugging Face API is called.
#
# This module represents a FUTURE capability only.
# It exists to define the intended interface and document design decisions.
#
# Why this layer exists:
#   Manually downloading GGUF files from HuggingFace requires knowing
#   the exact URL structure, handling authentication for gated models,
#   verifying file integrity, and tracking where files land locally.
#   This module will eventually automate that workflow.
#
# Future dependencies (NOT YET INSTALLED):
#   - huggingface_hub   (pip install huggingface_hub)
#     The official HF Hub client library. Handles auth, caching, downloads.
#
# TODO (Phase 4.6):
#   - Implement download_model_file()
#   - Implement list_gguf_files_for_model()
#   - Handle authentication token for gated models
#   - Show progress bar during download
#   - Verify SHA256 checksum after download
#   - Register downloaded model in model_registry


class DownloadError(Exception):
    """Raised when a model download fails."""
    pass


def download_model_file(
    repo_id: str,
    filename: str,
    revision: str = "main",
    destination_dir: str = "./models/",
) -> str:
    """
    Download a specific file from a Hugging Face Hub repository.

    Arguments:
        repo_id         (str) — HF repo identifier, e.g. "TheBloke/Mistral-7B-Instruct-v0.2-GGUF"
        filename        (str) — Specific file to download, e.g. "mistral-7b-instruct-v0.2.Q4_K_M.gguf"
        revision        (str) — Git revision/branch (default: "main")
        destination_dir (str) — Local directory to save to (default: ./models/)

    Returns:
        str — Absolute path to the downloaded file

    Raises:
        DownloadError — If download fails for any reason

    Example (future usage):
        path = download_model_file(
            repo_id="TheBloke/Mistral-7B-Instruct-v0.2-GGUF",
            filename="mistral-7b-instruct-v0.2.Q4_K_M.gguf"
        )
        # Returns: "/path/to/project/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"

    TODO (Phase 4.6) — Intended implementation:

        from huggingface_hub import hf_hub_download
        import shutil

        local_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            revision=revision,
            local_dir=destination_dir,
        )
        return local_path
    """
    raise NotImplementedError(
        "download_model_file() is a placeholder. "
        "Hugging Face model downloading is not implemented yet. "
        "See TODO.md Phase 4.6."
    )


def list_gguf_files_for_model(repo_id: str) -> list:
    """
    List all GGUF files available in a given HuggingFace repository.

    Arguments:
        repo_id (str) — HF repo identifier

    Returns:
        list[dict] — Each item has: filename, size_bytes, quantization_guess

    TODO (Phase 4.6) — Intended implementation:

        from huggingface_hub import list_repo_files, get_paths_info

        gguf_files = [
            f for f in list_repo_files(repo_id)
            if f.endswith(".gguf")
        ]
        # Enrich with size info via get_paths_info
        return [{"filename": f, "size_bytes": None} for f in gguf_files]
    """
    raise NotImplementedError(
        "list_gguf_files_for_model() is not implemented. See TODO.md Phase 4.6."
    )


def verify_checksum(file_path: str, expected_sha256: str) -> bool:
    """
    Verify the SHA256 checksum of a downloaded file.

    Arguments:
        file_path       (str) — Path to the file to verify
        expected_sha256 (str) — Expected hex digest

    Returns:
        bool — True if checksum matches

    NOTE: This one is safe to implement now — it only uses stdlib.
    It just hasn't been needed yet since downloading isn't implemented.

    TODO (Phase 4.6):
        import hashlib

        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest() == expected_sha256.lower()
    """
    raise NotImplementedError("verify_checksum() not yet implemented.")
