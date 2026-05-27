"""Tests for server health watchdog."""
from __future__ import annotations

import pytest

from maggy.services.health_watchdog import (
    HealthCheck,
    HealthStatus,
    HealthWatchdog,
)


@pytest.fixture()
def watchdog() -> HealthWatchdog:
    return HealthWatchdog()


# ── Process health checks ─────────────────────────────────────────────


class TestProcessChecks:
    def test_check_running_process(
        self, watchdog: HealthWatchdog,
    ) -> None:
        # PID 1 (launchd/init) should always exist
        result = watchdog.check_pid(1)
        assert result.alive is True

    def test_check_dead_process(
        self, watchdog: HealthWatchdog,
    ) -> None:
        result = watchdog.check_pid(999999999)
        assert result.alive is False

    def test_register_and_check(
        self, watchdog: HealthWatchdog,
    ) -> None:
        watchdog.register("test-svc", pid=1)
        status = watchdog.status()
        assert "test-svc" in status
        assert status["test-svc"].alive is True


# ── Endpoint health checks ────────────────────────────────────────────


class TestEndpointChecks:
    def test_check_unreachable_endpoint(
        self, watchdog: HealthWatchdog,
    ) -> None:
        result = watchdog.check_endpoint(
            "http://localhost:19999/health",
            timeout=0.5,
        )
        assert result.alive is False

    def test_register_endpoint(
        self, watchdog: HealthWatchdog,
    ) -> None:
        watchdog.register(
            "dead-api",
            endpoint="http://localhost:19999/health",
        )
        status = watchdog.status()
        assert "dead-api" in status
        assert status["dead-api"].alive is False


# ── Memory checks ─────────────────────────────────────────────────────


class TestMemoryChecks:
    def test_system_memory_report(
        self, watchdog: HealthWatchdog,
    ) -> None:
        mem = watchdog.system_memory()
        assert "total_gb" in mem
        assert "used_gb" in mem
        assert "percent" in mem
        assert mem["total_gb"] > 0

    def test_high_memory_detection(
        self, watchdog: HealthWatchdog,
    ) -> None:
        # Just verify it returns a bool
        alert = watchdog.memory_pressure(threshold=0.99)
        assert isinstance(alert, bool)


# ── Aggregate status ──────────────────────────────────────────────────


class TestAggregateStatus:
    def test_empty_status(
        self, watchdog: HealthWatchdog,
    ) -> None:
        status = watchdog.status()
        assert isinstance(status, dict)
        assert len(status) == 0

    def test_overall_health(
        self, watchdog: HealthWatchdog,
    ) -> None:
        watchdog.register("alive", pid=1)
        watchdog.register(
            "dead",
            endpoint="http://localhost:19999/x",
        )
        overall = watchdog.overall()
        assert overall in (
            HealthStatus.HEALTHY,
            HealthStatus.DEGRADED,
            HealthStatus.UNHEALTHY,
        )
        # One dead service means at least degraded
        assert overall != HealthStatus.HEALTHY


# ── Data model ─────────────────────────────────────────────────────────


class TestDataModel:
    def test_health_check_fields(self) -> None:
        hc = HealthCheck(
            name="test",
            alive=True,
            detail="ok",
        )
        assert hc.name == "test"
        assert hc.alive is True
        assert hc.detail == "ok"

    def test_health_status_enum(self) -> None:
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"
