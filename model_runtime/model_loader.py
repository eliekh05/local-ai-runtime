"""
Responsible for loading GGUF model files into the inference engine.
Uses llama-cpp-python for actual model loading.
"""

import time
from pathlib import Path


class ModelLoadError(Exception):
    pass


class ModelHandle:
    def __init__(self, model_file: str, context_length: int):
        self.model_file = model_file
        self.context_length = context_length
        self._runtime_object = None

    def is_valid(self) -> bool:
        return self._runtime_object is not None

    def __repr__(self):
        return f"ModelHandle(model_file='{self.model_file}', loaded={self.is_valid()})"


def load_model(model_path, context_length=4096, n_gpu_layers=0):
    """Load a GGUF model via llama-cpp-python."""
    model_path = Path(model_path)
    if not model_path.exists():
        raise ModelLoadError(f"Model file not found: {model_path}")
    if model_path.suffix != ".gguf":
        raise ModelLoadError(f"Expected .gguf, got: {model_path.suffix}")

    try:
        from llama_cpp import Llama
    except ImportError:
        raise ModelLoadError(
            "llama-cpp-python not installed. Install: pip install llama-cpp-python"
        )

    file_size_gb = model_path.stat().st_size / (1024 ** 3)
    print(f"Loading model: {model_path.name} ({file_size_gb:.2f} GB) ...")

    start = time.time()
    try:
        llm = Llama(
            model_path=str(model_path),
            n_ctx=context_length,
            n_gpu_layers=n_gpu_layers,
            verbose=False,
        )
    except Exception as e:
        raise ModelLoadError(f"Failed to load model: {e}")

    elapsed = time.time() - start
    print(f"Model loaded in {elapsed:.2f}s")

    handle = ModelHandle(model_file=model_path.name, context_length=context_length)
    handle._runtime_object = llm
    return handle


def unload_model(handle: ModelHandle) -> None:
    """Unload a model and free its memory."""
    if handle is None:
        return
    handle._runtime_object = None
    print(f"Unloaded model: {handle.model_file}")
