"""
Wraps the underlying local inference backend (llama.cpp via llama-cpp-python).
This module owns the actual model call. Nothing else should talk to llama.cpp.
"""

import time
from typing import Generator


class InferenceEngineError(Exception):
    """Raised when the inference engine encounters an error during generation."""
    pass


class GenerationResult:
    """
    Result from a single generation call.

    Attributes:
        text          (str)   -- The generated text (excluding the prompt)
        tokens_prompt (int)   -- Number of tokens in the input prompt
        tokens_gen    (int)   -- Number of tokens generated
        finish_reason (str)   -- stop | length | error
        elapsed       (float) -- Total generation time in seconds
        ttft          (float) -- Time to first token in seconds
    """
    def __init__(self, text: str, tokens_prompt: int = 0, tokens_gen: int = 0,
                 finish_reason: str = "stop", elapsed: float = 0.0, ttft: float = 0.0):
        self.text = text
        self.tokens_prompt = tokens_prompt
        self.tokens_gen = tokens_gen
        self.finish_reason = finish_reason
        self.elapsed = elapsed
        self.ttft = ttft

    @property
    def total_tokens(self) -> int:
        return self.tokens_prompt + self.tokens_gen


# Active model handle management
_active_handle = None


def set_handle(handle) -> None:
    global _active_handle
    _active_handle = handle


def get_handle():
    return _active_handle


def clear_handle() -> None:
    global _active_handle
    _active_handle = None


def is_model_loaded() -> bool:
    return _active_handle is not None and _active_handle._runtime_object is not None


def get_context_length() -> int | None:
    if not is_model_loaded():
        return None
    try:
        return _active_handle._runtime_object.n_ctx()
    except Exception:
        return _active_handle.context_length if _active_handle else None


DEFAULT_STOP_TOKENS = ["</s>", "<|eot_id|>", "</output>", "[/INST]"]


def generate(prompt: str, params: dict | None = None) -> GenerationResult:
    """
    Generate text from a given prompt string.

    Arguments:
        prompt  (str)        -- The fully formatted prompt string
        params  (dict|None)  -- Generation parameters
    Returns:
        GenerationResult
    Raises:
        InferenceEngineError -- If no model loaded or generation fails
    """
    if not is_model_loaded():
        raise InferenceEngineError("No model loaded. Load a model first.")

    params = params or {}
    llm = _active_handle._runtime_object
    stop_tokens = params.get("stop", DEFAULT_STOP_TOKENS)
    max_tokens = params.get("max_new_tokens", 512)

    gen_kwargs = {
        "max_tokens": max_tokens,
        "temperature": params.get("temperature", 0.7),
        "top_p": params.get("top_p", 0.9),
        "top_k": params.get("top_k", 40),
        "repeat_penalty": params.get("repeat_penalty", 1.1),
        "stop": stop_tokens,
    }
    seed = params.get("seed", -1)
    if seed >= 0:
        gen_kwargs["seed"] = seed

    start = time.time()
    ttft = 0.0
    try:
        result = llm(prompt, **gen_kwargs)
        ttft = time.time() - start
    except Exception as e:
        raise InferenceEngineError(f"Generation failed: {e}")

    elapsed = time.time() - start
    choice = result["choices"][0]
    text = choice["text"]
    finish = choice.get("finish_reason", "stop")
    usage = result.get("usage", {})
    tokens_prompt = usage.get("prompt_tokens", 0)
    tokens_gen = usage.get("completion_tokens", len(llm.tokenize(text.encode("utf-8"))))

    return GenerationResult(
        text=text,
        tokens_prompt=tokens_prompt,
        tokens_gen=tokens_gen,
        finish_reason=finish,
        elapsed=elapsed,
        ttft=ttft,
    )


def generate_stream(prompt: str, params: dict | None = None) -> Generator[str, None, None]:
    """
    Generate text token-by-token for SSE streaming.

    Yields:
        str -- Each generated token text
    Raises:
        InferenceEngineError -- If no model loaded or generation fails
    """
    if not is_model_loaded():
        raise InferenceEngineError("No model loaded. Load a model first.")

    params = params or {}
    llm = _active_handle._runtime_object
    stop_tokens = params.get("stop", DEFAULT_STOP_TOKENS)
    max_tokens = params.get("max_new_tokens", 512)

    gen_kwargs = {
        "max_tokens": max_tokens,
        "temperature": params.get("temperature", 0.7),
        "top_p": params.get("top_p", 0.9),
        "top_k": params.get("top_k", 40),
        "repeat_penalty": params.get("repeat_penalty", 1.1),
        "stop": stop_tokens,
        "stream": True,
    }
    seed = params.get("seed", -1)
    if seed >= 0:
        gen_kwargs["seed"] = seed

    try:
        for chunk in llm(prompt, **gen_kwargs):
            choice = chunk["choices"][0]
            delta = choice.get("delta", {})
            text = delta.get("content", "")
            if text:
                yield text
    except Exception as e:
        raise InferenceEngineError(f"Stream generation failed: {e}")


def load_model_from_path(model_path: str, context_length: int = 4096, n_gpu_layers: int = 0):
    """Load a model and set it as the active handle."""
    from model_runtime.model_loader import load_model, ModelLoadError
    try:
        handle = load_model(model_path, context_length=context_length, n_gpu_layers=n_gpu_layers)
        set_handle(handle)
        return handle
    except ModelLoadError:
        raise


def unload_active_model() -> None:
    """Unload the currently active model and free memory."""
    if _active_handle is not None:
        from model_runtime.model_loader import unload_model
        unload_model(_active_handle)
    clear_handle()


def generate_response_stub(prompt: str) -> GenerationResult:
    """Fallback stub when no model is loaded."""
    tokens_prompt = max(1, len(prompt) // 4)
    response = (
        "[STUB] Model not loaded. Configure a model via PUT /config and load it. "
        "Install llama-cpp-python: pip install llama-cpp-python"
    )
    tokens_gen = max(1, len(response) // 4)
    return GenerationResult(
        text=response,
        tokens_prompt=tokens_prompt,
        tokens_gen=tokens_gen,
        finish_reason="stub",
        elapsed=0.0,
        ttft=0.0,
    )