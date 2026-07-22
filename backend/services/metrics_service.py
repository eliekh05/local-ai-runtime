"""Performance monitoring metrics."""

import time

_generation_metrics: list[dict] = []


def record_generation(tokens_prompt: int, tokens_gen: int, elapsed_seconds: float) -> None:
    _generation_metrics.append({
        "tokens_prompt": tokens_prompt,
        "tokens_gen": tokens_gen,
        "elapsed_seconds": elapsed_seconds,
        "tokens_per_second": tokens_gen / elapsed_seconds if elapsed_seconds > 0 else 0,
        "timestamp": time.time(),
    })


def get_metrics() -> dict:
    if not _generation_metrics:
        return {
            "total_generations": 0,
            "avg_tokens_per_second": 0,
            "avg_generation_time_seconds": 0,
            "total_tokens_generated": 0,
        }

    total_gen = sum(m["tokens_gen"] for m in _generation_metrics)
    avg_tps = sum(m["tokens_per_second"] for m in _generation_metrics) / len(_generation_metrics)
    avg_elapsed = sum(m["elapsed_seconds"] for m in _generation_metrics) / len(_generation_metrics)

    return {
        "total_generations": len(_generation_metrics),
        "avg_tokens_per_second": round(avg_tps, 2),
        "avg_generation_time_seconds": round(avg_elapsed, 3),
        "total_tokens_generated": total_gen,
    }
