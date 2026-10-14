"""Lightweight In-Memory Circuit Breaker for External Public APIs.

Implements the standard 3-State Finite State Machine (FSM):
1. CLOSED: Normal operation. Requests route to external API.
2. OPEN: Short-circuited. API calls are instantly blocked (0ms), routing to Fallback.
3. HALF_OPEN: Probe state. After recovery timeout, single canary request tests API health.

Thread-safe and async-compatible for both FastAPI routes and background daemon workers.
"""

from __future__ import annotations

import enum
import logging
import threading
import time
from typing import Any, Optional

logger = logging.getLogger(__name__)


class CircuitState(str, enum.Enum):
    """Circuit Breaker 3-State FSM."""

    CLOSED = "CLOSED"        # Normal: all calls passed through
    OPEN = "OPEN"            # Tripped: fast short-circuit to fallback (0ms)
    HALF_OPEN = "HALF_OPEN"  # Testing: canary probe call to detect recovery


class CircuitBreakerOpenException(Exception):
    """Raised when an operation is attempted while circuit is OPEN."""

    pass


class AsyncCircuitBreaker:
    """Zero-dependency In-Memory Circuit Breaker with automatic recovery probing."""

    def __init__(
        self,
        name: str = "NMC_EGEN_API",
        failure_threshold: int = 3,
        recovery_timeout: float = 60.0,
        request_timeout: float = 3.0,
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.request_timeout = request_timeout

        self.state: CircuitState = CircuitState.CLOSED
        self.failure_count: int = 0
        self.success_count: int = 0
        self.total_requests: int = 0
        self.short_circuit_count: int = 0
        self.last_state_change: float = time.time()
        self.last_failure_time: float = 0.0

        self._lock = threading.RLock()

    def is_available(self) -> bool:
        """Determines whether an outbound network call is permitted.

        Returns:
            True if state is CLOSED or transitioned to HALF_OPEN (probe allowed).
            False if state is OPEN and recovery timeout has not expired.
        """
        with self._lock:
            self.total_requests += 1
            now = time.time()

            if self.state == CircuitState.OPEN:
                elapsed = now - self.last_state_change
                if elapsed >= self.recovery_timeout:
                    logger.info(
                        f"[{self.name}] Recovery timeout expired ({elapsed:.1f}s >= {self.recovery_timeout}s). "
                        f"Transitioning OPEN -> HALF_OPEN (Canary probe allowed)."
                    )
                    self.state = CircuitState.HALF_OPEN
                    self.last_state_change = now
                    return True
                else:
                    self.short_circuit_count += 1
                    return False

            return True

    def record_success(self) -> None:
        """Records a successful network response, restoring CLOSED state."""
        with self._lock:
            self.success_count += 1
            if self.state != CircuitState.CLOSED:
                logger.info(
                    f"[{self.name}] Canary probe succeeded! Restoring circuit state {self.state} -> CLOSED."
                )
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.last_state_change = time.time()

    def record_failure(self, error: Optional[Any] = None) -> None:
        """Records a network timeout or HTTP 5xx error, tripping to OPEN if threshold reached."""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            now = time.time()

            logger.warning(
                f"[{self.name}] Failure #{self.failure_count}/{self.failure_threshold} recorded: {error}"
            )

            if self.state == CircuitState.HALF_OPEN:
                logger.error(
                    f"[{self.name}] Canary probe failed in HALF_OPEN! Tripping back to OPEN "
                    f"for another {self.recovery_timeout}s cooldown."
                )
                self.state = CircuitState.OPEN
                self.last_state_change = now
            elif self.failure_count >= self.failure_threshold:
                if self.state != CircuitState.OPEN:
                    logger.error(
                        f"[{self.name}] Failure threshold reached ({self.failure_count}>={self.failure_threshold})! "
                        f"Tripping circuit CLOSED -> OPEN. Engaging multi-tier fallback."
                    )
                self.state = CircuitState.OPEN
                self.last_state_change = now

    def reset(self) -> None:
        """Resets the circuit breaker to clean initial CLOSED state (for testing)."""
        with self._lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.total_requests = 0
            self.short_circuit_count = 0
            self.last_state_change = time.time()
            self.last_failure_time = 0.0

    def get_metrics(self) -> dict[str, Any]:
        """Returns diagnostic operational metrics for monitoring & API health endpoints."""
        with self._lock:
            now = time.time()
            return {
                "name": self.name,
                "state": self.state.value,
                "failure_count": self.failure_count,
                "failure_threshold": self.failure_threshold,
                "success_count": self.success_count,
                "total_requests": self.total_requests,
                "short_circuit_count": self.short_circuit_count,
                "recovery_timeout_seconds": self.recovery_timeout,
                "seconds_in_current_state": round(now - self.last_state_change, 1),
                "is_tripped": self.state == CircuitState.OPEN,
            }


# Default singleton circuit breaker for NMC E-Gen Public API
default_egen_circuit_breaker = AsyncCircuitBreaker(
    name="NMC_EGEN_API",
    failure_threshold=3,
    recovery_timeout=60.0,
    request_timeout=3.0,
)
