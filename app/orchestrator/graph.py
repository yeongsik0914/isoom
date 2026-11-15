"""Declarative StateGraph Orchestration Engine for i-Soom Multi-Agent Triage.

Implements a lightweight, deterministic LangGraph-compatible StateGraph pattern
(`add_node`, `add_edge`, `add_conditional_edges`, `compile`, `ainvoke`) with:
- Instant 0ms Red Flag Early-Exit edge
- Safety-Aware Semantic Cache bypass / hit Early-Exit edge
- Adaptive Triage -> Conformal Escalation / Matching / Logistics transitions
- Constitutional Post-Guard Output Verification node
- Per-node latency telemetry & full pipeline trace recording
"""

from __future__ import annotations

import inspect
import time
from typing import Any, Callable, Optional

from app.services.telemetry import telemetry

START = "__start__"
END = "__end__"

NodeCallable = Callable[[dict[str, Any]], Any]
ConditionCallable = Callable[[dict[str, Any]], str]


class CompiledStateGraph:
    """Executable state machine compiled from ClinicalStateGraph."""

    def __init__(
        self,
        nodes: dict[str, NodeCallable],
        edges: dict[str, str],
        conditional_edges: dict[str, tuple[ConditionCallable, dict[str, str]]],
        entry_point: Optional[str],
    ) -> None:
        self._nodes = nodes
        self._edges = edges
        self._conditional_edges = conditional_edges
        self._entry_point = entry_point

    async def ainvoke(
        self,
        initial_state: dict[str, Any],
        max_steps: int = 16,
    ) -> dict[str, Any]:
        state = dict(initial_state)
        trace: list[str] = list(state.get("trace", []))
        current = self._entry_point or self._edges.get(START)

        steps = 0
        while current and current != END:
            if steps >= max_steps:
                raise RuntimeError(f"StateGraph exceeded max_steps={max_steps} at node '{current}'")
            node_fn = self._nodes.get(current)
            if node_fn is None:
                raise KeyError(f"Unknown StateGraph node: '{current}'")

            t0 = time.perf_counter()
            res = node_fn(state)
            if inspect.isawaitable(res):
                res = await res
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            telemetry.observe_latency(f"node_{current}", elapsed_ms)

            if isinstance(res, dict):
                state.update(res)
            trace.append(current)
            state["trace"] = trace
            steps += 1

            if current in self._conditional_edges:
                cond_fn, route_map = self._conditional_edges[current]
                route_key = cond_fn(state)
                current = route_map.get(route_key, END)
            elif current in self._edges:
                current = self._edges[current]
            else:
                current = END

        return state


class ClinicalStateGraph:
    """Declarative multi-agent DAG/cyclic workflow builder."""

    def __init__(self) -> None:
        self._nodes: dict[str, NodeCallable] = {}
        self._edges: dict[str, str] = {}
        self._conditional_edges: dict[str, tuple[ConditionCallable, dict[str, str]]] = {}
        self._entry_point: Optional[str] = None

    def add_node(self, name: str, fn: NodeCallable) -> "ClinicalStateGraph":
        self._nodes[name] = fn
        return self

    def set_entry_point(self, name: str) -> "ClinicalStateGraph":
        self._entry_point = name
        return self

    def add_edge(self, src: str, dst: str) -> "ClinicalStateGraph":
        self._edges[src] = dst
        return self

    def add_conditional_edges(
        self,
        src: str,
        condition: ConditionCallable,
        mapping: dict[str, str],
    ) -> "ClinicalStateGraph":
        self._conditional_edges[src] = (condition, dict(mapping))
        return self

    def compile(self) -> CompiledStateGraph:
        return CompiledStateGraph(
            nodes=dict(self._nodes),
            edges=dict(self._edges),
            conditional_edges=dict(self._conditional_edges),
            entry_point=self._entry_point,
        )
