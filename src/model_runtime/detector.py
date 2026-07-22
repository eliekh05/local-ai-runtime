"""
Model detection — auto-detect architecture, chat template, context length from GGUF metadata.
Replaces manual config with automatic detection.
"""

import struct
from pathlib import Path


# GGUF magic number
GGUF_MAGIC = 0x46554747  # "GGUF"

# Architecture to default chat template mapping
ARCH_TEMPLATE_MAP = {
    "llama": "llama3",
    "mistral": "mistral",
    "mixtral": "mistral",
    "phi": "chatml",
    "phi3": "chatml",
    "phi-3": "chatml",
    "qwen": "chatml",
    "qwen2": "chatml",
    "gemma": "chatml",
    "gemma2": "chatml",
    "command-r": "chatml",
    "deepseek": "chatml",
    "codellama": "llama3",
    "falcon": "chatml",
    "starcoder": "chatml",
    "yi": "chatml",
    "neox": "chatml",
    "mpt": "raw",
    "replit": "chatml",
    "phixtral": "mistral",
}


class ModelInfo:
    """Detected model metadata."""

    def __init__(self):
        self.filename = ""
        self.architecture = ""
        self.chat_template = "chatml"  # safe default
        self.context_length = 4096
        self.parameter_count = ""
        self.quantization = ""
        self.is_gguf = False
        self.detected = False

    def to_dict(self) -> dict:
        return {
            "filename": self.filename,
            "architecture": self.architecture,
            "chat_template": self.chat_template,
            "context_length": self.context_length,
            "parameter_count": self.parameter_count,
            "quantization": self.quantization,
            "is_gguf": self.is_gguf,
            "detected": self.detected,
        }


def _read_gguf_string(f) -> str:
    """Read a length-prefixed string from a GGUF file."""
    length = struct.unpack("<Q", f.read(8))[0]
    if length > 10000:
        return ""
    return f.read(length).decode("utf-8", errors="replace")


def _guess_quantization(filename: str) -> str:
    """Extract quantization level from filename."""
    name_lower = filename.lower()
    quants = [
        "Q2_K", "Q3_K_S", "Q3_K_M", "Q3_K_L",
        "Q4_0", "Q4_K_S", "Q4_K_M", "Q4_K_L",
        "Q5_0", "Q5_K_S", "Q5_K_M", "Q5_K_L",
        "Q6_K", "Q8_0", "F16", "F32",
        "IQ2_XXS", "IQ2_XS", "IQ2_S", "IQ2_M",
        "IQ3_XXS", "IQ3_XS", "IQ3_S", "IQ3_M",
        "IQ4_NL", "IQ4_XS",
    ]
    for q in quants:
        if q.lower() in name_lower:
            return q
    return ""


def _guess_parameters(filename: str) -> str:
    """Guess parameter count from filename."""
    name_lower = filename.lower()
    import re
    match = re.search(r"(\d+\.?\d*)[bB]", name_lower)
    if match:
        return f"{match.group(1)}B"
    return ""


def detect_model(model_path: str | Path) -> ModelInfo:
    """
    Auto-detect model metadata from a GGUF file.
    Reads the GGUF header to extract architecture, context length, etc.
    Falls back to filename heuristics.
    """
    model_path = Path(model_path)
    info = ModelInfo()
    info.filename = model_path.name
    info.quantization = _guess_quantization(model_path.name)
    info.parameter_count = _guess_parameters(model_path.name)

    if not model_path.exists():
        return info

    if model_path.suffix != ".gguf":
        return info

    info.is_gguf = True

    try:
        with open(model_path, "rb") as f:
            # Read magic number
            magic = struct.unpack("<I", f.read(4))[0]
            if magic != GGUF_MAGIC:
                return info

            # Read version
            version = struct.unpack("<I", f.read(4))[0]

            # Read tensor count and metadata KV count
            tensor_count = struct.unpack("<Q", f.read(8))[0]
            kv_count = struct.unpack("<Q", f.read(8))[0]

            # Read metadata key-value pairs
            for _ in range(kv_count):
                key = _read_gguf_string(f)
                value_type = struct.unpack("<I", f.read(4))[0]

                if value_type == 0:  # UINT8
                    f.read(1)
                elif value_type == 1:  # INT8
                    f.read(1)
                elif value_type == 2:  # UINT16
                    f.read(2)
                elif value_type == 3:  # INT16
                    f.read(2)
                elif value_type == 4:  # UINT32
                    val = struct.unpack("<I", f.read(4))[0]
                    if key == "general.context_length" and val > 0:
                        info.context_length = val
                elif value_type == 5:  # INT32
                    val = struct.unpack("<i", f.read(4))[0]
                    if key == "general.context_length" and val > 0:
                        info.context_length = val
                elif value_type == 6:  # FLOAT32
                    struct.unpack("<f", f.read(4))
                elif value_type == 7:  # BOOL
                    f.read(1)
                elif value_type == 8:  # STRING
                    val = _read_gguf_string(f)
                    if key == "general.architecture":
                        info.architecture = val
                    elif key == "general.name":
                        if not info.parameter_count:
                            info.parameter_count = val
                elif value_type == 9:  # ARRAY
                    arr_type = struct.unpack("<I", f.read(4))[0]
                    arr_len = struct.unpack("<Q", f.read(8))[0]
                    # Skip array elements
                    for _ in range(arr_len):
                        if arr_type == 8:
                            _read_gguf_string(f)
                        elif arr_type in (0, 1):
                            f.read(1)
                        elif arr_type in (2, 3):
                            f.read(2)
                        elif arr_type in (4, 5):
                            f.read(4)
                        elif arr_type == 6:
                            f.read(4)
                        elif arr_type == 7:
                            f.read(1)
                elif value_type == 10:  # UINT64
                    f.read(8)
                elif value_type == 11:  # INT64
                    f.read(8)
                elif value_type == 12:  # FLOAT64
                    f.read(8)
                else:
                    break

            info.detected = True

    except Exception:
        pass

    # Map architecture to chat template
    if info.architecture:
        arch_lower = info.architecture.lower()
        for arch_key, template in ARCH_TEMPLATE_MAP.items():
            if arch_key in arch_lower:
                info.chat_template = template
                break

    return info


def detect_models_in_directory(models_dir: str | Path) -> list[dict]:
    """Scan a directory and detect metadata for all GGUF files."""
    models_dir = Path(models_dir)
    if not models_dir.exists():
        return []

    results = []
    for gguf_file in sorted(models_dir.glob("*.gguf")):
        info = detect_model(gguf_file)
        results.append(info.to_dict())

    return results
