"""Real-time LLMOps Telemetry & Prometheus Metrics Collector for i-Soom.

Tracks stage-level latencies, Vertex AI token/cost consumption, RAG retrieval metrics,
conformal uncertainty escalations, safety-aware cache hit/bypass rates, and bandit feedback.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque
from typing import Any


# Approximate Vertex AI Gemini pricing per 1M tokens (USD) for cost observability
MODEL_COST_PER_1M: dict[str, tuple[float, float]] = {
    "gemini-2.5-flash": (0.15, 0.60),
    "gemini-2.5-flash-lite": (0.075, 0.30),
    "gemini-3.5-flash-lite": (0.075, 0.30),
    "gemini-3.8-flash": (0.15, 0.60),
    "text-embedding-005": (0.025, 0.0),
}


class LLMOpsTelemetry:
    """Thread-safe in-memory LLMOps metrics and trace aggregator."""

    def __init__(self, max_latencies: int = 500) -> None:
        self._lock = threading.Lock()
        self._started_at = time.time()
        self._stage_latencies: dict[str, deque[float]] = defaultdict(
            lambda: deque(maxlen=max_latencies)
        )
        self._counters: dict[str, int] = defaultdict(int)
        self._model_usage: dict[str, dict[str, float]] = defaultdict(
            lambda: {"calls": 0, "prompt_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "errors": 0}
        )
        self._recent_traces: deque[dict[str, Any]] = deque(maxlen=50)

    def inc(self, key: str, value: int = 1) -> None:
        with self._lock:
            self._counters[key] += value

    def observe_latency(self, stage: str, latency_ms: float) -> None:
        with self._lock:
            self._stage_latencies[stage].append(max(0.0, float(latency_ms)))

    def record_llm_call(
        self,
        model: str,
        prompt_tokens: int,
        output_tokens: int,
        latency_ms: float,
        success: bool = True,
    ) -> float:
        in_rate, out_rate = MODEL_COST_PER_1M.get(model, (0.15, 0.60))
        cost_usd = (prompt_tokens / 1_000_000.0) * in_rate + (output_tokens / 1_000_000.0) * out_rate
        with self._lock:
            bucket = self._model_usage[model]
            bucket["calls"] += 1
            bucket["prompt_tokens"] += max(0, int(prompt_tokens))
            bucket["output_tokens"] += max(0, int(output_tokens))
            bucket["cost_usd"] += cost_usd
            if not success:
                bucket["errors"] += 1
            self._stage_latencies["llm"].append(max(0.0, float(latency_ms)))
        return cost_usd

    def record_trace(self, trace: dict[str, Any]) -> None:
        with self._lock:
            self._recent_traces.append(trace)

    def get_summary(self) -> dict[str, Any]:
        with self._lock:
            stage_stats: dict[str, dict[str, float]] = {}
            for stage, vals in self._stage_latencies.items():
                if not vals:
                    continue
                sorted_v = sorted(vals)
                p95_idx = min(len(sorted_v) - 1, int(len(sorted_v) * 0.95))
                stage_stats[stage] = {
                    "count": len(sorted_v),
                    "avg_ms": round(sum(sorted_v) / len(sorted_v), 2),
                    "p95_ms": round(sorted_v[p95_idx], 2),
                }

            total_cost = round(sum(v["cost_usd"] for v in self._model_usage.values()), 6)
            return {
                "uptime_sec": round(time.time() - self._started_at, 1),
                "counters": dict(self._counters),
                "stage_latencies_ms": stage_stats,
                "model_usage": {
                    m: {**u, "cost_usd": round(u["cost_usd"], 6)}
                    for m, u in self._model_usage.items()
                },
                "total_estimated_cost_usd": total_cost,
                "recent_traces": list(self._recent_traces)[-10:],
            }

    def render_prometheus(self) -> str:
        """Renders counters and stage latencies in Prometheus exposition format."""
        summary = self.get_summary()
        lines: list[str] = [
            "# HELP isoom_uptime_seconds Application uptime in seconds.",
            "# TYPE isoom_uptime_seconds gauge",
            f"isoom_uptime_seconds {summary['uptime_sec']}",
            "# HELP isoom_llm_estimated_cost_usd_total Estimated cumulative Vertex AI cost in USD.",
            "# TYPE isoom_llm_estimated_cost_usd_total counter",
            f"isoom_llm_estimated_cost_usd_total {summary['total_estimated_cost_usd']}",
        ]
        for key, val in sorted(summary["counters"].items()):
            safe = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in key)
            lines.append(f"isoom_counter_{safe}_total {val}")
        for stage, stat in sorted(summary["stage_latencies_ms"].items()):
            safe = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in stage)
            lines.append(f'isoom_stage_latency_avg_ms{{stage="{safe}"}} {stat["avg_ms"]}')
            lines.append(f'isoom_stage_latency_p95_ms{{stage="{safe}"}} {stat["p95_ms"]}')
        return "\n".join(lines) + "\n"


telemetry = LLMOpsTelemetry()
