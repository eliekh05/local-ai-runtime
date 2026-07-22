"""Data models for model configuration and inference I/O."""

from dataclasses import dataclass, field
from typing import Optional


CHAT_TEMPLATES = {
    "auto",
    "chatml",
    "llama3",
    "llama2",
    "mistral",
    "alpaca",
    "raw",
}

BACKEND_TYPES = {
    "llama-cpp",
    "ollama",
    "vllm",
    "openai",
    "anthropic",
    "gemini",
    "openai_compatible",
}


@dataclass
class GenerationParams:
    """Parameters controlling text generation."""
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.1
    max_new_tokens: int = 512
    min_new_tokens: int = 1
    seed: int = -1

    def to_dict(self) -> dict:
        return {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "repeat_penalty": self.repeat_penalty,
            "max_new_tokens": self.max_new_tokens,
            "min_new_tokens": self.min_new_tokens,
            "seed": self.seed,
        }


@dataclass
class ModelConfig:
    """Complete configuration for one model — all from config, no hardcoded defaults."""
    model_file: str = ""
    backend_type: str = "llama-cpp"
    chat_template: str = "auto"
    context_length: int = 4096
    system_prompt: str = "You are a helpful assistant."
    n_gpu_layers: int = 0
    generation: GenerationParams = field(default_factory=GenerationParams)
    profile_name: Optional[str] = None
    models_dir: str = "./models"
    # API backend overrides
    openai_model: str = ""
    anthropic_model: str = ""
    gemini_model: str = ""
    ollama_model: str = ""
    vllm_model: str = ""
    compatible_model: str = ""

    def to_dict(self) -> dict:
        return {
            "profile_name": self.profile_name,
            "backend_type": self.backend_type,
            "model_file": self.model_file,
            "chat_template": self.chat_template,
            "context_length": self.context_length,
            "system_prompt": self.system_prompt,
            "n_gpu_layers": self.n_gpu_layers,
            "models_dir": self.models_dir,
            "generation": self.generation.to_dict(),
            "openai_model": self.openai_model,
            "anthropic_model": self.anthropic_model,
            "gemini_model": self.gemini_model,
            "ollama_model": self.ollama_model,
            "vllm_model": self.vllm_model,
            "compatible_model": self.compatible_model,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ModelConfig":
        gen_data = data.get("generation", {})
        generation = GenerationParams(
            temperature=gen_data.get("temperature", 0.7),
            top_p=gen_data.get("top_p", 0.9),
            top_k=gen_data.get("top_k", 40),
            repeat_penalty=gen_data.get("repeat_penalty", 1.1),
            max_new_tokens=gen_data.get("max_new_tokens", 512),
            seed=gen_data.get("seed", -1),
        )
        return cls(
            model_file=data.get("model_file", ""),
            backend_type=data.get("backend_type", "llama-cpp"),
            chat_template=data.get("chat_template", "auto"),
            context_length=data.get("context_length", 4096),
            system_prompt=data.get("system_prompt", "You are a helpful assistant."),
            n_gpu_layers=data.get("n_gpu_layers", 0),
            generation=generation,
            profile_name=data.get("profile_name"),
            models_dir=data.get("models_dir", "./models"),
            openai_model=data.get("openai_model", ""),
            anthropic_model=data.get("anthropic_model", ""),
            gemini_model=data.get("gemini_model", ""),
            ollama_model=data.get("ollama_model", ""),
            vllm_model=data.get("vllm_model", ""),
            compatible_model=data.get("compatible_model", ""),
        )


@dataclass
class InferenceRequest:
    """Internal representation of an inference request."""
    prompt: str
    system_prompt: str = ""
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.1
    seed: int = -1
    stop_tokens: list[str] = field(default_factory=list)


@dataclass
class InferenceResponse:
    """Internal representation of an inference response."""
    text: str
    tokens_prompt: int = 0
    tokens_generated: int = 0
    finish_reason: str = "stop"
    model_name: str = ""

    @property
    def tokens_used(self) -> int:
        return self.tokens_prompt + self.tokens_generated
