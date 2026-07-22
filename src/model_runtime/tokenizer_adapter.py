"""
Normalizes the tokenizer interface across different model families.
Uses llama-cpp-python when a model is loaded.
Falls back to character-count estimation when no model is available.
"""


class TokenizerError(Exception):
    pass


def tokenize(text: str, model_handle) -> list:
    """Convert text to token IDs using the loaded model's tokenizer."""
    if model_handle is None or model_handle._runtime_object is None:
        raise TokenizerError("No model loaded for tokenization.")
    try:
        return model_handle._runtime_object.tokenize(
            text.encode("utf-8"), add_bos=True
        )
    except Exception as e:
        raise TokenizerError(f"Tokenization failed: {e}")


def detokenize(token_ids: list, model_handle) -> str:
    """Convert token IDs back to text."""
    if model_handle is None or model_handle._runtime_object is None:
        raise TokenizerError("No model loaded for detokenization.")
    try:
        raw = model_handle._runtime_object.detokenize(token_ids)
        return raw.decode("utf-8", errors="replace")
    except Exception as e:
        raise TokenizerError(f"Detokenization failed: {e}")


def count_tokens(text: str, model_handle) -> int:
    """Count tokens in text using the real tokenizer."""
    return len(tokenize(text, model_handle))


def get_special_tokens(model_handle) -> dict:
    """Return special token IDs (bos, eos) for the loaded model."""
    if model_handle is None or model_handle._runtime_object is None:
        raise TokenizerError("No model loaded.")
    try:
        meta = model_handle._runtime_object.metadata
        return {
            "bos_token_id": meta.get("general.bos_token_id", 1),
            "eos_token_id": meta.get("general.eos_token_id", 2),
        }
    except Exception:
        return {"bos_token_id": 1, "eos_token_id": 2}


def estimate_token_count(text: str) -> int:
    """Rough estimate without a loaded model. ~1 token per 4 chars."""
    if not text:
        return 0
    return max(1, len(text) // 4)
